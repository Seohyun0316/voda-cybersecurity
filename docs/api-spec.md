# VibeSafe MVP API 계약 v1

이 문서는 VS Code Extension과 Flask Server 사이의 기준 계약이다.
구현이나 다른 문서와 내용이 다르면 이 문서를 우선한다.

## 1. MVP 범위

- Python 파일 한 개를 수동으로 분석한다.
- Extension Host가 `localhost`의 Flask Server를 호출한다.
- 인증, HTTPS, CORS, 요청 크기 제한, 다중 파일 분석은 MVP 범위에서 제외한다.
- 서버는 룰 엔진으로 후보를 찾고 ML 모델을 2차 필터로 사용한다.
- 서버 JSON은 `snake_case`, Extension 내부 모델은 `camelCase`를 사용한다.
- 모든 위치 좌표는 0-based이고, 끝 열(`end_col`)은 exclusive이다.

기본 주소:

```text
http://localhost:5000
```

## 2. ML 처리 의미

`POST /detect`의 탐지 순서는 다음과 같다.

1. 룰 엔진이 finding 후보를 만든다.
2. 학습된 rule에 대해 ML 취약 확률을 계산한다.
3. 확률이 `0.5` 이상인 후보만 유지한다.
4. ML이 알지 못하는 rule은 모델·룰셋 버전 차이로 탐지가 사라지지 않도록 유지한다.

ML 확률은 내부 필터링 값이며 MVP 응답에는 노출하지 않는다.
`risk_score`는 ML 확률이 아니며, 둘을 같은 의미로 사용하지 않는다.

## 3. 상태 확인

### `GET /health`

정상 응답은 HTTP `200`이다.

```json
{
  "status": "ok",
  "rule_engine": {
    "status": "ready",
    "rules_loaded": 29
  },
  "ml": {
    "status": "ready",
    "available": true,
    "reason": null,
    "feature_count": 10,
    "known_rule_count": 29,
    "risk_score_policy": "pending_team_decision"
  }
}
```

Extension은 MVP에서 `/health` 응답 필드에 의존하지 않아도 된다. 개발자가
서버와 모델 준비 상태를 확인하는 용도로 사용한다.

## 4. 코드 분석

### `POST /detect`

요청 헤더:

```http
Content-Type: application/json
```

요청 본문:

```json
{
  "code": "password = \"super-secret-value\"",
  "language": "python",
  "file_name": "auth.py"
}
```

| 필드 | 타입 | 필수 | 규칙 |
| --- | --- | --- | --- |
| `code` | string | 예 | 분석할 전체 소스 코드. 빈 문자열은 허용한다. |
| `language` | string | 예 | MVP에서는 대소문자를 구분하지 않는 `python`만 허용한다. |
| `file_name` | string | 예 | 비어 있지 않은 파일명 또는 경로. path allowlist 판정에 사용한다. |

알 수 없는 추가 요청 필드는 무시한다.

정상 응답은 HTTP `200`이다.

```json
{
  "risk_score": null,
  "findings": [
    {
      "rule_id": "A04-798-001",
      "cwe": "CWE-798",
      "category": "secret",
      "severity": "high",
      "line": 0,
      "start_col": 0,
      "end_col": 31,
      "message": "하드코딩된 비밀값 패턴이 감지되었습니다.",
      "detail": "Hardcoded Generic Secret Variables 룰에 의해 탐지되었습니다.",
      "legal": {
        "law": "개인정보보호법",
        "article": "§29",
        "description": "안전조치 의무 위반 소지가 있습니다.",
        "liability": null,
        "sanction": null
      }
    }
  ],
  "analyzed_at": "2026-07-26T06:53:02.185Z"
}
```

### 최상위 응답 필드

| 필드 | 타입 | 필수 | 규칙 |
| --- | --- | --- | --- |
| `risk_score` | number \| null | 예 | `0`~`100`. 서버 정책이 미정이면 `null`이며 Extension이 계약 공식을 사용해 계산한다. |
| `findings` | Finding[] | 예 | 탐지 결과. 결과가 없으면 빈 배열이다. |
| `analyzed_at` | string | 예 | UTC ISO 8601 시각이다. |

### Finding

