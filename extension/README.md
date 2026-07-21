# VibeSafe

AI 생성 코드의 보안 취약점과 법적 리스크를 VS Code에서 실시간으로 알려주는 extension.

## 빠른 시작

```bash
npm install
npm run compile
```

VS Code로 이 폴더를 열고 **F5** → 새로 뜬 창에서 `sample/auth.py` 열기.

## 명령어

- `npm run compile` — TypeScript 빌드
- `npm run watch` — 변경 감지 빌드
- `npm test` — 룰 엔진 유닛 테스트
- `npm run mock-server` — 가짜 ML 백엔드 (포트 8788)

## 개발 가이드

파트별 튜토리얼과 F1/F2 역할 분담, ML 백엔드 연결 방법은 **TUTORIAL.md** 참고.
