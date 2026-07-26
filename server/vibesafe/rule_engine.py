"""TOML-backed regular-expression detection engine."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Pattern

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib


@dataclass(frozen=True)
class CompiledRule:
    rule_id: str
    name: str
    description: str
    severity: str
    cwes: tuple[str, ...]
    pattern: Pattern[str]
    allowlist: tuple[Pattern[str], ...]
    path_allowlist: tuple[Pattern[str], ...]


CATEGORY_BY_CWE = {
    "CWE-20": "input_validation",
    "CWE-22": "path_traversal",
    "CWE-77": "command_injection",
    "CWE-78": "command_injection",
    "CWE-79": "xss",
    "CWE-89": "sql_injection",
    "CWE-94": "code_injection",
    "CWE-200": "privacy",
    "CWE-201": "privacy",
    "CWE-209": "information_exposure",
    "CWE-256": "secret",
    "CWE-295": "tls",
    "CWE-307": "authentication",
    "CWE-327": "cryptography",
    "CWE-330": "cryptography",
    "CWE-352": "csrf",
    "CWE-359": "privacy",
    "CWE-434": "file_upload",
    "CWE-502": "insecure_deserialization",
    "CWE-532": "logging",
    "CWE-770": "resource_exhaustion",
    "CWE-798": "secret",
    "CWE-862": "access_control",
    "CWE-918": "ssrf",
}


FIX_BY_CWE = {
    "CWE-20": (
        "입력값 검증 추가",
        "입력값을 허용 목록과 명시적인 스키마로 검증한 뒤 사용하세요.",
    ),
    "CWE-22": (
        "안전한 경로로 제한",
        "기준 디렉터리에서 경로를 해석하고, 결과가 그 디렉터리 내부인지 확인하세요.",
    ),
    "CWE-77": (
        "명령과 인자 분리",
        "subprocess.run([command, arg], shell=False, check=True)를 사용하세요.",
    ),
    "CWE-78": (
        "셸 실행 제거",
        "subprocess.run([command, arg], shell=False, check=True)를 사용하세요.",
    ),
    "CWE-79": (
        "출력 이스케이프 적용",
        "신뢰할 수 있는 템플릿의 자동 이스케이프를 사용하고 mark_safe 사용을 제거하세요.",
    ),
    "CWE-89": (
        "매개변수화 쿼리 사용",
        'cursor.execute("SELECT ... WHERE id = %s", (user_id,))',
    ),
    "CWE-94": (
        "동적 코드 실행 제거",
        "eval/exec 대신 허용된 명령을 명시적으로 매핑해 실행하세요.",
    ),
    "CWE-200": (
        "민감정보 노출 제거",
        "응답과 소스 코드에서 불필요한 개인정보 및 민감정보를 제거하세요.",
    ),
    "CWE-201": (
        "응답 필드 최소화",
        "허용된 공개 필드만 새 응답 객체에 담아 반환하세요.",
    ),
    "CWE-209": (
        "일반화된 오류 응답",
        "내부 예외는 서버에 기록하고 클라이언트에는 일반 오류 메시지만 반환하세요.",
    ),
    "CWE-256": (
        "비밀번호 단방향 해시",
        "비밀번호는 Argon2id 또는 bcrypt로 해시한 값만 저장하세요.",
    ),
    "CWE-295": (
        "TLS 검증 활성화",
        "인증서 및 호스트명 검증을 활성화하고 신뢰할 CA를 설정하세요.",
    ),
    "CWE-307": (
        "인증 시도 제한 추가",
        "계정과 IP별 로그인 시도 횟수를 제한하고 지연 또는 잠금 정책을 적용하세요.",
    ),
    "CWE-327": (
        "안전한 암호 알고리즘 사용",
        "용도에 맞는 최신 암호 알고리즘과 라이브러리 기본값을 사용하세요.",
    ),
    "CWE-330": ("보안 난수 사용", "보안 토큰은 Python secrets 모듈로 생성하세요."),
    "CWE-352": (
        "CSRF 보호 활성화",
        "상태 변경 요청에 CSRF 검증을 적용하고 예외 설정을 제거하세요.",
    ),
    "CWE-359": (
        "개인정보 하드코딩 제거",
        "실제 개인정보를 코드에서 제거하고 테스트용 예약 도메인을 사용하세요.",
    ),
    "CWE-434": (
        "업로드 검증 추가",
        "파일명, 확장자, MIME 유형, 크기를 검증하고 안전한 저장명을 생성하세요.",
    ),
    "CWE-502": (
        "안전한 역직렬화",
        "신뢰할 수 없는 입력에는 JSON과 명시적 스키마 검증을 사용하세요.",
    ),
    "CWE-532": (
        "민감정보 로그 제거",
        "민감값을 로그에서 제거하거나 마스킹한 값만 기록하세요.",
    ),
    "CWE-770": (
        "자원 사용량 제한",
        "요청 크기, 반복 횟수, 메모리 할당량 및 타임아웃에 상한을 두세요.",
    ),
    "CWE-798": ("환경변수로 교체", 'secret = os.environ["SECRET"]'),
    "CWE-862": (
        "인가 검사 추가",
        "인증된 사용자의 권한과 대상 자원 소유권을 서버에서 확인하세요.",
    ),
    "CWE-918": (
        "요청 대상 제한",
        "URL을 파싱한 뒤 허용된 스킴과 호스트만 서버 측 요청에 사용하세요.",
    ),
}

# 감지된 위험의 두 번째 줄에 노출할 짧은 대응 안내.
# 내부 룰 이름 대신 사용자가 바로 적용할 수 있는 권고 문구를 보여준다.
DETAIL_BY_CWE = {
    "CWE-20": "허용 목록 기반 입력값 검증 권장",
    "CWE-22": "기준 디렉터리 내부의 안전한 경로만 사용 권장",
    "CWE-77": "shell=False와 명령 인자 배열 사용 권장",
    "CWE-78": "shell=False와 명령 인자 배열 사용 권장",
    "CWE-79": "템플릿 자동 이스케이프 사용 권장",
    "CWE-89": "매개변수화 쿼리 또는 ORM 사용 권장",
    "CWE-94": "eval/exec 대신 허용 목록 기반 명령 매핑 사용 권장",
    "CWE-200": "불필요한 개인정보·민감정보 제거 권장",
    "CWE-201": "허용된 공개 필드만 응답에 포함 권장",
    "CWE-209": "클라이언트에는 일반 오류 메시지만 반환 권장",
    "CWE-256": "Argon2id 또는 bcrypt 해시 저장 권장",
    "CWE-295": "인증서·호스트명 검증 활성화 권장",
    "CWE-307": "계정·IP별 로그인 시도 제한 권장",
    "CWE-327": "최신 암호 알고리즘과 검증된 라이브러리 사용 권장",
    "CWE-330": "보안 토큰 생성 시 Python secrets 모듈 사용 권장",
    "CWE-352": "상태 변경 요청에 CSRF 보호 기능 사용 권장",
    "CWE-359": "실제 개인정보 제거 및 테스트용 예약 도메인 사용 권장",
    "CWE-434": "파일명·확장자·MIME 유형·크기 검증 권장",
    "CWE-502": "JSON과 명시적 스키마 검증 사용 권장",
    "CWE-532": "민감정보 제거 또는 마스킹 후 로깅 권장",
    "CWE-770": "요청 크기·반복 횟수·메모리·타임아웃 제한 권장",
    "CWE-798": "환경변수(.env) 또는 Secrets Manager 사용 권장",
    "CWE-862": "사용자 권한 및 대상 자원 소유권 검사 권장",
    "CWE-918": "허용된 스킴·호스트만 서버 요청에 사용 권장",
}


# docs/legal-mapping.md의 "1안: CWE별 경고 문구"를 API용 한 줄
# 문자열로 옮긴 매핑이다. 규칙 이름이나 설명과 무관하게 동일 CWE는 동일한
# 사용자 경고를 반환한다.
WARNING_BY_CWE = {
    "CWE-20": (
        "입력값 검증이 미흡합니다. 악의적인 입력으로 인해 보안 취약점이 "
        "발생할 수 있습니다. 개인정보보호법 제29조 관련 보호조치가 필요합니다."
    ),
    "CWE-22": (
        "Path Traversal이 탐지되었습니다. 중요 파일이 노출될 수 있습니다. "
        "정보통신망법 제49조 관련 보안조치가 필요합니다."
    ),
    "CWE-77": (
        "OS Command Injection이 탐지되었습니다. 시스템 명령 실행 위험이 "
        "있습니다. 정보통신망법 제48조 관련 보안조치가 필요합니다."
    ),
    "CWE-78": (
        "OS Command Injection이 탐지되었습니다. 시스템 명령 실행 위험이 "
        "있습니다. 정보통신망법 제48조 관련 보안조치가 필요합니다."
    ),
    "CWE-79": (
        "XSS가 탐지되었습니다. 세션 탈취 및 개인정보 유출 위험이 있습니다. "
        "개인정보보호법 제29조 관련 보안조치가 필요합니다."
    ),
    "CWE-89": (
        "SQL Injection이 탐지되었습니다. 개인정보 유출 및 DB 변조 위험이 "
        "있습니다. 개인정보보호법 제29조 관련 보안조치가 필요합니다."
    ),
    "CWE-94": (
        "Code Injection이 탐지되었습니다. 악성 코드 실행 위험이 있습니다. "
        "정보통신망법 제48조 관련 보안조치가 필요합니다."
    ),
    "CWE-200": (
        "민감한 개인정보가 노출되었습니다. 개인정보 유출 및 프라이버시 침해 "
        "위험이 있습니다. 개인정보보호법 제29조 관련 보호조치가 필요합니다."
    ),
    "CWE-201": (
        "응답 데이터에 민감한 정보가 포함되었습니다. 개인정보 유출 위험이 "
        "있습니다. 개인정보보호법 제24조의2 및 제29조 관련 보호조치가 필요합니다."
    ),
    "CWE-209": (
        "오류 메시지에 민감한 정보가 포함되었습니다. 시스템 내부 정보 및 "
        "개인정보가 노출될 위험이 있습니다. 개인정보보호법 제29조 관련 보호조치가 "
        "필요합니다."
    ),
    "CWE-256": (
        "비밀번호가 평문으로 저장되고 있습니다. 계정 정보 유출 위험이 "
        "있습니다. 개인정보보호법 제24조의2 관련 보안조치가 필요합니다."
    ),
    "CWE-295": (
        "인증서 검증이 올바르게 수행되지 않았습니다. 중간자 공격으로 개인정보 "
        "및 인증 정보가 탈취될 위험이 있습니다. 개인정보보호법 제29조 관련 "
        "보호조치가 필요합니다."
    ),
    "CWE-307": (
        "로그인 시도 제한이 없습니다. 무차별 대입 공격 위험이 있습니다. "
        "개인정보보호법 제29조 관련 보안조치가 필요합니다."
    ),
    "CWE-327": (
        "취약한 암호화가 사용되었습니다. 민감정보 유출 위험이 있습니다. "
        "개인정보보호법 제29조 관련 보안조치가 필요합니다."
    ),
    "CWE-330": (
        "안전하지 않은 난수 생성이 탐지되었습니다. 인증 우회 위험이 있습니다. "
        "전자금융거래법 제21조 관련 보안조치가 필요합니다."
    ),
    "CWE-352": (
        "CSRF가 탐지되었습니다. 비정상 요청이 수행될 수 있습니다. "
        "전자금융거래법 제21조 관련 보안조치가 필요합니다."
    ),
    "CWE-359": (
        "민감한 개인정보가 노출되었습니다. 개인정보 유출 및 프라이버시 침해 "
        "위험이 있습니다. 개인정보보호법 제29조 관련 보호조치가 필요합니다."
    ),
    "CWE-434": (
        "위험한 파일 업로드가 탐지되었습니다. 서버 침해 위험이 있습니다. "
        "정보통신망법 제48조 관련 보안조치가 필요합니다."
    ),
    "CWE-502": (
        "안전하지 않은 역직렬화가 탐지되었습니다. 원격 코드 실행 위험이 "
        "있습니다. 정보통신망법 제48조 관련 보안조치가 필요합니다."
    ),
    "CWE-532": (
        "로그 파일에 민감한 정보가 저장되었습니다. 개인정보 및 인증 정보 유출 "
        "위험이 있습니다. 개인정보보호법 제29조 관련 보호조치가 필요합니다."
    ),
    "CWE-770": (
        "자원 사용 제한이 없습니다. 서비스 장애가 발생할 수 있습니다. "
        "정보통신망법 제48조 관련 보안조치가 필요합니다."
    ),
    "CWE-798": (
        "하드코딩된 인증 정보가 탐지되었습니다. 계정 정보 유출 위험이 있습니다. "
        "개인정보보호법 제29조 관련 보안조치가 필요합니다."
    ),
    "CWE-862": (
        "접근 권한 검증이 미흡합니다. 비인가 접근 위험이 있습니다. "
        "개인정보보호법 제29조 관련 보안조치가 필요합니다."
    ),
    "CWE-918": (
        "SSRF가 탐지되었습니다. 내부 시스템 접근 위험이 있습니다. "
        "개인정보보호법 제29조 관련 보안조치가 필요합니다."
    ),
}


# liability + sanction 값은 docs/legal-mapping.md의 법적 가중치와 일치하도록
# 하드코딩했다. 문서에 가중치가 없는 CWE-307은 개인정보보호법 제29조의 기존
# 계약 예시(2 + 1)를 적용한다.
LEGAL_BY_CWE = {
    "CWE-20": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "입력값 검증 미흡으로 안전조치 의무 위반 소지가 있습니다.",
        "liability": 2,
        "sanction": 2,
    },
    "CWE-22": {
        "law": "정보통신망법",
        "article": "§49",
        "description": "중요 파일 노출로 관련 보안조치 의무 위반 소지가 있습니다.",
        "liability": 3,
        "sanction": 1,
    },
    "CWE-77": {
        "law": "정보통신망법",
        "article": "§48",
        "description": "시스템 명령 실행으로 관련 보안조치 의무 위반 소지가 있습니다.",
        "liability": 3,
        "sanction": 2,
    },
    "CWE-78": {
        "law": "정보통신망법",
        "article": "§48",
        "description": "시스템 명령 실행으로 관련 보안조치 의무 위반 소지가 있습니다.",
        "liability": 3,
        "sanction": 2,
    },
    "CWE-79": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "세션 탈취 및 개인정보 유출로 안전조치 의무 위반 소지가 있습니다.",
        "liability": 2,
        "sanction": 2,
    },
    "CWE-89": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "개인정보 유출 및 DB 변조로 안전조치 의무 위반 소지가 있습니다.",
        "liability": 3,
        "sanction": 2,
    },
    "CWE-94": {
        "law": "정보통신망법",
        "article": "§48",
        "description": "악성 코드 실행으로 관련 보안조치 의무 위반 소지가 있습니다.",
        "liability": 3,
        "sanction": 2,
    },
    "CWE-200": {
        "law": "개인정보보호법, 신용정보법",
        "article": "§29",
        "description": "민감한 개인정보 노출로 보호조치 의무 위반 소지가 있습니다.",
        "liability": 3,
        "sanction": 2,
    },
    "CWE-201": {
        "law": "개인정보보호법",
        "article": "§24의2, §29",
        "description": "응답 데이터의 민감정보 노출로 보호조치 의무 위반 소지가 있습니다.",
        "liability": 2,
        "sanction": 1,
    },
    "CWE-209": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "오류 메시지의 민감정보 노출로 보호조치 의무 위반 소지가 있습니다.",
        "liability": 1,
        "sanction": 0.5,
    },
    "CWE-256": {
        "law": "개인정보보호법",
        "article": "§24의2",
        "description": "비밀번호 평문 저장으로 보호조치 의무 위반 소지가 있습니다.",
        "liability": 2,
        "sanction": 2,
    },
    "CWE-295": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "인증서 검증 미흡으로 안전조치 의무 위반 소지가 있습니다.",
        "liability": 2,
        "sanction": 2,
    },
    "CWE-307": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "인증 시도 제한 미흡으로 안전조치 의무 위반 소지가 있습니다.",
        "liability": 2,
        "sanction": 1,
    },
    "CWE-327": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "취약한 암호화 사용으로 안전조치 의무 위반 소지가 있습니다.",
        "liability": 2,
        "sanction": 2,
    },
    "CWE-330": {
        "law": "전자금융거래법",
        "article": "§21",
        "description": "안전하지 않은 난수 생성으로 보안조치 의무 위반 소지가 있습니다.",
        "liability": 1,
        "sanction": 0.5,
    },
    "CWE-352": {
        "law": "전자금융거래법",
        "article": "§21",
        "description": "비정상 요청 방지 미흡으로 보안조치 의무 위반 소지가 있습니다.",
        "liability": 2,
        "sanction": 2,
    },
    "CWE-359": {
        "law": "개인정보보호법, 신용정보법",
        "article": "§29",
        "description": "민감한 개인정보 노출로 보호조치 의무 위반 소지가 있습니다.",
        "liability": 3,
        "sanction": 2,
    },
    "CWE-434": {
        "law": "정보통신망법",
        "article": "§48",
        "description": "위험한 파일 업로드로 관련 보안조치 의무 위반 소지가 있습니다.",
        "liability": 3,
        "sanction": 2,
    },
    "CWE-502": {
        "law": "정보통신망법",
        "article": "§48",
        "description": "안전하지 않은 역직렬화로 관련 보안조치 의무 위반 소지가 있습니다.",
        "liability": 3,
        "sanction": 2,
    },
    "CWE-532": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "로그 파일의 민감정보 저장으로 보호조치 의무 위반 소지가 있습니다.",
        "liability": 2,
        "sanction": 2,
    },
    "CWE-770": {
        "law": "정보통신망법",
        "article": "§48",
        "description": "자원 사용 제한 미흡으로 관련 보안조치 의무 위반 소지가 있습니다.",
        "liability": 1,
        "sanction": 0.5,
    },
    "CWE-798": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "하드코딩된 인증정보로 안전조치 의무 위반 소지가 있습니다.",
        "liability": 3,
        "sanction": 2,
    },
    "CWE-862": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "접근 권한 검증 미흡으로 안전조치 의무 위반 소지가 있습니다.",
        "liability": 2,
        "sanction": 2,
    },
    "CWE-918": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "내부 시스템 접근 위험으로 안전조치 의무 위반 소지가 있습니다.",
        "liability": 3,
        "sanction": 2,
    },
}

# docs/legal-mapping.md의 "제재 수준" 열을 사용자 표시용 문자열로 보존한다.
SANCTION_TYPE_BY_CWE = {
    "CWE-20": "과징금·과태료",
    "CWE-22": "형사처벌",
    "CWE-77": "형사처벌",
    "CWE-78": "형사처벌",
    "CWE-79": "과징금·과태료",
    "CWE-89": "형사처벌, 과징금·과태료",
    "CWE-94": "형사처벌",
    "CWE-200": "형사처벌, 과징금·과태료",
    "CWE-201": "과징금·과태료",
    "CWE-209": "시정명령·권고",
    "CWE-256": "과징금·과태료",
    "CWE-295": "과징금·과태료",
    # 문서 표에 없는 CWE-307은 기존 sanction 1 계약값을 따른다.
    "CWE-307": "과징금·과태료",
    "CWE-327": "과징금·과태료",
    "CWE-330": "시정명령·권고",
    "CWE-352": "과징금·과태료",
    "CWE-359": "형사처벌, 과징금·과태료",
    "CWE-434": "형사처벌",
    "CWE-502": "형사처벌",
    "CWE-532": "과징금·과태료",
    "CWE-770": "시정명령·권고",
    "CWE-798": "형사처벌, 과징금·과태료",
    "CWE-862": "과징금·과태료",
    "CWE-918": "형사처벌",
}


class RuleEngine:
    def __init__(self, ruleset_path: str | Path) -> None:
        self.ruleset_path = Path(ruleset_path)
        self.target_languages, self.rules = self._load_rules(self.ruleset_path)

    @property
    def rule_count(self) -> int:
        return len(self.rules)

    def detect(self, code: str, language: str, file_name: str) -> list[dict[str, Any]]:
        if language.strip().lower() not in self.target_languages:
            return []

        line_starts = _line_starts(code)
        findings: list[dict[str, Any]] = []
        seen: set[tuple[str, int, int]] = set()

        for rule in self.rules:
            if any(pattern.search(file_name) for pattern in rule.path_allowlist):
                continue

            for match in rule.pattern.finditer(code):
                matched_text = match.group(0)
                if any(pattern.search(matched_text) for pattern in rule.allowlist):
                    continue

                key = (rule.rule_id, match.start(), match.end())
                if key in seen:
                    continue
                seen.add(key)

                line, start_col, end_col = _coordinates(
                    code, line_starts, match.start(), match.end()
                )
                findings.append(self._to_finding(rule, line, start_col, end_col))

        findings.sort(
            key=lambda item: (item["line"], item["start_col"], item["rule_id"])
        )
        return findings

    @staticmethod
    def _load_rules(path: Path) -> tuple[set[str], tuple[CompiledRule, ...]]:
        with path.open("rb") as ruleset_file:
            raw = tomllib.load(ruleset_file)

        keyword_sets = raw.get("keyword_sets", {})
        targets = {
            str(value).strip().lower()
            for value in raw.get("rule_config", {}).get("target_lang", [])
        }
        compiled_rules: list[CompiledRule] = []

        for item in raw.get("rules", []):
            expanded = _expand_keyword_sets(item["regex"], keyword_sets)
            compiled_rules.append(
                CompiledRule(
                    rule_id=item["id"],
                    name=item["name"],
                    description=item["desc"],
                    severity=_normalize_severity(item["severity"]),
                    cwes=tuple(item.get("cwe", ())),
                    pattern=re.compile(expanded),
                    allowlist=tuple(
                        re.compile(value) for value in item.get("allowlist", ())
                    ),
                    path_allowlist=tuple(
                        re.compile(value) for value in item.get("path_allowlist", ())
                    ),
                )
            )
        return targets, tuple(compiled_rules)

    @staticmethod
    def _to_finding(
        rule: CompiledRule, line: int, start_col: int, end_col: int
    ) -> dict[str, Any]:
        primary_cwe = rule.cwes[0] if rule.cwes else ""
        fix_title, replacement = FIX_BY_CWE.get(
            primary_cwe,
            ("안전한 구현으로 교체", "탐지된 패턴을 제거하고 안전한 API를 사용하세요."),
        )
        legal = LEGAL_BY_CWE.get(primary_cwe)
        legal_response = dict(legal) if legal else None
        if legal_response:
            legal_response["sanction_type"] = SANCTION_TYPE_BY_CWE[primary_cwe]
        return {
            "rule_id": rule.rule_id,
            "cwe": ", ".join(rule.cwes),
            "category": CATEGORY_BY_CWE.get(primary_cwe, "security"),
            "severity": rule.severity,
            "line": line,
            "start_col": start_col,
            "end_col": end_col,
            "message": WARNING_BY_CWE.get(
                primary_cwe,
                f"{rule.description}에 해당하는 패턴이 감지되었습니다.",
            ),
            "detail": DETAIL_BY_CWE.get(
                primary_cwe,
                "안전한 구현 방식 사용 권장",
            ),
            "legal": legal_response,
            "fix": {
                "title": fix_title,
                "replacement": replacement,
            },
        }


def _normalize_severity(value: str) -> str:
    """Normalize ruleset severities to the high/medium/low API contract."""
    normalized = value.strip().lower()
    if normalized == "critical":
        return "high"
    if normalized not in {"high", "medium", "low"}:
        raise ValueError(f"지원하지 않는 severity 값입니다: {value}")
    return normalized


def _expand_keyword_sets(pattern: str, keyword_sets: dict[str, list[str]]) -> str:
    expanded = pattern
    for name, values in keyword_sets.items():
        alternatives = "|".join(values)
        expanded = expanded.replace("{" + name + "}", f"(?:{alternatives})")

    unresolved = re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", expanded)
    if unresolved:
        names = ", ".join(sorted(set(unresolved)))
        raise ValueError(f"ruleset에 정의되지 않은 keyword set이 있습니다: {names}")
    return expanded


def _line_starts(code: str) -> list[int]:
    starts = [0]
    starts.extend(match.end() for match in re.finditer("\n", code))
    return starts


def _coordinates(
    code: str, line_starts: list[int], start: int, end: int
) -> tuple[int, int, int]:
    line = bisect_right(line_starts, start) - 1
    line_start = line_starts[line]
    start_col = _utf16_length(code[line_start:start])

    # The response contract has no end_line. For a multi-line match, highlight
    # from the start column to the end of the first matched line.
    next_newline = code.find("\n", start, end)
    visible_end = next_newline if next_newline != -1 else end
    if visible_end > start and code[visible_end - 1 : visible_end] == "\r":
        visible_end -= 1
    end_col = _utf16_length(code[line_start:visible_end])
    return line, start_col, max(start_col, end_col)


def _utf16_length(value: str) -> int:
    """Return the number of UTF-16 code units used by VS Code positions."""
    return len(value.encode("utf-16-le")) // 2
