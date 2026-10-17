# STATUS

Single source for the current state. Read this first every session. Each member edits ONLY their own section (plus the project-wide table if they changed a component) to avoid merge conflicts.

## Project-wide state

| Area | State | Last updated | By |
|---|---|---|---|
| GitHub repo | CREATED 2026-10-01 (confirm all 3 collaborators added) | 2026-10-02 | Gautam |
| Reference analysis | DONE, awaiting team review: `docs/REFERENCE_ANALYSIS.md` | 2026-10-01 | Gautam |
| Topic / dataset | DECIDED: same as reference (D-009) | 2026-10-02 | Gautam |
| Architectural change | DECIDED: run on Hadoop (D-009); stack locked (D-011): PySpark, HDFS + Parquet, Hive, MongoDB serving, Docker Compose | 2026-10-02 | Gautam |
| Build order | Code first; cluster smoke test deferred to the cluster phase (D-030) | 2026-10-10 | Gautam |
| Shared foundation (config, logging, Spark factory) | DONE, local mode verified | 2026-10-02 | Gautam |
| Processing: jobs and courses | DONE (local mode) | 2026-10-02 | Gautam |
| Analytics (stats, trends, vulnerability, reskilling lookup, serving extras) | DONE (local mode) | 2026-10-02 | Gautam |
| Serving layer: Mongo + loader | DONE (local mode) | 2026-10-02 | Gautam |
| Backend API (auth, dashboard, courses, worker, reskilling, chatbot) | DONE (local mode) | 2026-10-02 | Gautam |
| Chatbot warm-up and city hint (D-029) | DONE | 2026-10-10 | Heta |
| Frontend: scaffold, auth, shell (F1) | DONE | 2026-10-09 | Heta |
| Frontend: dashboard pages (F2) | DONE | 2026-10-10 | Heta |
| Frontend: worker pages and chatbot (F3, D-033) | DRAFTED 2026-10-14 (tsc, eslint and 47 new tests pass in a scratch project); run `npm install`, `npm test`, `npm run build` in the repo and check in a browser before committing | 2026-10-14 | (to be committed by the member who applies it) |
| Ingestion: Naukri + course scrapers, course enrichment | DRAFTED, parsers unit-tested (10 tests); scrapers not run against live sites; design PROPOSED in D-034 | 2026-10-14 | (same) |
| Pipeline orchestration (`pipeline/run_pipeline.py`) | DRAFTED, step selection tested, not run against Spark here | 2026-10-14 | (same) |
| Cluster config (Compose, Hadoop, Spark, Hive, scripts) | DRAFTED, syntax checked only; NOT RUN (needs the D-010 smoke test first) | 2026-10-14 | (same) |
| Cluster (1 master + 2 workers) | NOT RUN | 2026-10-14 | - |
| README, PROJECT_CONTEXT | WRITTEN 2026-10-14 (Contributions section still to fill at the end) | 2026-10-14 | - |

## Gautam

- **Working on now:** (see project-wide table)
- **Last session (2026-10-02):** backend, analytics and chatbot (D-014 to D-025).
- **Broken / blocked:** none known. `winutils.exe` warning on Windows is harmless.
- **Next:** review and commit the 2026-10-14 drafts, then run the cluster smoke test.

## Heta

- **Working on now:** review the F3 draft (worker pages and chatbot) in a browser.
- **Last session (2026-10-10):** frontend F2 (D-031, D-032) and chatbot warm-up (D-029).
- **Broken / blocked:** none.
- **Next:** commit F3, then help with the cluster phase.

## Member 3

- **Working on now:** (not started). Suggested: take ingestion (src/ingestion, D-034) and the cluster config files, which do not touch the frontend (D-002: write the choice here before starting).
- **Last session:** -
- **Broken / blocked:** -
- **Next:** -
