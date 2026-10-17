#!/usr/bin/env bash
# Start the Hadoop daemons of one node and keep the container alive.
# Usage: entrypoint.sh master|worker      (set by docker-compose `command`)
# Master: NameNode (formats HDFS on first start) + ResourceManager.
# Worker: DataNode + NodeManager.
set -euo pipefail

ROLE="${1:-}"
export HADOOP_LOG_DIR=/var/log/hadoop
mkdir -p "$HADOOP_LOG_DIR"

case "$ROLE" in
  master)
    if [ ! -d /hadoop/dfs/name/current ]; then
      echo "Formatting the NameNode (first start)"
      hdfs namenode -format -force -nonInteractive
    fi
    hdfs --daemon start namenode
    yarn --daemon start resourcemanager
    ;;
  worker)
    hdfs --daemon start datanode
    yarn --daemon start nodemanager
    ;;
  *)
    echo "Usage: entrypoint.sh master|worker" >&2
    exit 2
    ;;
esac

echo "$ROLE daemons started; following the logs"
exec tail -F "$HADOOP_LOG_DIR"/*.log
