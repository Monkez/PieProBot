#!/usr/bin/env sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -d ".venv" ]; then
  sh scripts/install.sh
fi

.venv/bin/piepro start
