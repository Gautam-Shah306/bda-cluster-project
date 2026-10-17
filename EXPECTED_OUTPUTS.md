# Skills Mirage on Hadoop: Expected Outputs & Execution Guide

This document explains what is running, the **exact outputs expected at each step**, how to verify the cluster on Hadoop/YARN/HDFS, and how to start the web dashboard.

---

## 1. Architecture Overview

```
naukri_jobs.csv (52 MB) ──┐
courses.csv (132 KB)     ──┴──> HDFS (/skills_mirage/raw/)
                                    │
                                    ▼
                         PySpark Processing (on YARN)
                                    │
                                    ▼
                         HDFS (/skills_mirage/processed/ Parquet)
                                    │
                                    ├─► Hive External Tables (skills_mirage DB)
                                    ▼
                         PySpark Analytics (18 Result Sets on YARN)
                                    │
                                    ▼
                         MongoDB 7.0 (18 res_* collections)
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                  FastAPI Backend         React + Vite Frontend
                  (http://localhost:8000) (http://localhost:5173)
```

---

## 2. The 7 Steps of `scripts/demo_on_hadoop.sh`

The running automated script executes 7 sequential stages:

### Step 1: Preflight Checks (`scripts/preflight.sh`)
- **Status**: **PASSED**
- **What it checks**:
  - Docker engine & Docker Compose v2 active.
  - `.env` secrets present (MongoDB credentials, JWT secret, Hive DB password).
  - Datasets located: `dataset/raw/jobs/naukri_jobs.csv` (52,349,369 bytes) & `dataset/raw/courses/courses.csv` (132,640 bytes).
  - Cluster ports free: `9870` (NameNode), `8088` (YARN), `9083` (Hive Thrift), `10000` (HiveServer2).

---

### Step 2: Start the Cluster (`scripts/cluster_up.sh`)
- **Action**: Builds custom images (`skills-mirage-hadoop:3.3.6`, `skills-mirage-hive:3.1.3`) and boots 6 containers:
  - `hdp-master` (NameNode, ResourceManager, History Server)
  - `hdp-worker1` (DataNode 1, NodeManager 1)
  - `hdp-worker2` (DataNode 2, NodeManager 2)
  - `hive-postgres` (PostgreSQL 15 for Hive Metastore DB)
  - `hive-metastore` (Apache Hive Metastore service)
  - `hive-server2` (Hive JDBC/Beeline server)
  - `skills-mirage-mongo` (MongoDB 7.0 for user auth and analytics serving)
- **Expected Terminal Output**:
  ```text
  Cluster ready: 2 DataNodes
  ```

---

### Step 3: Cluster Smoke Test (`scripts/cluster_smoke.sh`)
- **Action**: Verifies HDFS distributed blocks and submits a test PySpark job on YARN.
- **Expected Terminal Output**:
  ```text
  === HDFS DFSADMIN REPORT ===
  Live datanodes (2):
  Name: 172.x.x.x:9866 (hdp-worker1...)
  Name: 172.x.x.x:9866 (hdp-worker2...)

  === YARN NODE REPORT ===
  Total Nodes: 2
  Node-Id: hdp-worker1:8041   State: RUNNING
  Node-Id: hdp-worker2:8041   State: RUNNING

  === SPARK ON YARN TEST ===
  PASS: Spark on YARN wrote and read Parquet on HDFS
  Evidence saved to output/cluster_evidence_<timestamp>.txt
  ```

---

### Step 4: Load Datasets into HDFS (`scripts/load_to_hdfs.sh`)
- **Action**: Uploads the raw CSV datasets from host to HDFS cluster storage with replication factor 2.
- **Expected Terminal Output**:
  ```text
  loaded dataset/raw/jobs -> hdfs://hdp-master:9000/skills_mirage/raw/jobs/naukri_jobs.csv
  loaded dataset/raw/courses -> hdfs://hdp-master:9000/skills_mirage/raw/courses/courses.csv
  Found 2 items:
  -rw-r--r--   2 root supergroup   52349369 /skills_mirage/raw/jobs/naukri_jobs.csv
  -rw-r--r--   2 root supergroup     132640 /skills_mirage/raw/courses/courses.csv
  ```

---

