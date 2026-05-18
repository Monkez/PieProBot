#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
REPO_PATH="${TENCENTDB_AGENT_MEMORY_HOME:-${1:-}}"

if [ -z "$REPO_PATH" ]; then
  echo "Set TENCENTDB_AGENT_MEMORY_HOME or pass the TencentDB-Agent-Memory repo path." >&2
  exit 1
fi

cd "$REPO_PATH"

if [ ! -d "node_modules" ]; then
  npm install
fi

TDAI_GATEWAY_HOST="${TDAI_GATEWAY_HOST:-127.0.0.1}" \
TDAI_GATEWAY_PORT="${TDAI_GATEWAY_PORT:-8420}" \
TDAI_DATA_DIR="${TDAI_DATA_DIR:-$ROOT/runtime/tencentdb-agent-memory}" \
node --import tsx src/gateway/server.ts

