#!/usr/bin/env sh
set -eu

BACKEND_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON_COMMAND=${PYTHON_COMMAND:-python3}

if [ ! -x "$BACKEND_ROOT/.venv/bin/python" ]; then
  echo "[VibeSafe] Python 가상환경을 생성합니다..."
  "$PYTHON_COMMAND" -m venv "$BACKEND_ROOT/.venv"
fi

VENV_PYTHON="$BACKEND_ROOT/.venv/bin/python"
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install --requirement "$BACKEND_ROOT/requirements.txt"

cd "$BACKEND_ROOT"
"$VENV_PYTHON" -B -c "from vibesafe.api import create_app; app = create_app(); assert app.test_client().get('/health').status_code == 200"
echo "[VibeSafe] 설치가 완료되었습니다. sh start.sh를 실행하세요."