| 필드 | 타입 | 필수 | 규칙 |
| --- | --- | --- | --- |
| `rule_id` | string | 예 | 룰셋의 고유 ID이다. |
| `cwe` | string | 예 | 기본적으로 `CWE-NNN`. 여러 값이면 쉼표로 구분할 수 있다. |
| `category` | BackendCategory | 예 | 아래의 백엔드 카테고리 중 하나이다. |
| `severity` | `high` \| `medium` \| `low` | 예 | Extension에서 각각 `error`, `warning`, `info`로 변환한다. |
| `line` | integer | 예 | 0-based 시작 줄이다. |
| `start_col` | integer | 예 | 0-based 시작 열이다. |
| `end_col` | integer | 예 | 동일 줄의 exclusive 끝 열이다. |
| `message` | string | 예 | 사용자에게 보여줄 탐지 요약이다. |
| `detail` | string | 예 | 룰 또는 대응 방법에 대한 상세 설명이다. |
| `legal` | Legal \| null | 아니요 | 법적 정보가 없으면 생략하거나 `null`로 보낸다. |
| `fix` | Fix \| null | 아니요 | 안전한 자동 치환이 가능한 경우에만 제공한다. |

현재 응답에는 `end_line`이 없다. 여러 줄에 걸친 패턴은 시작 줄에서 첫 줄의
끝까지만 표시한다.

## 5. 카테고리 변환

백엔드는 탐지 의미를 보존하기 위해 상세 카테고리를 반환하고, Extension의
API 어댑터가 이를 UI 카테고리로 변환한다.

| 백엔드 `category` | Extension 카테고리 |
| --- | --- |
| `secret`, `privacy`, `information_exposure`, `logging` | `secret` |
| `input_validation`, `path_traversal`, `command_injection`, `sql_injection`, `code_injection`, `xss`, `insecure_deserialization`, `ssrf` | `injection` |
| `cryptography`, `tls` | `crypto` |
| `resource_exhaustion` | `cost` |
| `csrf`, `file_upload`, `access_control` | `other` |

알 수 없는 카테고리는 `other`로 처리한다.

## 6. Legal

```json
{
  "law": "개인정보보호법",
  "article": "§29",
  "description": "안전조치 의무 위반 소지가 있습니다.",
  "liability": 2,
  "sanction": 1
}
```

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| `law` | string | 예 |
| `article` | string | 예 |
| `description` | string | 예 |
| `liability` | `1` \| `2` \| `3` \| null | 예 |
| `sanction` | `0.5` \| `1` \| `2` \| null | 예 |

Extension의 점수 계산에서 `liability: null`은 `1`, `sanction: null`은 `0.5`로
처리한다. `legal` 자체가 없거나 `null`이면 법적 가중치는 `1.0`이다.

## 7. Fix

```json
{
  "title": "SHA-256으로 교체",
  "replacement": "hashlib.sha256"
}
```

`replacement`는 `line`, `start_col`, `end_col`이 지정한 범위를 그대로 대체할
실행 가능한 소스 코드여야 한다. 설명 문장, 의사 코드, 추가 import 없이는
동작하지 않는 코드는 `replacement`로 보내지 않는다. 이 조건을 만족하지
못하면 서버는 `fix`를 생략하거나 `null`로 보낸다.

## 8. 위험 점수

서버가 `risk_score`를 숫자로 제공하면 Extension은 해당 값을 사용한다.
`null`이면 ML 필터를 통과한 findings로 다음 공식을 적용한다.

```text
score = Σ(기술 심각도 × 법적 가중치)
최종 점수 = min(100, round(score))
```

기술 심각도:

| severity | 가중치 |
| --- | ---: |
| `high` | 25 |
| `medium` | 12 |
| `low` | 4 |

법적 가중치는 `liability + sanction`이다. `legal`이 없으면 `1.0`을 사용한다.

## 9. 오류 응답

유효하지 않은 요청은 HTTP `400`과 다음 형식을 반환한다.

```json
{
  "error": "현재 지원하는 language 값은 python뿐입니다."
}
```

다음 경우가 `400`에 해당한다.

- 요청 본문이 JSON 객체가 아닌 경우
- `code`, `language`, `file_name`이 없거나 문자열이 아닌 경우
- `language`가 `python`이 아닌 경우
- `file_name`이 빈 문자열인 경우

Extension은 모든 non-2xx 응답을 분석 실패로 처리하며, 오류 응답의 추가
필드에는 의존하지 않는다.

## 10. MVP 클라이언트 동작

- 기본 엔드포인트는 `http://localhost:5000/detect`이다.
- 요청 타임아웃은 10초이다.
- 네트워크 오류, 타임아웃, non-2xx 응답은 원격 분석 실패로 처리한다.
- MVP에는 인증 헤더가 없다.
- VS Code Extension Host의 Node `fetch`가 직접 호출하므로 브라우저 CORS는
  MVP 연결 조건이 아니다.

## 11. 호환성 규칙

- 서버는 응답에 선택 필드를 추가할 수 있고 Extension은 알 수 없는 필드를 무시한다.
- 기존 필드 삭제, 타입 변경, 좌표 기준 변경은 breaking change이다.
- breaking change가 필요하면 `/api/v2/detect` 같은 새 버전 경로를 사용한다.
