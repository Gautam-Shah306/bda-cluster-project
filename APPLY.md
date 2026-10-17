# How to apply this overlay

The zip mirrors the repo layout. Unzip it over the repo root (it adds and replaces files only; it deletes nothing).

1. `git pull`, then unzip over the repo root.
2. Frontend: `cd src/frontend && npm install` (this adds react-markdown to package-lock.json; commit the lock), then `npm test`, `npm run lint`, `npm run build`.
3. Backend cleanups: `python scripts/apply_cleanups.py` (idempotent), then `python pipeline/run_pipeline.py --dry-run`.
4. Docs: append the rows of `docs/DECISIONS_NEW_ROWS.md` to `docs/DECISIONS.md` (and edit the D-012 and D-026 status cells as D-037 says), delete the rows file.
5. Ingestion tests: `pip install -r requirements-ingestion.txt pytest` then `pytest src/ingestion pipeline`.
6. Cluster: see README. Run `scripts/cluster_up.sh` then `scripts/cluster_smoke.sh` before anything else.
7. Commit in small commits from your own account, docs separate from code, for example:
   feat(frontend): add worker analysis, reskilling and chatbot pages
   feat(ingestion): add naukri and course scrapers with parsers
   feat(pipeline): add pipeline runner
   config(cluster): add hadoop, spark, hive config and compose services
   docs(decisions): add D-034 to D-037
Check `git status` first and confirm `.env` is not listed.
