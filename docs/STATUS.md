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

## Gautam

- **Working on now:** reuse / reimplement / change table for components C01-C27, and the keep/fix list for known reference bugs.
- **Last session (2026-10-02):** agreed the target (same system on Hadoop) and build order; logged D-009 and D-010; fixed the D-008 row; reviewed repo state.
- **Broken / blocked:** `dataset/` is git-ignored, so how teammates obtain the jobs and courses CSVs is undocumented. D-005 and D-006 still need team OK.
- **Next:** commit these doc updates (separate commits, own account); confirm collaborators; decide stack (#3) and cluster type (#5); fill `PROJECT_CONTEXT.md` and `ARCHITECTURE.md`.

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
