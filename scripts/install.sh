#!/usr/bin/env sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -d ".venv" ]; then
  PYTHON_BIN="${PYTHON:-python3}"
  "$PYTHON_BIN" -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -e ".[test]"

cd frontend
npm install

echo "Install complete."
