#!/usr/bin/env sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -d ".venv" ]; then
  sh scripts/install.sh
fi

mkdir -p logs
TWIN_AGENT_ROOT="$ROOT" ./scripts/start_backend.sh > logs/backend.out.log 2> logs/backend.err.log &
BACKEND_PID=$!
NEXT_PUBLIC_API_BASE="http://127.0.0.1:8000" ./scripts/start_frontend.sh > logs/frontend.out.log 2> logs/frontend.err.log &
FRONTEND_PID=$!

echo "PiePro local dev started."
echo "Backend PID:  $BACKEND_PID  http://127.0.0.1:8000"
echo "Frontend PID: $FRONTEND_PID http://127.0.0.1:3000/dashboard"
echo "Logs: $ROOT/logs"
