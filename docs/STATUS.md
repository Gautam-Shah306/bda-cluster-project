# STATUS

Single source for the current state. Read this first every session. Each member edits ONLY their own section (plus the project-wide table if they changed a component) to avoid merge conflicts.

## Project-wide state

| Area | State | Last updated | By |
|---|---|---|---|
| GitHub repo | CREATED 2026-10-01 (confirm all 3 collaborators added) | 2026-10-02 | Gautam |
| Reference analysis | DONE, awaiting team review: `docs/REFERENCE_ANALYSIS.md` | 2026-10-01 | Gautam |
| Topic / dataset | DECIDED: same as reference (D-009) | 2026-10-02 | Gautam |
| Architectural change | DECIDED: run on Hadoop (D-009); stack locked (D-011): PySpark, HDFS + Parquet, Hive, MongoDB serving, Docker Compose | 2026-10-02 | Gautam |
| Build order | Code first, early cluster smoke test (D-010) | 2026-10-02 | Gautam |
| Cluster (1 master + 2 workers) | NOT STARTED. Type decided: Docker Compose (D-011) | 2026-10-02 | Gautam |
Shared foundation (config, logging, Spark factory) | DONE, local mode verified | 2026-10-02 | Gautam |

## Gautam

- **Working on now:** next component (see below).
- **Last session (2026-10-02):** built the shared foundation: `config/pipeline.yaml`, `src/common/{config,logging_setup,spark_session}.py`, `requirements.txt`, `scripts/smoke_local.py`. Local smoke test passes (Python 3.11.9 venv, PySpark 3.5.9, Java 8).
- **Broken / blocked:** `winutils.exe` warning on Windows is harmless so far. Datasets are not yet in `dataset/raw/`.
- **Next:** place the jobs and courses CSVs in `dataset/raw/jobs/` and `dataset/raw/courses/`, then build the jobs-processing job.

## Member 2

- **Working on now:** (not started)
- **Last session:** -
- **Broken / blocked:** -
- **Next:** -

## Member 3

- **Working on now:** (not started)
- **Last session:** -
- **Broken / blocked:** -
- **Next:** -
