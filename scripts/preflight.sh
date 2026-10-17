#!/usr/bin/env bash
# Purpose: check everything the Hadoop demo needs BEFORE you start it. Changes nothing.
# Usage:   scripts/preflight.sh
# Prints OK/MISSING lines and exits 1 if something required is missing. Never prints secrets.
set -uo pipefail
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
bad=0
ok()   { echo "  OK       $*"; }
miss() { echo "  MISSING  $*"; bad=1; }

echo "Tools"
command -v docker >/dev/null && ok "docker: $(docker --version)" || miss "docker (install Docker Desktop)"
docker compose version >/dev/null 2>&1 && ok "docker compose v2" || miss "docker compose v2"
docker info >/dev/null 2>&1 && ok "Docker daemon is running" || miss "Docker daemon not running (start Docker Desktop)"
mem=$(docker info --format '{{.MemTotal}}' 2>/dev/null || echo 0)
if [ "${mem:-0}" -ge 9000000000 ]; then ok "Docker memory $((mem/1024/1024/1024)) GB"; else echo "  WARNING  Docker has less than 10 GB RAM; raise it in Docker Desktop > Settings > Resources"; fi

echo "Configuration (.env keys, values are not shown)"
if [ -f .env ]; then
  ok ".env exists"
  for k in MONGO_ROOT_USER MONGO_ROOT_PASSWORD MONGO_HOST_PORT MONGO_URI MONGO_DB JWT_SECRET_KEY HIVE_DB_PASSWORD; do
    grep -qE "^${k}=.+" .env && ok "$k set" || miss "$k not set in .env"
  done
else
  miss ".env (copy .env.example to .env and fill it in)"
fi

echo "Datasets"
for f in dataset/raw/jobs/naukri_jobs.csv dataset/raw/courses/courses.csv; do
  [ -f "$f" ] && ok "$f ($(wc -c < "$f") bytes)" || miss "$f"
done

echo "Ports that must be free (or already used by OUR containers)"
for p in 9870 8088 9083 10000; do
  if (echo > /dev/tcp/127.0.0.1/$p) >/dev/null 2>&1; then
    docker ps --format '{{.Ports}}' | grep -q ":$p->" && ok "port $p used by our cluster" || miss "port $p is used by something else"
  else ok "port $p free"; fi
done
[ $bad -eq 0 ] && echo "Preflight passed." || { echo "Preflight FAILED: fix the MISSING items."; exit 1; }
