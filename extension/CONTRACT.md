# VibeSafe 개발 계약서 (확정본)

F1, F2가 합의해야 할 것들을 미리 전부 정해둔 문서. Day 1에 이 문서를 같이 읽고 이의 없으면 그대로 개발 시작. **여기 적힌 것을 바꾸려면 반드시 둘이 동의 후 이 문서와 코드를 함께 수정한다.**

---

## 1. 데이터 계약 (types.ts — 이미 코드로 구현됨)

| 항목 | 확정값 |
|---|---|
| 위치 좌표 | `line`, `startCol`, `endCol` 모두 **0-based UTF-16 code unit** (VS Code API 기준) |
| severity | `error` \| `warning` \| `info` 세 가지만. 추가 금지 |
| category | `secret` \| `injection` \| `crypto` \| `cost` \| `other` 다섯 가지만 |
| ruleId | kebab-case 영문 (예: `hardcoded-password`). 룰 추가 시 F2가 명명 |
| cwe | `CWE-NNN`. 여러 값이면 쉼표로 구분 |
| message | 한국어, 한 줄, "무엇이 위험한지" (예: `하드코딩 비밀번호 — 개인정보보호법 §29`) |
| detail | 한국어, 한 줄, "어떻게 고치는지" (예: `환경변수(.env) 사용 권장`) |
| legal | 법적 근거 있을 때만 채움. `{ law, article, description, liability, sanction, sanctionType? }` — liability/sanction은 아래 표의 값 필수 |
| fix.replacement | 설명문이 아닌 대체 코드 예시. `replaceEntireLine`이 true면 현재 줄 전체, false면 탐지 범위를 바꾼 미리보기로 표시 |
| analyzedAt | ISO 8601 문자열 |

**위험도 점수 (`docs/risk-scoring.md` 기준)**

확정 공식:

```text
개별 점수 = 빈도 점수 × 기술 심각도 × 법적 가중치 / 60 × 100
종합 점수 = 현재 남아있는 findings의 개별 점수 중 최댓값
```

- 기술 심각도: error 3, warning 2, info 1. 단 CWE-502는 Critical 4
- 빈도와 법적 가중치는 [`docs/risk-scoring.md`](../docs/risk-scoring.md)의 CWE별 표 사용
- 같은 위험이 반복 탐지되어도 합산하지 않음
- finding이 없으면 0, 소수 둘째 자리까지 유지
- 라벨: 70 이상 `높음`, 40~69 `중간`, 1~39 `낮음`, 0 `안전`
- 예시: CWE-798(75)과 CWE-532(60)이 함께 있으면 종합 점수는 75
- CWE-798을 수정하면 종합 점수는 60, 모두 수정하면 0
- 구버전 백엔드가 `risk_score`를 생략하거나 `null`로 보내면 클라이언트가 같은 공식으로 계산

## 2. API 계약 (MVP v1)

API의 단일 기준 문서는 저장소의 [`docs/api-spec.md`](../docs/api-spec.md)다.
이 문서에는 프론트 내부 모델과의 경계만 요약한다.

| 항목 | 확정값 |
|---|---|
| 엔드포인트 | `POST /detect`, `Content-Type: application/json` |
| MVP 언어 | `python`만 지원 |
| 요청 | `{ code, language, file_name }` — 세 필드 모두 필수 |
| 응답 | `{ risk_score: number \| null, findings: Finding[], analyzed_at: string }` |
| 좌표 | `line`, `start_col`, `end_col` 모두 0-based, `end_col`은 exclusive |
| severity 매핑 | high → error, medium → warning, low → info |
| category | 백엔드 상세 카테고리를 `api-spec.md` 표에 따라 다섯 UI 카테고리로 변환 |
| legal | `liability`, `sanction`은 MVP에서 `null` 허용. 표시용 제재 유형은 API의 `sanction_type`을 사용 |
| fix | 대체 코드 예시와 선택적 `replace_entire_line` 범위를 전달. 클라이언트는 자동 적용하지 않음 |
| ML | 룰 후보의 2차 필터이며 확률은 응답에 노출하지 않음 |
| risk_score | 서버는 현재 findings의 최대 점수를 반환; 누락/null이면 클라이언트가 §1 공식으로 계산 |
| 오류 | non-2xx를 원격 분석 실패로 처리 |
| 타임아웃 | 클라이언트 10초 |
| 인증 | MVP 없음 |
| 기본 URL | `http://127.0.0.1:38457/detect` |

백엔드 응답과 Extension 어댑터의 통합 테스트도 이 계약을 기준으로 작성한다.

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
- 설정 키: `vibesafe.<camelCase>` — 현재 `engine`(기본 `remote`), `remoteEndpoint`(기본 `http://127.0.0.1:38457/detect`)
- 진단 source: `VibeSafe`, DiagnosticCollection 이름: `vibesafe`

## 5. 동작 스펙

- 지원 언어: python, javascript, typescript, javascriptreact, typescriptreact, java, go, php, ruby (`extension.ts`의 `SUPPORTED`). Python은 remote 백엔드, 나머지는 로컬 룰 엔진으로 직접 라우팅
- 분석 트리거: **수동 검사만** (팀 확정) — 에디터 타이틀 방패 버튼, 사이드 패널 "▶ 현재 파일 검사" 버튼, 상태바 클릭, 명령 팔레트. 자동 검사 없음
- 검사 대상: 현재 열린 파일 하나. 서버는 로컬호스트에서 별도 실행 (extension이 켜고 끄지 않음, 서버 다운 시 로컬 룰 폴백)
- 미지원 파일: 검사 시 안내 메시지 표시
- 원격 엔진 실패: 경고 메시지 1회 → 해당 검사만 로컬 룰로 재분석하며 설정은 `remote`로 유지
- 수정 제안: 검사 결과가 유효한 동안 취약 코드가 있는 줄에 마우스를 올리면 해당 줄의 hover 미리보기를 표시하며, 원본 문서는 변경하지 않음

## 6. Git 규칙

- 브랜치: `main`(항상 동작) / `f1/<기능>` / `f2/<기능>`, PR로 머지
- 커밋 메시지: `[F1] 사이드 패널 점수 바 추가` 형식
- 머지 조건: `npm run compile` 성공 + `npm test` 통과
- 공동 소유 파일(§3) 변경 PR은 상대방 승인 필수

## 7. 완료 기준 (Definition of Done)

Day 4 종료 시 아래 전부 통과하면 v0.1 완성:

- [ ] `sample/auth.py`에서 검사 버튼 클릭 → 1초 내 밑줄·패널·상태바 갱신
- [ ] 경고 원인 줄 삭제 후 재검사 → 경고 소멸 + 점수 하락
- [ ] 각 취약 코드 줄에 마우스 hover → 해당 수정 제안 표시 + 원본 문서 변경 없음
- [ ] mock 서버 + remote 모드 동작, 서버 다운 시 폴백
- [ ] `npm test` 전부 통과
- [ ] `vsce package`로 .vsix 생성 및 설치 확인
