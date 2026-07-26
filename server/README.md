# VibeSafe 서버

VibeSafe 서버는 Python 소스 코드에서 보안 취약 가능성을 탐지하는 Flask 백엔드입니다. TOML 룰 엔진으로 후보를 찾고, 10피처 XGBoost 모델로 각 룰 후보의 취약 확률을 계산합니다.

## 현재 상태

- Python 분석 및 프로젝트 활성 룰 29개 지원
- GitHub 표본 702건, LLM 생성 299건, 보강 표본 23건을 합친 1,024건 데이터로 학습
- 보강된 10피처 XGBoost 모델과 룰별 취약 확률 계산 지원
- 활성 룰 29개와 ML 학습 룰 29개 일치
- `GET /health`, `POST /detect` 제공
- 자동 테스트 42개 통과
- 모델 확률은 서버 내부에서 정규식 후보를 2차 필터링하는 데만 사용
- 모델이 취약 확률 0.5 이상으로 판정한 후보만 `findings`로 반환
- PDF 기준 CWE별 위험도 점수와 현재 findings 중 최대 `risk_score` 반환

## 구조

```text
server/
|-- app.py                         # 로컬 서버 진입점
|-- config/ruleset.toml            # 탐지 룰
|-- final_binary_set.jsonl         # 1,024건 보강 학습 데이터셋
|-- models/xgboost_10f/
|   |-- source_bundle.pkl          # 신뢰된 원본 모델 bundle
|   |-- model.json                 # 런타임 모델
|   `-- metadata.json              # 인코더·스케일러 메타데이터
|-- scripts/                       # 변환·피처 생성·학습·수동 예측
|-- tests/                         # 자동 테스트
`-- vibesafe/
    |-- api.py                     # Flask API
    |-- detector.py                # 탐지 흐름
    |-- risk_scoring.py            # PDF 기준 위험도 산식
    |-- rule_engine.py             # TOML 룰 엔진
    `-- ml/                        # 10피처와 예측기
```

## 설치와 실행

```powershell
python -m pip install -r requirements.txt
python app.py
```

기본 로컬 주소는 `http://127.0.0.1:5000`입니다. 포트 5000은 로컬 개발에 사용해도 괜찮습니다. 다른 프로그램이나 프론트엔드가 이미 5000번을 사용한다면 변경해야 합니다.

현재 개발 서버는 `0.0.0.0:5000`으로 실행됩니다. 신뢰할 수 없는 네트워크에서는 실행하지 말고, 운영 환경에서는 Flask 개발 서버 대신 운영용 WSGI 서버와 리버스 프록시를 사용해야 합니다.

## API

상태 확인:

```http
GET /health
```

코드 탐지:

```http
POST /detect
Content-Type: application/json
```

```json
{
  "code": "password = \"super-secret-value\"",
  "language": "python",
  "file_name": "auth.py"
}
```

모델은 룰 후보별 취약 확률을 서버 내부에서 계산하고, 확률이 0.5 이상인 후보만 최종 `findings`에 포함합니다. ML 확률 자체는 위험 점수에 사용하지 않습니다. 필터를 통과한 각 finding은 `빈도 × 기술 심각도 × 법적 가중치 / 60 × 100`으로 계산하며, 응답의 최상위 `risk_score`는 현재 findings 중 가장 높은 점수입니다. finding이 없으면 `0`입니다.

## 테스트

```powershell
python -m pip install -r requirements-dev.txt
python -B -m pytest -p no:cacheprovider -q
```

정상 결과는 `42 passed`입니다. ML만 확인하려면 다음을 실행합니다.

```powershell
python scripts/predict_model.py A04-798-001 --code 'password = "secret-value"'
```

## 모델 파일 주의사항

운영 서버는 pickle을 직접 읽지 않고 `model.json`과 `metadata.json`을 사용합니다. Pickle은 임의 코드를 실행할 수 있으므로 신뢰할 수 있는 `source_bundle.pkl`만 다음 명령으로 변환해야 합니다.

```powershell
python scripts/convert_model.py
```

현재 모델은 루트의 `final_binary_set.jsonl`을 기본 입력으로 사용합니다. 같은 설정으로 다시 학습하고 운영 모델을 갱신하려면 다음 두 명령을 순서대로 실행합니다.

```powershell
python scripts/train_model.py
python scripts/convert_model.py
```

남은 작업은 [TODO.md](TODO.md)에서 관리합니다.
