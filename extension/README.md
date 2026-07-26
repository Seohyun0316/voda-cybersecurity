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

## 폴더 구조

```text
extension/
├─ .vscode/       # F5 Extension Development Host 설정
├─ media/         # 확장 화면에서 사용하는 아이콘과 로고
├─ mock-server/   # 원격 분석 API 개발용 서버
├─ sample/        # 데모 및 수동 확인용 코드
├─ scripts/       # 개발 보조 스크립트
├─ src/           # 실제 TypeScript 확장 소스와 테스트
├─ reference/     # 실행에 사용하지 않는 팀원 원본·보존 파일
├─ out/           # TypeScript 빌드 결과(자동 생성)
└─ package.json   # 확장 실행 기준 패키지
```

실제 수정과 실행은 이 폴더의 `src`, `media`, `package.json`을 기준으로 합니다.
`reference`는 병합 전 원본을 삭제하지 않고 보관하는 용도입니다.
