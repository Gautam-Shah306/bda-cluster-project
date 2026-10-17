# Skills Mirage on Hadoop (Big Data Analytics project)

A reimplementation of the public [Mack-a-Hined / Skills Mirage](https://github.com/Asterrage2209/Mackahined) labour-market dashboard (licence check pending, see `docs/DECISIONS.md` D-005) with the heavy analytics moved onto a Hadoop cluster stack. No code or history was copied from the reference.

## Architecture
```
dataset/raw (CSV) --> HDFS raw --> Spark (processing) --> Parquet --> Spark (analytics) --> Parquet
                                         |                                  |
                                   Hive external tables              MongoDB res_* collections
                                                                            |
                                                  FastAPI (src/api)  <------+   React + Vite (src/frontend)
```
Details: `docs/ARCHITECTURE.md`. Decisions: `docs/DECISIONS.md`. Current state: `docs/STATUS.md`.

### Project Reports
- **Big Data Analytics & Technology Stack Report:** [`docs/BIG_DATA_ANALYTICS_REPORT.md`](docs/BIG_DATA_ANALYTICS_REPORT.md)
- **Social & Multimedia Analytics Report:** [`docs/SOCIAL_MULTIMEDIA_ANALYTICS_REPORT.md`](docs/SOCIAL_MULTIMEDIA_ANALYTICS_REPORT.md)

## Run locally (no cluster)
1. Python 3.11, Java 8/11/17 on PATH, Docker Desktop, Node 20+.
2. `py -3.11 -m venv .venv` then activate it, and `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and fill it in (generate `JWT_SECRET_KEY` with `python -c "import secrets; print(secrets.token_hex(32))"`).
4. Put the datasets in `dataset/raw/jobs/naukri_jobs.csv` and `dataset/raw/courses/courses.csv` (not in git; ask the team).
5. Start MongoDB: `docker compose --env-file .env -f config/cluster/docker-compose.yml up -d mongo`.
6. Run the pipeline: `python pipeline/run_pipeline.py` (`--dry-run` shows the plan).
7. API: `python -m uvicorn src.api.main:app --port 8000`. Frontend: `cd src/frontend && npm install && npm run dev` (port 5173).

## Run on the cluster (1 master + 2 workers)
STATUS: configuration written, not yet run (D-030). Start with the smoke test.
```
scripts/cluster_up.sh          # build and start HDFS, YARN, Hive, Mongo
scripts/cluster_smoke.sh       # node report, DataNodes, HDFS blocks, Spark-on-YARN job (saves evidence)
scripts/load_to_hdfs.sh        # copy dataset/raw into HDFS
scripts/run_pipeline_cluster.sh
scripts/create_hive_tables.sh
```
Web UIs: NameNode http://localhost:9870, ResourceManager http://localhost:8088.

## Ingestion (optional, outside the cluster)
`pip install -r requirements-ingestion.txt`, then `python -m src.ingestion.naukri_scraper` (needs Chrome) and `python -m src.ingestion.courses_scraper` (needs the `COURSES_*` variables). Output goes to `dataset/raw/scraped_*/dt=YYYY-MM-DD/`. How scraped rows join the processed data is proposed in D-034.

## Tests
- Frontend: `cd src/frontend && npm test && npm run lint && npm run build`
- Python helpers: `pytest src/ingestion pipeline`

## Contributions
Filled from the commit history and `docs/STATUS.md` at the end.
