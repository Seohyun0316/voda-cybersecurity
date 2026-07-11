# VibeSafe 🛡️

**AI 생성 코드(바이브코딩)의 보안 취약점을 실시간으로 탐지·경고하는 VS Code 익스텐션**

ChatGPT, Claude, Cursor 등이 생성한 코드에는 하드코딩된 API 키, 취약한 암호화,
인젝션 위험 같은 보안 문제가 자주 포함됩니다. VibeSafe는 이런 코드를 붙여넣는
순간 취약점을 감지하고, **기술적 위험과 함께 관련 법 조항까지** 알려줍니다.

## 특징

- **실시간 탐지**: VS Code에서 코드 작성·붙여넣기 시 인라인 경고 표시
- **2단계 탐지**: 정규표현식 룰셋으로 후보 추출 → RandomForest로 오탐(더미 값, placeholder) 필터링
- **법적 위험 안내**: CWE 유형별로 개인정보보호법·AI 기본법 등 관련 조항 및 제재 수준 표시
- **위험도 점수**: 빈도 × 기술 심각도 × 법적 가중치 기반 산정

## 탐지 범위

OWASP Top 10 (2025), CWE Top 25, OWASP LLM Top 10 기반

| 카테고리 | 주요 CWE |
|---|---|
| PII 노출 (자체 추가) | CWE-359, 200, 532, 201, 598, 209 |
| 보안 오설정 (A02) | CWE-352, 434, 862, 295* |
| 암호화 실패 (A04) | CWE-798, 256, 327, 330, 200 |
| 인젝션 — Input (A05) | CWE-20, 77, 78, 89, 94 |
| 인젝션 — Output (A05) | CWE-79, 502, 918 |
| 예외 처리 (A10) | CWE-770 |

## 아키텍처

```
VS Code Extension (TypeScript)
        │  POST /detect
        ▼
Flask API Server
        │
        ▼
Regex Ruleset (1차 후보 추출) → RandomForest (오탐 필터)
```

## 📁 저장소 구조

```
voda-cybersecurity/
├── docs/                   # 프로젝트 문서
│   ├── taxonomy.md         #   취약점 분류 체계 (CWE·OWASP·PII 매핑표)
│   ├── risk-scoring.md     #   위험도 산정 공식 (빈도 × 심각도 × 법적 가중치)
│   ├── legal-mapping.md    #   CWE ↔ 법 조항·처벌 사례 매핑
│   └── api-spec.md         #   /detect API 요청·응답 스키마
├── ruleset/                # 정규표현식 탐지 룰셋 + 검증 스크립트
│   ├── ruleset.toml        #   탐지 룰 정의
│   ├── validate.py         #   룰 컴파일 검사
│   ├── smoke.py            #   탐지 동작 테스트
│   └── perf_coverage.py    #   성능·커버리지 측정
├── server/                 # Flask API 서버 (ML/백엔드 파트)
│   ├── app.py              #   /detect 엔드포인트
│   ├── detector/           #   정규식 매칭 + RandomForest 오탐 필터
│   └── model/              #   모델 학습 스크립트
├── extension/              # VS Code 익스텐션 (프론트엔드 파트)
│   └── src/                #   TypeScript 소스
├── data/                   # 데이터 수집
│   ├── scripts/            #   GitHub·AI 코드 수집 스크립트
│   ├── ai_generated/       #   LLM 생성 코드 샘플 (커밋 OK)
│   └── schema.sql          #   samples / findings DB 스키마
│   ※ GitHub 크롤링 원본은 data/raw/ (로컬 전용, 커밋 금지)
└── .github/workflows/      # CI (룰셋 자동 검증)
```


## 시작하기

### 서버 실행
```bash
cd server
pip install -r requirements.txt
python app.py
```

### 익스텐션 실행 (개발 모드)
```bash
cd extension
npm install
# VS Code에서 F5로 Extension Development Host 실행
```

### 룰셋 검증
```bash
cd ruleset
python validate.py && python smoke.py && python perf_coverage.py
```

## 팀

VODA 사이버보안팀 (6인)
- **PM**: 양서현
- **ML/Backend**: 김현빈, 박은진
- **Frontend/Extension**: 김수린, 안태훈
- **Legal**: 심민주

## 라이선스 / 고지

본 프로젝트는 교육·연구 목적으로 개발되었습니다. 탐지 결과의 법률 안내는
참고용이며 법률 자문을 대체하지 않습니다.
