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
| Processing: jobs | DONE (local mode) | 2026-10-02 | Gautam |
| Processing: courses | DONE (local mode) | 2026-10-02 | Gautam |
| Analytics: dashboard stats and top-N | DONE (local mode) | 2026-10-02 | Gautam |
| Analytics: trends and skill gap | DONE (local mode) | 2026-10-02 | Gautam |
| Analytics: vulnerability index | DONE (local mode) | 2026-10-02 | Gautam |
| Analytics: reskilling lookup | DONE (local mode) | 2026-10-02 | Gautam |
| Serving layer: Mongo + loader | DONE (local mode) | 2026-10-02 | Gautam |
| Backend API: auth + dashboard routes | DONE (local mode) | 2026-10-02 | Gautam |
| Backend API: courses + latest-jobs | DONE (local mode) | 2026-10-02 | Gautam |
| Backend API: worker profile + Gemini risk | DONE (local mode) | 2026-10-02 | Gautam |
| Backend API: reskilling | DONE (local mode) | 2026-10-02 | Gautam |
| Backend API: chatbot | DONE (local mode) | 2026-10-02 | Gautam |
| Frontend: scaffold, auth, shell (F1) | DONE | 2026-10-09 | Heta |

## Gautam

- **Working on now:** next component (see below).
- **Last session (2026-10-02):** chatbot: intent routing, Spark SQL data questions (lazy session, two views over processed Parquet), validation + input-file check, masked Gemini errors, shutdown handler. Verified with stubs, Spark vs raw CSV, and real Gemini (English and Hindi). Logged D-025.
- **Broken / blocked:** `winutils.exe` warning on Windows is harmless so far. Datasets are not yet in `dataset/raw/`.
- **Next:** frontend, then ingestion (scrapers), pipeline orchestration, cluster config files.

## Heta

- **Working on now:** (not started)
- **Last session (2026-10-09):** frontend F1: Vite + React + TypeScript + Tailwind scaffold in `src/frontend/` (auth context with synchronous session restore, shared API client with 401 handling, Login, Register, Landing, dashboard shell with 7 placeholder pages, 404 page), 28 Vitest tests, lint/tsc/build clean, CORS and live sign-up/sign-in/refresh checked in a browser. Logged D-026, D-027, D-028.
- **Broken / blocked:** none. (The older note about datasets not being in `dataset/raw/` is obsolete.)
- **Next:** D-026 backend step (Spark warm-up, city hint), then the D-010 cluster smoke test, then F2 (dashboard pages) and F3 (worker pages and chatbot).

## Member 3

- **Working on now:** (not started)
- **Last session:** -
- **Broken / blocked:** -
- **Next:** -
