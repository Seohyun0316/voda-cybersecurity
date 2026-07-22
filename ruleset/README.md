# Ruleset

- `ruleset.toml` — 정규식 룰셋 (현재 v2.1.0)
- 검증 워크플로: `validate.py` → `smoke.py` (0 FAIL 확인) → `perf_coverage.py` → commit

```bash
pip install regex
python validate.py && python smoke.py && python perf_coverage.py
```

## scan_local_dataset.py — AI 생성 코드 findings 추출

### 뭘 하는 파일인가

`data/ai_generated/<ChatGPT|Claude|Gemini>/*.py`, `*.js` 파일 전체를 **실제
`ruleset.toml` 룰셋**으로 스캔해서 findings를 JSONL로 뽑아내는 배치 스크립트다.

룰 로딩 → 키워드셋 전개 → 정규식 컴파일 → 매칭까지 전 과정을
`collect_github_code.py`의 `load_rule_set` / `prepare_rules` / `scan_content`
함수를 그대로 import해서 쓴다. 정규식 로직을 별도로 복사하지 않았기 때문에
GitHub 저장소 스캔과 항상 동일한 룰셋 기준으로 동작한다 (스캔 대상만
GitHub API 대신 로컬 폴더로 바뀔 뿐).

파일마다 각 룰이 찾은 매치 하나하나가 결과 JSONL의 한 줄이 되고, 각 줄에는
`label: null` 필드가 비어 있다. 이 자리는 사람이 채워야 하는 자리다.

### 왜 실행하는가

LightGBM 2차 오탐 필터를 학습시키려면 "룰셋이 후보로 뽑은 것 중 실제로
위험한 것(true) vs 오탐인 것(false)" 라벨이 붙은 데이터가 필요하다.

- 이 스크립트는 그 **후보(findings)를 자동으로 뽑아주는 역할**만 한다 —
  라벨링(사람 검토)은 별도로 해야 한다.
- GitHub에서 수집한 코드만으로는 "실제 사람이 AI에게 대충 요청했을 때
  나오는" 취약 패턴(트랩형 프롬프트로 유도된 코드)을 충분히 대표하지
  못하므로, LLM 생성 코드 데이터셋을 별도로 스캔해 학습 데이터 커버리지를
  보강하는 목적이다.

### 실행 방법

```bash
cd ruleset
pip install regex requests   # 아직 없으면
python scan_local_dataset.py ../data/ai_generated
```

출력 경로를 바꾸고 싶으면 두 번째 인자로 지정한다:

```bash
python scan_local_dataset.py ../data/ai_generated output/my_findings.jsonl
```

### 출력

- 기본 경로: `output/ai_generated_findings.jsonl`
- 한 줄 = finding 하나. 필드: `file, model, rule_id, rule_name, owasp, cwe,
  severity, line, column, end_line, end_column, line_preview, match_masked,
  match_hash, label`
- `model`은 `data/ai_generated/<모델명>/...` 경로에서 자동으로 채워짐
  (ChatGPT / Claude / Gemini)
- `label`을 사람이 true/false로 채우면 그대로 LightGBM 학습 데이터가 된다

### 참고

- `.py`/`.js`만 스캔 대상이다 (`collect_github_code.py`와 동일한 확장자
  범위). `.html`/`.htm` 파일은 스캔되지 않는다.
- 일부 파일(특히 ChatGPT 폴더)이 CP949(EUC-KR)로 저장돼 있어도 자동으로
  인코딩을 재시도하므로 별도 변환이 필요 없다.

## label_findings.py — findings 라벨링 CLI

### 뭘 하는 파일인가

`scan_local_dataset.py`가 뽑아낸 `label: null` findings를 터미널에서 하나씩
보여주고, 사람이 판정하면 그 자리에서 `label`을 채워 저장하는 대화형 도구다.
finding마다 룰 설명(`desc`), CWE/OWASP, 그리고 실제 소스 코드에서 매치 줄
전후 3줄을 함께 보여주므로 파일을 직접 열어보지 않아도 판단할 수 있다.

### 왜 실행하는가

`scan_local_dataset.py`는 후보만 뽑을 뿐 진짜 위험인지 오탐인지는 사람이
판정해야 한다. 이 스크립트가 그 라벨링 작업을 빠르게 반복할 수 있게
해준다 — 응답 하나마다 즉시 파일에 저장하므로 중간에 멈춰도 안전하고,
다시 실행하면 라벨이 없는 항목부터 이어서 진행한다.

### 실행 방법

```bash
cd ruleset
python label_findings.py output/ai_generated_findings.jsonl ../data/ai_generated
```

조작: `y`=진짜 위험, `n`=오탐, `s`=모르겠음(건너뜀), `u`=방금 판정 취소,
`q`=저장하고 종료.
