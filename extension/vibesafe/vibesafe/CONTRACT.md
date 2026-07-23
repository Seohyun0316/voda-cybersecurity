# VibeSafe 개발 계약서 (확정본)

F1, F2가 합의해야 할 것들을 미리 전부 정해둔 문서. Day 1에 이 문서를 같이 읽고 이의 없으면 그대로 개발 시작. **여기 적힌 것을 바꾸려면 반드시 둘이 동의 후 이 문서와 코드를 함께 수정한다.**

---

## 1. 데이터 계약 (types.ts — 이미 코드로 구현됨)

| 항목 | 확정값 |
|---|---|
| 위치 좌표 | `line`, `startCol`, `endCol` 모두 **0-based** (VS Code API 기준) |
| severity | `error` \| `warning` \| `info` 세 가지만. 추가 금지 |
| category | `secret` \| `injection` \| `crypto` \| `cost` \| `other` 다섯 가지만 |
| ruleId | kebab-case 영문 (예: `hardcoded-password`). 룰 추가 시 F2가 명명 |
| message | 한국어, 한 줄, "무엇이 위험한지" (예: `하드코딩 비밀번호 — 개인정보보호법 §29`) |
| detail | 한국어, 한 줄, "어떻게 고치는지" (예: `환경변수(.env) 사용 권장`) |
| legal | 법적 근거 있을 때만 채움. `{ law, article, description, liability, sanction }` — liability/sanction은 아래 표의 값 필수 |
| fix.replacement | 해당 범위(line, startCol~endCol)를 **통째로 대체**할 문자열 |
| analyzedAt | ISO 8601 문자열 |

**위험도 점수 (computeRiskScore — 변경 금지)**

확정 공식: **위험 점수 = Σ (빈도 × 기술 심각도 가중치 × 법적 가중치)**, 100점 만점

- 기술 심각도 가중치: error 25, warning 12, info 4
- **법적 가중치 = 법적 책임도 + 제재 수준** (`legal` 없으면 ×1.0)

| 법적 책임도 (`legal.liability`) | 값 |
|---|---|
| 형사처벌 규정 | 3 |
| 과징금·과태료 부과 가능한 의무조항 | 2 |
| 일반 관리·안전조치 의무 | 1 |

| 제재 수준 (`legal.sanction`) | 값 |
|---|---|
| 형사처벌 또는 1억 이상 과징금 사례 | 2 |
| 과징금·과태료 사례 | 1 |
| 시정명령·권고 또는 사례 없음 | 0.5 |

- 법적 가중치 범위: 최소 1.5 (1+0.5) ~ 최대 5 (3+2)
- 빈도: 같은 위험이 n번 탐지되면 n번 합산, 총합 반올림 후 상한 100
- 라벨: 70 이상 `높음`, 40~69 `중간`, 1~39 `낮음`, 0 `안전`
- 예시: 하드코딩 비밀번호(error 25) × §29 가중치(책임도 2 + 제재 1 = 3) = **75점**
- 예시(sample/auth.py): 75 + API 키 25 + SQL injection 12 + md5 12 = 124 → **상한 적용 100점 높음**
- 룰에 `legal`을 붙일 때는 F2가 위 표에서 liability/sanction 값을 정해 기입한다 (법령·사례 근거 주석 권장)
- ML 백엔드가 `riskScore`를 직접 보낼 때도 **반드시 이 공식**을 따른다 (생략 시 클라이언트가 계산)

## 2. API 계약 (ML 백엔드 /detect — F 파트 확정 v1.0)

백엔드가 아직 스키마를 정의하지 않았으므로 **F 파트가 확정해서 전달한다.**
전체 스펙 문서는 `api-spec.md` (저장소 `docs/api-spec.md` 교체용),
살아있는 레퍼런스는 `mock-server/server.js`.

