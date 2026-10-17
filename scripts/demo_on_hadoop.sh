#!/usr/bin/env bash
# Purpose: run the WHOLE Hadoop demo end to end and show the results.
#   preflight -> start cluster -> smoke test -> load data into HDFS -> run the Spark pipeline on YARN
#   -> create Hive tables -> print results.
# Usage:   scripts/demo_on_hadoop.sh [--from N] [--yes]
#            --from N  start at step N (1..7) after a failure, e.g. --from 4
#            --yes     do not pause between steps
# Needs:   Docker Desktop (about 10 GB RAM), .env filled in, datasets in dataset/raw/.
# Takes:   roughly 10-25 minutes the first time (image build and downloads), less afterwards.
set -euo pipefail
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."

FROM=1; ASK=1
while [ $# -gt 0 ]; do
  case "$1" in
    --from) FROM="$2"; shift 2 ;;
    --yes)  ASK=0; shift ;;
    *) echo "Unknown option $1" >&2; exit 2 ;;
  esac
done

step() {  # step N "title" command...
  local n="$1" title="$2"; shift 2
  [ "$n" -lt "$FROM" ] && return 0
  echo; echo "################ STEP $n: $title ################"
  "$@"
  if [ "$ASK" -eq 1 ]; then read -r -p "Step $n done. Take a screenshot if you need one, then press Enter... " _; fi
}

step 1 "Preflight checks"                        scripts/preflight.sh
step 2 "Start the cluster (HDFS, YARN, Hive, Mongo)" scripts/cluster_up.sh
step 3 "Cluster smoke test (evidence)"           scripts/cluster_smoke.sh
step 4 "Load the datasets into HDFS"             scripts/load_to_hdfs.sh
step 5 "Run the Spark pipeline on YARN"          scripts/run_pipeline_cluster.sh
step 6 "Create Hive tables over the HDFS data"   scripts/create_hive_tables.sh
step 7 "Show the results"                        scripts/show_results.sh

echo
echo "DONE. Next: start the API and the dashboard (RUNBOOK.md, Part C) to see the same data in the web app."
