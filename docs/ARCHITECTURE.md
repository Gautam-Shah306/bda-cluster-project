# ARCHITECTURE

Facts per D-009 to D-012. Anything marked OPEN is undecided. Versions are in use but image tags are unverified until the cluster smoke test.

## Cluster (Docker Compose, 1 master + 2 workers)
Compose file: `config/cluster/docker-compose.yml`

| Node (hostname) | Role | Services | Ports |
|---|---|---|---|
| `hdp-master` | master | HDFS NameNode, YARN ResourceManager | NN RPC 9000, NN UI 9870, RM UI 8088, RM 8032 |
| `hdp-worker1` | worker 1 | HDFS DataNode, YARN NodeManager | DN UI 9864, NM UI 8042 |
| `hdp-worker2` | worker 2 | HDFS DataNode, YARN NodeManager | DN UI 9864, NM UI 8042 |

Auxiliary service containers (not counted as cluster nodes):

| Container | Purpose | Ports |
|---|---|---|
| `hive-postgres` | PostgreSQL 15, Hive metastore DB | 5432 |
| `hive-metastore` | Hive 3.1.3 metastore (Java 8) | 9083 |
| `hive-server2` | Hive 3.1.3 HiveServer2 (Java 8) | 10000, UI 10002 |
| `mongo` | MongoDB 7.0: users + precomputed results (hosting OPEN: container vs Atlas) | Configurable host port (27018 on the first machine) |

Application processes (outside the cluster): FastAPI on 8000, React/Vite on 5173.

## Versions (D-012)
Hadoop 3.3.6; Spark/PySpark 3.5.x (Hadoop 3 build); Hive 3.1.3; PostgreSQL 15; MongoDB 7.0; Java 11 (Hadoop, Spark), Java 8 (Hive); Python 3.11; Node 20 LTS; Docker Compose v2.
HDFS: `dfs.blocksize` = 8 MB, `dfs.replication` = 2.
Spark-Hive: `spark.sql.hive.metastore.version=3.1`, `spark.sql.hive.metastore.jars` pointed at the Hive 3.1.3 jars.

## Config locations
| Path | Contents |
|---|---|
| `config/cluster/docker-compose.yml` | all cluster and service containers |
| `config/hadoop/` | `core-site.xml`, `hdfs-site.xml`, `yarn-site.xml`, `mapred-site.xml` |
| `config/spark/` | `spark-defaults.conf` |
| `config/hive/` | `hive-site.xml` |
| `config/pipeline.yaml` | run mode (`local` or `cluster`) and all data paths |
Secrets (Mongo URI, Gemini keys, JWT secret) come from `.env` (git-ignored), never from committed config.

## Data layout
Root is set by `config/pipeline.yaml`: `local` = `file://<repo>/dataset/...`, `cluster` = `hdfs://hdp-master:9000/...`

| Path under root | Content | Format |
|---|---|---|
| `raw/jobs/` | historical jobs CSV (22,979 rows, 14 columns) | CSV |
| `raw/courses/` | courses CSV (398 rows, 9 columns) | CSV |
| `raw/scraped_jobs/dt=YYYY-MM-DD/` | one file per scrape run | JSON/CSV |
| `raw/scraped_courses/dt=YYYY-MM-DD/` | one file per course scrape run | JSON/CSV |
| `processed/jobs/` | cleaned jobs, parsed skills, city, AI mentions | Parquet |
| `processed/courses/` | courses with normalised tags | Parquet |
| `analytics/<result_set>/` | precomputed results before loading into Mongo | Parquet |

Hive: database `skills_mirage`, external tables over `raw/*` and `processed/*`.

## Pipeline
ingestion -> processing -> analytics -> serving

1. **Ingestion** (`src/ingestion/`): Selenium and requests scrapers run as a standalone step and write to `raw/scraped_*`. Loaders put the historical CSVs into `raw/`.
2. **Processing** (`src/processing/`): PySpark jobs clean and normalise jobs, extract skills, and enrich course tags, writing to `processed/`.
3. **Analytics** (`src/analytics/`): PySpark jobs compute the reference's results with the same formulas: stats, top cities/roles/industries, roles-by-city, cities-by-role, hiring trends, skill trends and years, skill gap, vulnerability index, and reskilling matching inputs.
4. **Serving**: the analytics jobs write results to MongoDB (separate collections from users; names OPEN). FastAPI reads them and returns the response shapes in `REFERENCE_ANALYSIS.md` D.4.
5. **Chatbot data queries**: NL-to-SQL runs against Hive/Spark SQL over `processed/*` (replaces SQLite).

Orchestration lives in `pipeline/`, run scripts in `scripts/`.

## File map
| Folder | What it does |
|---|---|
| `dataset/` | local copies of the CSVs (git-ignored); see README for how to obtain them |
| `src/ingestion/` | scrapers and HDFS/local loaders |
| `src/processing/` | PySpark cleaning, skill extraction, course enrichment |
| `src/analytics/` | PySpark analytics jobs |
| `src/api/` | FastAPI backend (auth, dashboard, worker, chatbot, courses routes) |
| `src/frontend/` | React + Vite frontend |
| `scripts/` | cluster up/down, smoke test, run scripts |
| `config/` | cluster, Hadoop, Spark, Hive and pipeline config |
| `output/` | results (git-ignored) |
| `screenshots/` | demo evidence |
| `pipeline/` | end-to-end orchestration |

## OPEN
MongoDB hosting (container vs Atlas); Mongo collection names