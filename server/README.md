# VibeSafe 서버

VibeSafe 서버는 Python 소스 코드에서 보안 취약 가능성을 탐지하는 Flask 백엔드입니다. TOML 룰 엔진으로 후보를 찾고, 10피처 XGBoost 모델로 각 룰 후보의 취약 확률을 계산합니다.

## 현재 상태

- Python 분석 및 프로젝트 활성 룰 32개 지원
- 10피처 XGBoost 모델과 룰별 취약 확률 계산 지원
- ML 학습 룰 29개와 의도적 룰 전용 탐지 3개 지원
- `GET /health`, `POST /detect` 제공
- 자동 테스트 14개 통과
- 확률 합산 정책 미정으로 `risk_score`는 현재 `null`

## 구조

```text
server/
|-- app.py                         # 로컬 서버 진입점
|-- config/ruleset.toml            # 탐지 룰
|-- models/xgboost_10f/
|   |-- source_bundle.pkl          # 신뢰된 원본 모델 bundle
|   |-- model.json                 # 런타임 모델
|   `-- metadata.json              # 인코더·스케일러 메타데이터
|-- scripts/                       # 변환·피처 생성·학습·수동 예측
|-- tests/                         # 자동 테스트
`-- vibesafe/
    |-- api.py                     # Flask API
    |-- detector.py                # 탐지 흐름
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

모델은 룰 후보별 확률을 계산하지만 여러 확률을 하나의 위험 점수로 합치는 기준이 아직 없어 `risk_score`는 의도적으로 `null`을 반환합니다.

## 테스트

```powershell
python -m pip install -r requirements-dev.txt
python -B -m pytest -p no:cacheprovider -q
```

정상 결과는 `14 passed`입니다. ML만 확인하려면 다음을 실행합니다.

```powershell
python scripts/predict_model.py A04-798-001 --code 'password = "secret-value"'
```

## 모델 파일 주의사항

운영 서버는 pickle을 직접 읽지 않고 `model.json`과 `metadata.json`을 사용합니다. Pickle은 임의 코드를 실행할 수 있으므로 신뢰할 수 있는 `source_bundle.pkl`만 다음 명령으로 변환해야 합니다.

```powershell
python scripts/convert_model.py
```

남은 작업은 [TODO.md](TODO.md)에서 관리합니다.
