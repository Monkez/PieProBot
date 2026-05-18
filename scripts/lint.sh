#!/usr/bin/env sh
set -eu
cd backend
../.venv/bin/python -m compileall app
