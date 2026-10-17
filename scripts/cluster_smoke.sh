#!/usr/bin/env bash
# Purpose: the D-010 smoke test and the demo evidence for HOW_WE_WORK Section 10:
#   node/cluster report, DataNode list, HDFS block distribution, a Spark job on YARN.
# Usage:   scripts/cluster_smoke.sh            (cluster must be up: scripts/cluster_up.sh)
# Output:  printed, and saved to output/cluster_evidence_<timestamp>.txt (git-ignored);
#          take screenshots into screenshots/ as NN_short_description.png.
set -euo pipefail
export MSYS_NO_PATHCONV=1   # Git Bash on Windows would otherwise rewrite /skills_mirage paths
cd "$(dirname "$0")/.."
mkdir -p output
OUT="output/cluster_evidence_$(date +%Y%m%d_%H%M%S).txt"
run() { echo; echo "### $*"; docker exec hdp-master bash -c "$*"; }
{
  run "hdfs dfsadmin -report"
  run "yarn node -list -all"
  run "hdfs dfs -mkdir -p /skills_mirage/smoke_files"
  # A 30 MB file -> 4 blocks of 8 MB, replicated twice over the two DataNodes.
  run "head -c 31457280 /dev/urandom > /tmp/blocks.bin && hdfs dfs -put -f /tmp/blocks.bin /skills_mirage/smoke_files/blocks.bin"
  run "hdfs fsck /skills_mirage/smoke_files/blocks.bin -files -blocks -locations"
  run "cd /workspace && PIPELINE_MODE=cluster python scripts/smoke_cluster.py"
  run "yarn application -list -appStates FINISHED"
} 2>&1 | tee "$OUT"
echo "Evidence saved to $OUT"
