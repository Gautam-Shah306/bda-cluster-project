#!/usr/bin/env bash
# Purpose: run the full batch pipeline on the cluster (Spark on YARN, data in HDFS).
# Usage:   scripts/run_pipeline_cluster.sh [pipeline options, e.g. --from trends_and_gap]
# Needs:   cluster up, data loaded with scripts/load_to_hdfs.sh, Mongo reachable as "mongo".
set -euo pipefail
export MSYS_NO_PATHCONV=1   # Git Bash on Windows would otherwise rewrite /skills_mirage paths
cd "$(dirname "$0")/.."
docker exec hdp-master bash -c "cd /workspace && PIPELINE_MODE=cluster python pipeline/run_pipeline.py $*"
