# VibeSafe {{VERSION}} 배포 파일

이 폴더의 파일만으로 VibeSafe Extension과 로컬 분석 백엔드를 설치할 수 있습니다.

## 포함 파일

- `VibeSafe-{{VERSION}}.vsix`: VS Code Extension 설치 파일
- `VibeSafe-backend-{{VERSION}}.zip`: 로컬 Flask 백엔드 압축 파일
- `backend/`: 위 압축 파일과 같은 백엔드 실행 폴더
- `SHA256SUMS.txt`: 배포 파일이 손상되지 않았는지 확인하는 SHA-256 값
- `release-manifest.json`: 빌드 버전과 원본 커밋 정보

## 설치 순서

1. VS Code의 Extensions 화면에서 `...` 메뉴를 누릅니다.
2. `Install from VSIX...`를 선택하고 `VibeSafe-{{VERSION}}.vsix`를 설치합니다.
3. `backend/install.cmd`를 한 번 실행합니다.
4. VibeSafe를 사용할 때 `backend/start.cmd`를 실행합니다.
5. VS Code에서 분석할 파일을 열고 VibeSafe의 검사 버튼을 누릅니다.

백엔드는 `127.0.0.1:38457`에만 열립니다. Extension 기본 설정도
`http://127.0.0.1:38457/detect`를 사용하므로 별도 주소 설정은 필요하지 않습니다.

## 주의사항

- 최초 백엔드 설치에는 Python 패키지 다운로드를 위한 인터넷 연결이 필요합니다.
- 백엔드 창을 닫으면 Python 원격 분석은 중지되고 Extension은 로컬 규칙 엔진으로 폴백합니다.
- 법률 정보와 위험 점수는 참고용이며 법률 자문이나 보안 인증을 대체하지 않습니다.
- 수정 제안은 프로젝트 문맥에 맞게 조정해야 하는 구현 예시이며 자동 적용되지 않습니다.

## 배포 파일 재생성

저장소의 깨끗한 checkout에서 다음을 실행합니다.

```powershell
python -m pip install -r server\requirements-dev.txt
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-publish.ps1
```

빌드 스크립트는 Node 의존성을 `npm ci`로 다시 설치하고 서버·Extension 테스트를
통과한 경우에만 이 폴더를 생성합니다.
