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
    "CWE-201": "privacy",
    "CWE-209": "information_exposure",
    "CWE-256": "secret",
    "CWE-295": "tls",
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
    "CWE-20": ("입력값 검증 추가", "입력값을 허용 목록과 명시적인 스키마로 검증한 뒤 사용하세요."),
    "CWE-22": ("안전한 경로로 제한", "기준 디렉터리에서 경로를 해석하고, 결과가 그 디렉터리 내부인지 확인하세요."),
    "CWE-77": ("명령과 인자 분리", "subprocess.run([command, arg], shell=False, check=True)를 사용하세요."),
    "CWE-78": ("셸 실행 제거", "subprocess.run([command, arg], shell=False, check=True)를 사용하세요."),
    "CWE-79": ("출력 이스케이프 적용", "신뢰할 수 있는 템플릿의 자동 이스케이프를 사용하고 mark_safe 사용을 제거하세요."),
    "CWE-89": ("매개변수화 쿼리 사용", "cursor.execute(\"SELECT ... WHERE id = %s\", (user_id,))"),
    "CWE-94": ("동적 코드 실행 제거", "eval/exec 대신 허용된 명령을 명시적으로 매핑해 실행하세요."),
    "CWE-201": ("응답 필드 최소화", "허용된 공개 필드만 새 응답 객체에 담아 반환하세요."),
    "CWE-209": ("일반화된 오류 응답", "내부 예외는 서버에 기록하고 클라이언트에는 일반 오류 메시지만 반환하세요."),
    "CWE-256": ("비밀번호 단방향 해시", "비밀번호는 Argon2id 또는 bcrypt로 해시한 값만 저장하세요."),
    "CWE-295": ("TLS 검증 활성화", "인증서 및 호스트명 검증을 활성화하고 신뢰할 CA를 설정하세요."),
    "CWE-327": ("안전한 암호 알고리즘 사용", "용도에 맞는 최신 암호 알고리즘과 라이브러리 기본값을 사용하세요."),
    "CWE-330": ("보안 난수 사용", "보안 토큰은 Python secrets 모듈로 생성하세요."),
    "CWE-352": ("CSRF 보호 활성화", "상태 변경 요청에 CSRF 검증을 적용하고 예외 설정을 제거하세요."),
    "CWE-359": ("개인정보 하드코딩 제거", "실제 개인정보를 코드에서 제거하고 테스트용 예약 도메인을 사용하세요."),
    "CWE-434": ("업로드 검증 추가", "파일명, 확장자, MIME 유형, 크기를 검증하고 안전한 저장명을 생성하세요."),
    "CWE-502": ("안전한 역직렬화", "신뢰할 수 없는 입력에는 JSON과 명시적 스키마 검증을 사용하세요."),
    "CWE-532": ("민감정보 로그 제거", "민감값을 로그에서 제거하거나 마스킹한 값만 기록하세요."),
    "CWE-770": ("자원 사용량 제한", "요청 크기, 반복 횟수, 메모리 할당량 및 타임아웃에 상한을 두세요."),
    "CWE-798": ("환경변수로 교체", "secret = os.environ[\"SECRET\"]"),
    "CWE-862": ("인가 검사 추가", "인증된 사용자의 권한과 대상 자원 소유권을 서버에서 확인하세요."),
    "CWE-918": ("요청 대상 제한", "URL을 파싱한 뒤 허용된 스킴과 호스트만 서버 측 요청에 사용하세요."),
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
                findings.append(
                    self._to_finding(rule, line, start_col, end_col)
                )

        findings.sort(key=lambda item: (item["line"], item["start_col"], item["rule_id"]))
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
                    severity=item["severity"].lower(),
                    cwes=tuple(item.get("cwe", ())),
                    pattern=re.compile(expanded),
                    allowlist=tuple(re.compile(value) for value in item.get("allowlist", ())),
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
        return {
            "rule_id": rule.rule_id,
            "cwe": ", ".join(rule.cwes),
            "category": CATEGORY_BY_CWE.get(primary_cwe, "security"),
            "severity": rule.severity,
            "line": line,
            "start_col": start_col,
            "end_col": end_col,
            "message": f"{rule.description}에 해당하는 패턴이 감지되었습니다.",
            "detail": f"{rule.name} 룰에 의해 탐지되었습니다.",
            "legal": {
                "law": "개인정보보호법",
                "article": "§29",
                "description": "개인정보 처리 시스템에 사용되는 경우 안전조치 의무 위반 소지가 있습니다.",
                "liability": None,
                "sanction": None,
            },
            "fix": {
                "title": fix_title,
                "replacement": replacement,
            },
        }


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
    start_col = start - line_starts[line]

    # The response contract has no end_line. For a multi-line match, highlight
    # from the start column to the end of the first matched line.
    next_newline = code.find("\n", start, end)
    visible_end = next_newline if next_newline != -1 else end
    if visible_end > start and code[visible_end - 1 : visible_end] == "\r":
        visible_end -= 1
    end_col = visible_end - line_starts[line]
    return line, start_col, max(start_col, end_col)
