#!/usr/bin/env bash
# Purpose: print everything worth screenshotting for the demo: cluster report, HDFS files and
#          blocks, finished YARN jobs, Hive query results and the MongoDB result collections.
# Usage:   scripts/show_results.sh            (cluster up and pipeline run)
# Saves:   output/results_<timestamp>.txt (git-ignored)
set -uo pipefail
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
mkdir -p output
OUT="output/results_$(date +%Y%m%d_%H%M%S).txt"
DB=$(grep -E '^MONGO_DB=' .env 2>/dev/null | cut -d= -f2- | tr -d '\r'); DB=${DB:-skills_mirage_db}
H="docker exec hdp-master"
sec() { echo; echo "=================== $*"; }
{
  sec "1. HDFS cluster report (live DataNodes, capacity)"
  $H hdfs dfsadmin -report | sed -n '1,30p'
  sec "2. YARN nodes (the two NodeManagers)"
  $H yarn node -list -all
  sec "3. Files in HDFS (raw CSVs, processed Parquet, analytics Parquet)"
  $H hdfs dfs -ls -R /skills_mirage | sed -n '1,70p'
  $H hdfs dfs -du -h /skills_mirage
  sec "4. Block distribution of the jobs CSV (8 MB blocks, replication 2, which DataNode holds each)"
  $H hdfs fsck /skills_mirage/raw/jobs -files -blocks -locations | sed -n '1,40p'
  sec "5. Spark jobs that ran on YARN"
  $H yarn application -list -appStates FINISHED | sed -n '1,30p'
  sec "6. Hive: tables and queries over the HDFS data"
  docker exec hive-server2 beeline -u jdbc:hive2://localhost:10000/skills_mirage --silent=true \
    -e "SHOW TABLES; SELECT COUNT(*) AS jobs_rows FROM jobs; SELECT city, COUNT(*) AS n FROM jobs GROUP BY city ORDER BY n DESC LIMIT 5; SELECT source, COUNT(*) AS n FROM courses GROUP BY source;" \
    || echo "(Hive not available: run scripts/create_hive_tables.sh)"
  sec "7. MongoDB result collections (precomputed by the pipeline)"
  docker exec skills-mirage-mongo bash -c "mongosh -u \"\$MONGO_INITDB_ROOT_USERNAME\" -p \"\$MONGO_INITDB_ROOT_PASSWORD\" --authenticationDatabase admin --quiet $DB --eval 'db.getCollectionNames().filter(n=>n.startsWith(\"res_\")).sort().forEach(n=>print(n.padEnd(22), db.getCollection(n).countDocuments())); print(\"\"); printjson(db.res_stats.findOne({}, {_id:0, seq:0}))'"
  echo
  echo "Expected counts: res_stats 1, res_top_cities 10, res_top_roles 10, res_industry 5, res_city_roles 540,"
  echo "res_role_cities 19261, res_hiring_trends 18, res_skill_years 4, res_skill_trends 100, res_skill_gap 10,"
  echo "res_vuln_roles 17353, res_vuln_regions 152, res_vuln_table 100, res_reskill_jobs 22448,"
  echo "res_reskill_courses 398, res_reskill_index 1062, res_latest_jobs 50, res_courses 398"
} 2>&1 | tee "$OUT"
echo; echo "Saved to $OUT"
echo "Web UIs:  NameNode http://localhost:9870   ResourceManager http://localhost:8088"
