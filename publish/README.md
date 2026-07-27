# 🛡️ VibeSafe 0.1.0 배포 파일

## 📦 포함 파일

- `VibeSafe-0.1.0.vsix`: VS Code Extension 설치 파일
- `VibeSafe-backend-0.1.0.zip`: 로컬 분석 백엔드 압축 파일
- `backend/`: 위 ZIP과 같은 내용의 바로 실행 가능한 백엔드 폴더
- `USER-GUIDE.md`: 기능별 사용자 가이드
- `SHA256SUMS.txt`: 배포 파일의 SHA-256 무결성 확인값
- `release-manifest.json`: 빌드 버전과 원본 커밋 정보

## 🚀 Windows 빠른 설치

1. VS Code의 Extensions 화면에서 `...` 메뉴를 누릅니다.
2. **Install from VSIX...**를 선택합니다.
3. `VibeSafe-0.1.0.vsix`를 설치하고 VS Code를 다시 로드합니다.
4. `backend/install.cmd`를 한 번 실행합니다.
5. VibeSafe를 사용할 때 `backend/start.cmd`를 실행해 둡니다.

백엔드 ZIP을 따로 전달받았다면 먼저 압축을 해제한 뒤, 압축을 푼
`backend` 폴더 안에서 같은 명령을 실행하면 됩니다.

## ✅ 실행 확인

백엔드가 실행된 상태에서 브라우저로 다음 주소를 엽니다.

```text
http://127.0.0.1:38457/health
```

`"status": "ok"`가 표시되면 정상입니다. Extension의 기본 분석 주소도
`http://127.0.0.1:38457/detect`로 설정되어 있어 별도 변경은 필요하지
않습니다.

macOS·Linux 설치 방법과 백엔드 세부 내용은 `backend/README.md`에서
확인할 수 있습니다.

## ⚠️ 사용 전 확인

- 최초 백엔드 설치에는 Python 3.11 이상과 인터넷 연결이 필요합니다.
- 백엔드 실행 창을 닫으면 Python 원격 분석이 중지됩니다.
- 법률 정보와 위험 점수는 참고용이며 법률 자문이나 보안 인증을
  대체하지 않습니다.
- 수정 제안은 범용적인 구현 예시입니다. 프로젝트 문맥에 맞는지 검토한
  뒤 적용해 주세요.

## 🧰 배포 파일 다시 만들기

프로젝트 저장소의 깨끗한 checkout에서 다음 명령을 실행합니다.

```powershell
python -m pip install -r server\requirements-dev.txt
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-publish.ps1
```

빌드 스크립트는 의존성 설치, 테스트, VSIX·백엔드 패키징과 무결성 파일
생성을 순서대로 수행합니다.
