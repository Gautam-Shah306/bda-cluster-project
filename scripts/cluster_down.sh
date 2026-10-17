#!/usr/bin/env bash
# Purpose: stop the cluster containers WITHOUT deleting any volume (HDFS data, Mongo users stay).
# Usage:   scripts/cluster_down.sh
# Never add -v here: it would delete the mongo_data volume and the users collection.
set -euo pipefail
export MSYS_NO_PATHCONV=1   # Git Bash on Windows would otherwise rewrite /skills_mirage paths
cd "$(dirname "$0")/.."
docker compose --env-file .env -f config/cluster/docker-compose.yml stop
