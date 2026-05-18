#!/usr/bin/env sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT/backend"
TWIN_AGENT_ROOT="$ROOT" ../.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