### Step 5: Run the Spark Pipeline on YARN (`scripts/run_pipeline_cluster.sh`)
- **Action**: Runs 8 distributed PySpark batch jobs on the YARN cluster in sequence:
  1. `process_jobs`: Cleans 22,979 Naukri job rows, extracts city/title/skills arrays, calculates AI keyword mentions -> Parquet.
  2. `process_courses`: Cleans 398 course rows, normalizes duration into integer weeks, parses syllabus JSON -> Parquet.
  3. `dashboard_stats`: Computes total jobs, top hiring cities, top roles, and industry proxies.
  4. `trends_and_gap`: Analyzes hiring trends over time, positional skill growth half-split, and skill-gap (market demand vs course supply).
  5. `vulnerability_index`: Calculates AI Vulnerability scores per role and region.
  6. `reskilling_lookup`: Builds inverted indices for reskilling engine.
  7. `serving_extras`: Extracts latest 50 jobs and course catalogs.
  8. `load_results_to_mongo`: Loads all 18 Parquet folders into MongoDB `res_*` collections.
- **Expected Terminal Output**:
  ```text
  === Running process_jobs on YARN ===
  Finished in 14 s
  === Running process_courses on YARN ===
  Finished in 8 s
  ...
  === Running load_results_to_mongo ===
  Loaded 18 collections into MongoDB
  Pipeline finished successfully.
  ```

---

### Step 6: Create Hive Tables (`scripts/create_hive_tables.sh`)
- **Action**: Runs Beeline / HiveServer2 to create external schema tables over HDFS data.
- **Expected Terminal Output**:
  ```sql
  CREATE DATABASE IF NOT EXISTS skills_mirage;
  CREATE EXTERNAL TABLE IF NOT EXISTS skills_mirage.jobs (...);
  CREATE EXTERNAL TABLE IF NOT EXISTS skills_mirage.courses (...);
  SELECT count(*) FROM skills_mirage.jobs;
  -- Result: 22979
  SELECT city, count(*) as c FROM skills_mirage.jobs GROUP BY city ORDER BY c DESC LIMIT 5;
  -- Result: Bengaluru/Bangalore, Mumbai, Delhi/NCR, Hyderabad, Pune
  ```

---

### Step 7: Show Results & Evidence (`scripts/show_results.sh`)
- **Action**: Generates a consolidated diagnostic report saved to `output/results_<timestamp>.txt`.
- **Expected Terminal Output**:
  - HDFS filesystem tree and block distribution across `hdp-worker1` and `hdp-worker2`.
  - Finished YARN applications list (`State: FINISHED, FinalStatus: SUCCEEDED`).
  - Hive SQL verification queries.
  - MongoDB collection document counts:
    - `res_stats`: 1 doc (Total Jobs: 22,979)
    - `res_top_cities`: 10 docs
    - `res_top_roles`: 10 docs
    - `res_skill_gap`: 10 docs
    - `res_vuln_table`: 100 docs
    - `res_courses`: 398 docs

---

## 3. Web UIs for Verification & Screenshots

During and after the execution, open the following URLs in your browser to verify and capture required academic screenshots:

| Component | Web UI URL | What to look for |
|---|---|---|
| **Hadoop NameNode** | [http://localhost:9870](http://localhost:9870) | Click **Datanodes** (2 Live DataNodes). Browse `/skills_mirage/raw/jobs/naukri_jobs.csv` to see block split. |
| **YARN ResourceManager** | [http://localhost:8088](http://localhost:8088) | Click **Nodes** (2 active). Check **Applications** to see all completed PySpark jobs with status `SUCCEEDED`. |
| **HiveServer2** | [http://localhost:10002](http://localhost:10002) | Hive query sessions and execution history. |

---

## 4. How to Start the Web Dashboard (Part C)

Once the cluster finishes populating MongoDB:

1. **Start the API & Dashboard**:
   Open Git Bash in `skills_mirage/`:
   ```bash
   scripts/start_app.sh
   ```
   *This starts the FastAPI backend on port 8000 and the React dashboard on port 5173.*

2. **Open the Web App**:
   Navigate to [http://localhost:5173](http://localhost:5173).
   - Sign up / log in.
   - The dashboard instantly renders:
     - **Total Jobs**: `22,979`
     - **Top City**: `Bengaluru/Bangalore`
     - **Interactive Charts**: Hiring Trends, Skill Gap Analysis, and AI Vulnerability Index.
     - **Worker Analysis & Reskilling**: Enter your profile to receive AI risk evaluation and tailored course pathways.
