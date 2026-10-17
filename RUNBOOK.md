# RUNBOOK: run Skills Mirage on Hadoop and see the output

Everything here is **untested on a real cluster** (written without Docker access). Expect to fix a few things on the first run; Part D lists the likely ones. Run the shell scripts from **Git Bash** or **WSL** on Windows (not PowerShell), from the repo root.

## Part A. One-time setup (manual)

1. Install Docker Desktop (Compose v2). In Settings > Resources give Docker **at least 10 GB RAM** and 4 CPUs.
2. Install Git for Windows (gives Git Bash). Keep the repo checked out with LF line endings; `.gitattributes` handles `.sh` files. If a script fails with `\r: command not found`, run `dos2unix scripts/*.sh config/cluster/entrypoint.sh`.
3. `cp .env.example .env`, then edit `.env`: set `MONGO_ROOT_PASSWORD`, `HIVE_DB_PASSWORD`, `JWT_SECRET_KEY` (`python -c "import secrets; print(secrets.token_hex(32))"`), and make the port inside `MONGO_URI` equal `MONGO_HOST_PORT`. Add your Gemini key(s) if you want the worker pages and chatbot to answer.
4. Put the datasets here (they are not in git, ask the team):
   - `dataset/raw/jobs/naukri_jobs.csv`  (52,349,369 bytes)
   - `dataset/raw/courses/courses.csv`   (132,640 bytes)

## Part B. Run it on Hadoop (one command)

```bash
scripts/demo_on_hadoop.sh          # pauses after each step so you can take screenshots
scripts/demo_on_hadoop.sh --yes    # no pauses
scripts/demo_on_hadoop.sh --from 4 # resume at step 4 after fixing a failure
```

What each step does (you can also run the script named in the second column alone):

| Step | Script | What you should see |
|---|---|---|
| 1 | `scripts/preflight.sh` | all lines OK |
| 2 | `scripts/cluster_up.sh` | images build (first time 5-15 min), then `Cluster ready: 2 DataNodes` |
| 3 | `scripts/cluster_smoke.sh` | HDFS report with 2 live DataNodes; `yarn node -list` with 2 nodes; a 30 MB file split into 4 blocks with replicas on both workers; `PASS: Spark on YARN wrote and read Parquet on HDFS`; evidence saved to `output/cluster_evidence_*.txt` |
| 4 | `scripts/load_to_hdfs.sh` | `loaded dataset/raw/jobs`, `loaded dataset/raw/courses`, then an HDFS listing |
| 5 | `scripts/run_pipeline_cluster.sh` | 8 steps `=== name ===` each ending `finished in N s`, then `Pipeline finished`. Watch jobs live at http://localhost:8088 |
| 6 | `scripts/create_hive_tables.sh` | beeline output ending with the jobs row count 22979 and the top 5 cities |
| 7 | `scripts/show_results.sh` | cluster report, HDFS tree, block locations of the jobs CSV, finished YARN apps, Hive query results, Mongo counts (saved to `output/results_*.txt`) |

Web pages to open and screenshot (save into `screenshots/` as `NN_short_description.png`):
- http://localhost:9870 NameNode: Datanodes tab (2 live), Utilities > Browse the file system > `/skills_mirage`; click `raw/jobs/naukri_jobs.csv` to see the block list.
- http://localhost:8088 ResourceManager: Nodes (2 active) and the finished applications.

Mapping to the course demo checklist (HOW_WE_WORK Section 10): node configuration = `config/` + compose file; cluster status and DataNodes = steps 3 and 7 section 1-2; HDFS file distribution = step 3 and step 7 section 4; MapReduce/Spark job execution = step 5 and 7 section 5; output/result = step 7 sections 6-7 and Part C.

## Part C. See the same results in the web app (manual)

The dashboard reads the MongoDB collections the cluster run just filled.

```bash
# terminal 1, repo root, Python 3.11 venv activated, pip install -r requirements.txt done
cd src/frontend && npm install && cd ../..    # once
scripts/start_app.sh                           # API on :8000 and dashboard on :5173
```
Open http://localhost:5173, create an account, sign in. Expected: Dashboard shows **22,979** jobs and top city **Bengaluru/Bangalore**; Hiring Trends, Skills Intelligence and AI Vulnerability show charts; Worker Analysis, Reskilling Paths and AI Chatbot need a Gemini key in `.env`. Chatbot data questions additionally need local processed data (`python pipeline/run_pipeline.py` once in local mode with `PIPELINE_MODE` unset).

## Part D. If something fails

| Symptom | Likely cause and fix |
|---|---|
| Image build fails downloading Hadoop or Hive | The URL or version moved. Edit `ARG HADOOP_VERSION` / `HIVE_VERSION` in `config/cluster/hadoop.Dockerfile` (look on https://archive.apache.org/dist/), or the jar URL in `hive.Dockerfile`. |
| `Timed out waiting for DataNodes` | `docker logs hdp-master` and `docker logs hdp-worker1`. Common: not enough Docker RAM, or an old HDFS volume with a different cluster id (`docker volume rm` the `hdp_*` volumes only; never the `mongo_data` volume). |
| Step 3 Spark job hangs in ACCEPTED | YARN has no room: raise Docker RAM or lower `spark.executor.memory` in `config/spark/spark-defaults.conf`. See http://localhost:8088. |
| Spark error about the Hive metastore or `hive-jars` | Spark 3.5 to Hive 3.1.3 integration is the least certain part. First check `docker logs hive-metastore`. To rule Hive out, temporarily remove the four `spark.sql.hive.metastore.*` and `spark.hadoop.hive.metastore.uris` lines in `config/spark/spark-defaults.conf`; if the job then runs, the problem is the jar path. Tell me the exact error and I will adjust. |
| `hdfs: command not found` | You ran a command with a login shell; use the scripts, or `docker exec hdp-master bash -c "..."` (not `-lc`). |
| Paths like `C:/Program Files/Git/skills_mirage` appear | Run from Git Bash with the scripts (they set `MSYS_NO_PATHCONV=1`), or use WSL. |
| Step 5 fails at `load_results_to_mongo` | MongoDB container not running: `docker ps` should list `skills-mirage-mongo`. |
| Hive step: connection refused | HiveServer2 takes about a minute after the metastore. Wait and re-run `scripts/create_hive_tables.sh`. |

## Part E. Stop and clean up

```bash
scripts/cluster_down.sh        # stops containers, keeps all data (HDFS volumes and MongoDB users)
```
Never run `docker compose down -v`: it deletes the MongoDB users.
