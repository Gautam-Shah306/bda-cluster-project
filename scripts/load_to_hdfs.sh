#!/usr/bin/env bash
# Purpose: copy the local raw datasets (and any scraped runs) into HDFS under /skills_mirage/raw.
# Usage:   scripts/load_to_hdfs.sh            (cluster must be up)
# Reads:   dataset/raw/jobs, dataset/raw/courses, dataset/raw/scraped_* (when present)
set -euo pipefail
export MSYS_NO_PATHCONV=1   # Git Bash on Windows would otherwise rewrite /skills_mirage paths
cd "$(dirname "$0")/.."
for name in jobs courses scraped_jobs scraped_courses; do
  src="dataset/raw/$name"
  [ -d "$src" ] || { echo "skip $src (not found)"; continue; }
  docker exec hdp-master hdfs dfs -mkdir -p "/skills_mirage/raw/$name"
  docker exec hdp-master bash -c "hdfs dfs -put -f /workspace/$src/* /skills_mirage/raw/$name/"
  echo "loaded $src"
done
docker exec hdp-master hdfs dfs -ls -R /skills_mirage/raw
