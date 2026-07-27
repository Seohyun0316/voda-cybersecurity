#!/usr/bin/env sh
set -eu

BACKEND_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
VENV_PYTHON="$BACKEND_ROOT/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
  echo "백엔드가 설치되지 않았습니다. sh install.sh를 먼저 실행하세요." >&2
  exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
echo "[VibeSafe] 상태 확인: http://127.0.0.1:38457/health"
echo "[VibeSafe] 종료하려면 Ctrl+C를 누르세요."
cd "$BACKEND_ROOT"
exec "$VENV_PYTHON" -B app.py
