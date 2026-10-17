#!/usr/bin/env bash
# Purpose: build and start the Hadoop cluster (1 master + 2 workers), Hive and MongoDB.
# Usage:   scripts/cluster_up.sh            (from anywhere; it moves to the repo root)
# Needs:   Docker Desktop (Compose v2) and a filled-in .env (see .env.example).
set -euo pipefail
export MSYS_NO_PATHCONV=1   # Git Bash on Windows would otherwise rewrite /skills_mirage paths
cd "$(dirname "$0")/.."
[ -f .env ] || { echo "Missing .env (copy .env.example and fill it in)" >&2; exit 1; }
docker compose --env-file .env -f config/cluster/docker-compose.yml up -d --build
echo "Waiting for 2 DataNodes (first start formats HDFS and can take 1-3 minutes)..."
for _ in $(seq 1 60); do
  live=$(docker exec hdp-master hdfs dfsadmin -report 2>/dev/null | grep -c '^Name:' || true)
  if [ "${live:-0}" -ge 2 ]; then docker exec hdp-master hdfs dfsadmin -safemode wait; echo "Cluster ready: $live DataNodes"; exit 0; fi
  sleep 5
done
echo "Timed out waiting for DataNodes; check: docker logs hdp-master" >&2
exit 1
