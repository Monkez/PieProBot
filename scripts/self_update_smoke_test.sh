#!/usr/bin/env sh
set -eu
BASE="${BASE:-http://127.0.0.1:8000}"
PLAN_ID=$(curl -s -X POST "$BASE/api/self-update/plan" -H 'content-type: application/json' -d '{"goal":"smoke update"}' | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
CANDIDATE_ID=$(curl -s -X POST "$BASE/api/self-update/create-candidate" -H 'content-type: application/json' -d "{\"plan_id\":\"$PLAN_ID\"}" | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
curl -s -X POST "$BASE/api/self-update/test" -H 'content-type: application/json' -d "{\"candidate_id\":\"$CANDIDATE_ID\"}"
curl -s -X POST "$BASE/api/self-update/start-candidate" -H 'content-type: application/json' -d "{\"candidate_id\":\"$CANDIDATE_ID\"}"
curl -s -X POST "$BASE/api/self-update/healthcheck" -H 'content-type: application/json' -d "{\"candidate_id\":\"$CANDIDATE_ID\"}"
curl -s -X POST "$BASE/api/self-update/promote" -H 'content-type: application/json' -d "{\"candidate_id\":\"$CANDIDATE_ID\"}"
curl -s "$BASE/api/self-update/status"
