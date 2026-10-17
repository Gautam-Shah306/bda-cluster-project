#!/usr/bin/env bash
# Purpose: create the Hive external tables over HDFS (needs hive-server2 up and the data loaded).
# Usage:   scripts/create_hive_tables.sh
set -euo pipefail
export MSYS_NO_PATHCONV=1   # Git Bash on Windows would otherwise rewrite /skills_mirage paths
cd "$(dirname "$0")/.."
docker cp scripts/create_hive_tables.sql hive-server2:/tmp/create_hive_tables.sql
docker exec hive-server2 beeline -u jdbc:hive2://localhost:10000 -f /tmp/create_hive_tables.sql
