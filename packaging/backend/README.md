# VibeSafe 로컬 백엔드

이 폴더는 VibeSafe VS Code Extension의 Python 분석을 담당하는 로컬 서버입니다.
서버는 `127.0.0.1:38457`에만 바인딩되며 외부 네트워크에 공개되지 않습니다.

## Windows 설치

1. `install.cmd`를 실행합니다.
2. 설치가 끝나면 `start.cmd`를 실행합니다.
3. 다음 주소가 열리는지 확인합니다.

```text
http://127.0.0.1:38457/health
```

실행 중인 검은 창을 닫거나 `Ctrl+C`를 누르면 서버가 종료됩니다.

PowerShell에서 직접 실행하려면 다음 명령을 사용할 수 있습니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\start.ps1
```

## macOS 또는 Linux 설치

```bash
sh install.sh
sh start.sh
```

## 요구 환경

- Python 3.11 이상
- 최초 설치 시 Python 패키지를 내려받을 인터넷 연결
- 로컬 포트 `38457`

## 개인정보 처리

Extension은 분석할 소스 코드와 파일 경로를 이 로컬 서버에 전달합니다.
이 서버는 분석 결과를 저장하지 않으며 소스 코드를 로그로 기록하지 않습니다.
인터넷에 공개된 서버로 실행하는 용도로 사용하지 마세요.
