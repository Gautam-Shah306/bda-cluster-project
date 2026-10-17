# PROJECT_CONTEXT

- **Course:** Big Data Analytics, group project, 3 students.
- **What we build:** Skills Mirage, a dashboard for the Indian labour market, reimplemented from the public reference repo https://github.com/Asterrage2209/Mackahined (read-only; licence check pending, D-005). Same product and API shapes; different internals.
- **Dataset:** the reference's Naukri jobs CSV (22,979 rows, 14 columns, mostly 2015-2017 plus about 1,000 rows scraped in 2026) and courses CSV (398 NPTEL/SWAYAM courses). Provenance and licence of the jobs data are unresolved.
- **Goal:** show distributed storage and processing on a cluster of 1 master + 2 workers (HDFS, Spark on YARN, Hive), with results precomputed into MongoDB and served by FastAPI to a React dashboard.
- **Two layers:** Core Intelligence (market analytics, AI Vulnerability Index) and Worker Action (Gemini risk analysis, reskilling plan, English/Hindi chatbot).
- **How our design differs from the reference:** the reference recomputes every analytic per request inside one Python process over a 52 MB CSV in RAM. We run PySpark batch jobs (local mode now, YARN on the cluster), store raw data in HDFS and processed data as Parquet, expose it through Hive external tables, load precomputed results into `res_*` MongoDB collections, and make the API read only those. Bugs in the reference are kept or fixed one by one (see DECISIONS.md, D-014 to D-033).
- **Timeline / demo date:** OPEN (nobody has set one yet).