| 항목 | 확정값 |
|---|---|
| 엔드포인트 | `POST /detect`, `Content-Type: application/json` |
| 요청 | `{ code, language, file_name? }` |
| 응답 | `{ risk_score, findings[], analyzed_at? }` |
| finding | `{ rule_id, cwe?, category, severity(high\|medium\|low), line, start_col, end_col, message, detail?, risk_score?, legal?, fix? }` |
| 좌표 | `line`, `start_col`, `end_col` 모두 **0-based** (VS Code 기준 — 변환 없음) |
| severity 매핑 | high → error, medium → warning, low → info (어댑터 고정) |
| legal | `{ law, article, description, liability(1~3), sanction(0.5~2) }` — §1 표 값 사용, legal-mapping.md 기준 |
| risk_score | §1 공식으로 백엔드가 계산. 생략 시 클라이언트가 동일 공식으로 계산 |
| 오류 | 4xx/5xx + `{ "error": "메시지" }` |
| 타임아웃 | 클라이언트 10초. 초과·실패 시 로컬 규칙 엔진으로 자동 폴백 |
| 인증 | v1 없음. 연결 시 `Authorization: Bearer <token>` (remoteAnalyzer.ts TODO 위치) |
| 기본 URL | `http://localhost:5000/detect` (Flask). mock 테스트는 `http://localhost:8788/detect` |

백엔드(M 파트)에 전달할 것: `api-spec.md` + `mock-server/server.js` 두 개.
"구현 후 mock 서버와 응답을 비교해서 같은 형태면 연결 완료"라고 안내하면 된다.

## 3. 코드 소유권 (충돌 방지)

| 파일 | 소유자 | 상대방 규칙 |
|---|---|---|
| `src/diagnostics.ts`, `src/riskPanel.ts`, `src/statusBar.ts` | F1 | 수정 시 PR로만 |
| `src/analyzer/ruleEngine.ts`, `src/analyzer/remoteAnalyzer.ts`, `src/codeActions.ts`, `mock-server/`, `src/test/` | F2 | 수정 시 PR로만 |
| `src/analyzer/types.ts` | **공동** | 둘 다 승인해야 머지 |
| `src/extension.ts`, `package.json` | **공동** | 둘 다 승인해야 머지 |

## 4. 이름 규칙 (이미 코드에 적용됨 — 새로 만들 때 따를 것)

- 명령 ID: `vibesafe.<동사구>` (예: `vibesafe.analyzeFile`, `vibesafe.showPanel`)
- 뷰 ID: `vibesafe.riskPanel`, 뷰 컨테이너 ID: `vibesafe`
- 설정 키: `vibesafe.<camelCase>` — 현재 `engine`(기본 `rules`), `remoteEndpoint`(기본 `http://localhost:5000/detect`), `debounceMs`(기본 `500`)
- 진단 source: `VibeSafe`, DiagnosticCollection 이름: `vibesafe`

## 5. 동작 스펙

- 지원 언어: python, javascript, typescript, javascriptreact, typescriptreact, java, go, php, ruby (`extension.ts`의 `SUPPORTED`). 추가는 공동 합의
- 분석 트리거: 파일 열기, 탭 전환, 수정 후 debounce(500ms), 명령 실행
- 미지원 파일: 아무 동작 안 함 (경고도 띄우지 않음)
- 원격 엔진 실패: 경고 메시지 1회 → `engine` 설정을 `rules`로 되돌리고 재분석

## 6. Git 규칙

- 브랜치: `main`(항상 동작) / `f1/<기능>` / `f2/<기능>`, PR로 머지
- 커밋 메시지: `[F1] 사이드 패널 점수 바 추가` 형식
- 머지 조건: `npm run compile` 성공 + `npm test` 통과
- 공동 소유 파일(§3) 변경 PR은 상대방 승인 필수

## 7. 완료 기준 (Definition of Done)

Day 4 종료 시 아래 전부 통과하면 v0.1 완성:

- [ ] `sample/auth.py` 열면 1초 내 밑줄·패널·상태바 갱신
- [ ] 경고 원인 줄 삭제 → 경고 소멸 + 점수 하락
- [ ] quick fix 적용 → 경고 소멸
- [ ] mock 서버 + remote 모드 동작, 서버 다운 시 폴백
- [ ] `npm test` 전부 통과
- [ ] `vsce package`로 .vsix 생성 및 설치 확인
