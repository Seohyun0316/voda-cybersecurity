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
| PII 노출 | CWE-359, 200, 532 |
| 접근 제어 (A02) | CWE-352, 434, 862 |
| 암호화 실패 (A04) | CWE-798, 256, 327, 330, 295 |
| 인젝션 (A05) | CWE-78, 89, 94, 79, 502, 918 |
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
