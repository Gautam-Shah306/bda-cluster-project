#!/usr/bin/env bash
# Purpose: start the API (port 8000) and the React dashboard (port 5173) on your machine so you can
#          see the cluster-computed results in a browser. They read the MongoDB filled by the cluster run.
# Usage:   scripts/start_app.sh            (Ctrl+C stops both)
# Needs:   the pipeline already run on the cluster, a venv with requirements.txt installed
#          (activate it first), Node 20+, and `npm install` done in src/frontend.
# Note:    the chatbot's DATA questions need local processed data (run the pipeline in local mode once);
#          everything else works from MongoDB. The Spark warm-up is therefore switched off here.
set -euo pipefail
cd "$(dirname "$0")/.."
export CHATBOT_WARMUP=0
unset PIPELINE_MODE
python -m uvicorn src.api.main:app --port 8000 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null || true' EXIT
cd src/frontend
npm run dev
