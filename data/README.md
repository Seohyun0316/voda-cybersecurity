# Data

## ⚠️ 원본 수집 데이터는 절대 커밋하지 마세요
수집 코드에는 실제 API 키·개인정보가 포함될 수 있습니다.
`data/raw/`, `data/collected/`는 .gitignore에 등록되어 있습니다.
실제 값은 반드시 마스킹 후 사용하세요.

## 수집 소스
1. AI 생성 코드 (ChatGPT / Claude / Cursor 프롬프팅)
2. GitHub Search API (위험 패턴 + 안전 패턴 별도 쿼리)
3. 참가자 실험 (비전공자 대상)

목표: 500~600개 라벨링 샘플

## 라벨링
- findings.is_true_positive: 진짜 위험 1 / 오탐(더미, placeholder, 테스트 코드) 0
- 샘플 20% 교차 검증, 나머지 단일 라벨링 + L 검수
