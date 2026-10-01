# REFERENCE ANALYSIS

> Analysis of the public reference repo `Asterrage2209/Mackahined` (read-only). Produced by direct reading of every tracked source, config, script and data file, with real file line numbers. Evidence tags: `[FACT file:line]` seen in a file, `[INFERRED]` reasoning from what was seen, `[NOT DETERMINABLE]` needs running the code or missing information. The `frontend/.npm-cache/` folder (599 tracked npm cache files) is listed but not analysed. Analysis only: no reuse/change classification and no design proposals are made here.

## 0. Header
- Reference: https://github.com/Asterrage2209/Mackahined (public), branch `main`, HEAD `d29294999a35f93c7d30ecf0d138b17b9c1dc158`.
- Licence: none found (no LICENSE file in the tracked files) [FACT git ls-files].
- History: 40 commits, 2026-03-06 to 2026-03-07 (a one-day hackathon burst); author identities in git: Advait Pandya (25 commits under two names/emails), Harsh Shah (5), ketavshah30 (4), Jemil / Jemil Patel (4), Shivam Jhaveri (1). README lists 5 teammates: Advait Pandya, Harsh Shah, Jemil Patel, Shivam Jhaveri, Ketav Shah [FACT README.md:100-105; git shortlog].
- Name: "Mack-a-Hined" / "Skills Mirage" (Hack A Mined hackathon project).
- Analysis performed by direct file reading with line numbers; analysis date 2026-10-01.

## 1. What the application is
Skills Mirage is a web dashboard for the Indian labour market with two layers [FACT layer names in DashboardLayout.tsx:17,24 and docstrings in courses_routes.py]:
- Layer 1, "Core Intelligence": overall job-market analytics from a jobs dataset (Naukri.com data): totals and top city/skill/role, hiring-trend by month, rising/declining skills, a skill-gap map comparing job-skill demand with course supply, an "AI Vulnerability Index" (a risk score per role and city), top cities and roles with drill-down charts, and a latest-jobs table with a refresh button that scrapes Naukri live.
- Layer 2, "Worker Action": a logged-in worker enters job title, city, years of experience, role description and skills; Gemini returns an AI-automation risk score, risk level, pivot roles and new skills; a second Gemini call builds a reskilling/upskilling plan (skills, matching NPTEL/SWAYAM courses, matching job openings, weekly timeline); and a chatbot answers questions in English or Hindi (data questions via natural-language-to-SQL, risk and improvement questions via the stored analysis).
Target users: workers (BPO and similar roles), career counsellors/hackathon judges [INFERRED from copy such as "BPO profiles are prioritised" in worker_gemini.py:19].

## 2. System overview

Components: React SPA (Vite, port 5173) -> FastAPI app (uvicorn, port 8000) -> MongoDB Atlas (users only) + local CSV/SQLite/JSON files + Google Gemini API + external scraping targets (naukri.com via Selenium Chrome; Google Sheets and nptel pages via requests) + APScheduler (in-process).

```text
 Browser (React SPA, localStorage JWT)
        |  HTTPS/JSON, Bearer token
        v
 FastAPI (single process, uvicorn)
   |-- /auth/*  --------------------> MongoDB Atlas  (users)
   |-- /worker/*, /chatbot/query ---> MongoDB (user doc) + Gemini API (gemini-2.5-flash)
   |-- /dashboard/*  -- reads -----> in-memory pandas frames <- dataset/naukri_jobs.csv (52 MB)
   |-- /courses/*  ----------------> in-memory frame <- dataset/courses.csv
   |-- chatbot data intent --------> SQLite backend/db/chat_data.db (courses, jobs) + Gemini (NL->SQL)
   |-- /dashboard/scraped-jobs ----> Selenium Chrome -> naukri.com -> append -> rewrite CSV
   '-- APScheduler: weekly courses scrape (Google Sheet + nptel preview pages) -> dataset/courses.csv
```

```text
Data flow (jobs):   naukri.com -> Selenium -> BeautifulSoup cards -> clean_jobs -> extract_skills
                    -> append_jobs (dedupe, in-memory) -> rewrite dataset/naukri_jobs.csv
                    -> get_all_jobs() (per request) -> Counter/keyword scoring -> JSON -> Recharts
Data flow (courses): Google Sheet CSV + nptel.ac.in preview -> normalise -> append_courses -> dataset/courses.csv
                    (+ offline enrichment dataset/update_course_skills.py)
Data flow (worker): form -> POST /worker/profile -> Gemini risk JSON -> Mongo users
                    -> POST /worker/reskilling -> trends + matched courses/jobs + Gemini plan -> Mongo
```

## 3. Folder tree (tracked files only, 112 files excluding `frontend/.npm-cache`; 711 in total)
```text
/                              repo root
  README.md                    project overview and setup steps
  context.md                   empty file
  package-lock.json            empty lockfile for a root package (no package.json)
  .gitignore                   ignores venv, __pycache__, .env, node_modules, dist
  backend/
    main.py                    FastAPI app, CORS, scheduler, routers (89 lines)
    requirements.txt           18 Python packages (2 pinned)
    config.py                  empty
    api/                       5 routers: auth, chatbot, courses, dashboard, worker
    chatbot/                   gemini_client, prompt_builder (unused), query_router (intents, NL->SQL)
    data/                      dataset_manager.py (jobs store), courses_dataset.py (courses store),
                               raw_jobs.json (40-job scrape snapshot)
    db/                        mongo.py (client), init_db.py (CSV->SQLite), chat_data.db (SQLite),
                               database.py and models.py (empty)
    intelligence/              hiring_trends, skill_trends, vulnerability_index
    pipeline/                  job_cleaner, skill_extractor, dummy_scraper, ai_signal_detector (empty)
    pipelines/                 job_pipeline.py (runs the scraper)
    scrapers/naukri/           naukri_scraper (Selenium orchestrator), naukri_parser, naukri_urls
    scrapers/courses/          courses_scraper, swayam_scraper, nptel_scraper
    scrapers/utils/            selenium_client, http_client (unused), skill_extractor (AI keywords)
    utils/                     jwt_handler.py; city_mapper, role_normalizer, skill_taxonomy (empty)
    worker_engine/             worker_parser, risk_score (unused), worker_gemini, reskilling_engine
    test_*.py (4)              manual scripts, no assertions; out.txt, test_out.txt are UTF-16 logs
  frontend/
    package.json, vite/ts/tailwind/eslint configs, index.html, .env.example
    src/main.tsx, App.tsx      entry and routes
    src/context/AuthContext.tsx   auth state in localStorage
    src/services/api.ts, jobAnalytics.ts   API client and adapters
    src/layout/DashboardLayout.tsx   sidebar + top bar
    src/pages/                 LandingPage, auth/{Login,Register}, dashboard/{Overview,HiringTrends,
                               SkillsIntelligence,AIVulnerability,WorkerIntelligence,ReskillingPath,
                               Chatbot,LatestJobs,DynamicInsights}
    src/utils/jobDataLoader.ts unused browser CSV loader
    src/data/naukri_jobs.csv   52 MB duplicate dataset (unused)
    .npm-cache/                599 committed npm cache files (about 88 MB)
    build/dev logs, eslint_report.json   committed UTF-16 logs (stale)
  data/                        courses_raw.json (398 courses); courses.json, jobs_raw.json,
                               jobs_processed.json are empty (0 bytes)
  dataset/                     naukri_jobs.csv (22,979 rows), naukri_com-job_sample.csv (22,000),
                               naukri_jobs_scraped.csv (775), courses.csv (398), update_course_skills.py
```

## 4. Tech stack and versions
| Layer | Item | Version | Declared in | Pinned? |
|---|---|---|---|---|
| Backend lang | Python | not stated | n/a | [NOT DETERMINABLE] (code uses `X | None` type hints, so 3.10+ [INFERRED reskilling_engine.py:144]) |
| Backend | fastapi, uvicorn, pydantic, python-dotenv, google-genai, requests, selenium, beautifulsoup4, lxml, numpy, pandas, scikit-learn, pymongo[srv], passlib[bcrypt], python-jose, email-validator | latest at install | backend/requirements.txt | floating |
| Backend | apscheduler | 3.10.4 | requirements.txt:13 | pinned |
| Backend | bcrypt | 4.0.1 | requirements.txt:16 | pinned |
| AI model | Gemini `gemini-2.5-flash` (three call sites) | n/a | worker_gemini.py:62, reskilling_engine.py:220, gemini_client.py:15 | hard-coded string |
| DB | MongoDB (Atlas, per log text) | n/a | mongo.py:16 | n/a |
| DB | SQLite | stdlib | init_db.py, query_router.py | n/a |
| Browser automation | Google Chrome + a matching WebDriver (Selenium Manager) | n/a | selenium_client.py:73 | not declared |
| Frontend lang | Node.js | not stated | n/a | [NOT DETERMINABLE] |
| Frontend | React 18.3.1 range, react-router-dom 7.13.1 range, Vite 5.4.x range (log shows vite 5.4.21), TypeScript ~5.6.2, Tailwind 3.4.19 range, Recharts 3.7.0 range, lucide-react 0.577.0 range, papaparse 5.5.3 | caret ranges | frontend/package.json | floating (caret) |
`scikit-learn`, `numpy` are installed but never imported by any backend file [INFERRED from grep]; `selenium` and `lxml` are used.

## 5. Backend, module by module

Reference: `Asterrage2209/Mackahined` @ `d29294999a35f93c7d30ecf0d138b17b9c1dc158`. All paths are relative to the repo root. Line numbers are real file line numbers. Tags: [FACT file:line], [INFERRED], [NOT DETERMINABLE].

Part A covers: `backend/main.py`, `config.py`, `requirements.txt`, `db/*`, `utils/*`, `api/*`, `pipeline/*`, `pipelines/*`.

### A.1 Application entry: `backend/main.py` (89 lines)

- Logging: `logging.basicConfig(level=INFO, format="%(asctime)s | %(levelname)s | %(message)s")` runs before other imports [FACT main.py:4-7].
- Imports: routers `dashboard_routes`, `worker_routes`, `chatbot_routes` from `api` [13]; `courses_routes.router` as `courses_router` [14]; `is_empty` (aliased `courses_dataset_is_empty`, never used) and `get_course_count` from `data.courses_dataset` [15]; `run_courses_scraper`, `run_courses_scraper_background` from `scrapers.courses.courses_scraper` [16-19]; `auth_routes` imported late at line 77 [77].
- `MIN_COURSES = 200` [23]. Module-level `scheduler = BackgroundScheduler()` (APScheduler, default settings) [26].
- `lifespan(app)` async context manager [29-56]:
  1. `course_count = get_course_count()` [32]. If `< MIN_COURSES`, log and call `run_courses_scraper_background()` [33-38].
  2. Add job `run_courses_scraper` with `trigger="interval", days=7, kwargs={"max_per_source": 50}, id="weekly_courses_scrape", replace_existing=True` [41-48].
  3. `scheduler.start()` [49]. `yield` [52]. On shutdown `scheduler.shutdown(wait=False)` [55].
- App: `FastAPI(title="Skills Mirage API", lifespan=lifespan)` [60].
- CORS: origins `http://localhost:5173` and `http://localhost:3000`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]` [62-68].
- HTTP middleware `log_requests`: logs `API Request: {method} {url}` then calls `call_next` [70-74].
- Routers included in this order, with their own prefixes (none added in main): dashboard, worker, chatbot, courses, auth [79-83].
- Route `GET /` returns `{"message": "Skills Mirage Backend Running"}` [86-88].
- Env vars read in this file: none.
- Note: the jobs data is NOT loaded at startup here; no job scraper is scheduled (only courses).

### A.2 `backend/requirements.txt` (18 lines, last line has no trailing newline)

Exact list [FACT requirements.txt:1-18]: `fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `google-genai`, `requests`, `selenium`, `beautifulsoup4`, `lxml`, `numpy`, `pandas`, `scikit-learn`, `apscheduler==3.10.4`, `pymongo[srv]`, `passlib[bcrypt]`, `bcrypt==4.0.1`, `python-jose`, `email-validator`. Only `apscheduler` and `bcrypt` are pinned; everything else is floating. No Python version is declared here.

### A.3 Empty files (0 bytes, verified)

`backend/config.py`, `backend/db/database.py`, `backend/db/models.py`, `backend/utils/city_mapper.py`, `backend/utils/role_normalizer.py`, `backend/utils/skill_taxonomy.py`, `backend/pipeline/ai_signal_detector.py`. Nothing imports them to useful effect [INFERRED].

### A.4 Database layer

#### `backend/db/mongo.py` (19 lines)
- `load_dotenv()` [6]. `MONGO_URI = os.getenv("MONGO_URI")` (no default) [9]; `DATABASE_NAME = os.getenv("DATABASE_NAME", "skills_mirage_db")` [10].
- `MongoClient(MONGO_URI)`; `users_collection = db["users"]` [13-15]. Logs "Connected to MongoDB Atlas" [16] (the client is lazy, so this log does not prove connectivity [INFERRED]). On exception, `users_collection = None` [17-19]; later code does not check for None, so every auth call would then raise AttributeError [INFERRED].

#### `backend/db/init_db.py` (49 lines): offline SQLite loader
- Paths: `BACKEND_DIR = backend/`, `PROJECT_DIR = repo root`, `DATASET_DIR = repo/dataset`, `DB_PATH = backend/db/chat_data.db` [8-12]. `DATA_DIR` (repo/data) is defined but unused.
- `init_db()`: creates the db folder, opens SQLite [14-17]. For `dataset/courses.csv`: `pd.read_csv`, normalise column names with `strip().lower().replace(" ","_").replace("-","_")`, `to_sql('courses', if_exists='replace', index=False)` [20-26]. Same for `dataset/naukri_jobs.csv` into table `jobs` [33-39]. Missing file: prints "File not found" [30, 43]. Errors are caught and printed [27-28, 40-41]. Run as a script via `__main__` [48-49].
- Committed DB (verified read-only): table `courses` (398 rows: NPTEL 200, SWAYAM 198; columns name, source, domain, url, institution, duration_weeks REAL, difficulty, skill_tags, syllabus_weeks), table `jobs` (775 rows; columns company, education REAL, experience, industry REAL, jobdescription, jobid REAL, joblocation_address, jobtitle, numberofpositions REAL, payrate REAL, postdate, site_name REAL, skills, uniq_id REAL; `postdate` range 2026-03-06 03:54:19 to 13:38:00).
- DISCREPANCY: `init_db` reads the ~52 MB `dataset/naukri_jobs.csv`, but the committed DB holds only 775 jobs, all from one morning, so the DB was not produced from that file as it exists in the repo. [INFERRED] It looks built from scraped data (`dataset/naukri_jobs_scraped.csv`, see Part E). The only runtime users of this DB are in `chatbot/query_router.py` (Part B).

### A.5 Auth: `backend/utils/jwt_handler.py` (58 lines)

- Env vars: `JWT_SECRET_KEY` default `"supersecretsaxkey"` [18]; `JWT_ALGORITHM` default `"HS256"` [19]; `ACCESS_TOKEN_EXPIRE_HOURS` default `"24"` cast to int [20].
- `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")` [9]; `hash_password`, `verify_password` [11-15].
- `create_access_token(data)`: copies data, adds `exp = utcnow + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)`, encodes with `jose.jwt` [22-27]. Payload keys at login: `user_id` (str of `_id`), `email`, `exp`.
- `verify_token(token)`: decode, returns payload or `None` on `JWTError` [29-34].
- `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")` [37].
- `get_current_user(token)`: any failure raises HTTP 401, detail `"Could not validate credentials"`, header `WWW-Authenticate: Bearer` [40-56]. Failure cases: invalid/expired token, no `email` claim, no matching user [46-56]. Success returns the full Mongo user document (including `_id` and the password hash) [54-58]. No caching of any kind: it does one `find_one({"email": email})` per request [54].
- Consequence: every endpoint using `Depends(get_current_user)` requires a valid token, even where typed `Optional`.

### A.6 API routers

Router prefixes and tags [FACT]: auth `/auth` tag "Authentication" (auth_routes.py:17); chatbot `/chatbot` tag "Chatbot" (chatbot_routes.py:8); dashboard `/dashboard` tag "Dashboard" (dashboard_routes.py:15); worker `/worker` tag "Worker" (worker_routes.py:14); courses router has NO prefix; full paths are written in decorators (courses_routes.py:29).

#### Complete endpoint table (27 routes + `GET /`)

| # | Method | Full path | Auth | Handler (file) | Data source |
|---|---|---|---|---|---|
| 1 | GET | `/` | none | root (main.py:86) | static |
| 2 | POST | `/auth/signup` | none | signup (auth_routes.py:28) | Mongo `users` |
| 3 | POST | `/auth/login` | none | login (:62) | Mongo `users` |
| 4 | GET | `/auth/me` | JWT | get_me (:103) | Mongo `users` |
| 5 | POST | `/chatbot/query` | JWT (required in effect) | chatbot (chatbot_routes.py:16) | Mongo + `handle_query` |
| 6 | GET | `/courses` | none | list_courses (courses_routes.py:32) | `data.courses_dataset` |
| 7 | GET | `/courses/stats` | none | courses_stats (:58) | same |
| 8 | GET | `/courses/for-skills` | none | courses_for_skills (:67) | same |
| 9 | GET | `/courses/reskilling` | none | courses_for_reskilling (:87) | same |
| 10 | POST | `/scrape/courses` | none | trigger_courses_scrape (:115) | background scraper |
| 11 | GET | `/dashboard/skill-gap` | none | skill_gap (dashboard_routes.py:17) | `compute_skill_gap` |
| 12 | GET | `/dashboard/stats` | none | stats (:21) | `get_all_jobs` |
| 13 | GET | `/dashboard/hiring-trends` | none | hiring_trends (:47) | `compute_hiring_trends` |
| 14 | GET | `/dashboard/skill-trends` | none | skill_trends (:51) | `compute_skill_trends` |
| 15 | GET | `/dashboard/skill-trend-years` | none | skill_trend_years (:55) | `get_available_job_years` |
| 16 | GET | `/dashboard/vulnerability` | none | vulnerability (:59) | jobs + vulnerability index |
| 17 | GET | `/dashboard/vulnerability-regions` | none | vulnerability_regions (:109) | `compute_vulnerability_index` |
| 18 | GET | `/dashboard/latest-jobs` | none | latest_jobs (:113) | `get_latest_jobs(50)` |
| 19 | GET | `/dashboard/scraped-jobs` | none | scraped_jobs (:117) | scraper + jobs |
| 20 | GET | `/dashboard/top-cities` | none | top_cities (:134) | jobs |
| 21 | GET | `/dashboard/industry-distribution` | none | industry_distribution (:140) | jobs |
| 22 | GET | `/dashboard/top-roles` | none | top_roles (:147) | jobs |
| 23 | GET | `/dashboard/city-role-distribution` | none | city_role_distribution (:153) | jobs |
| 24 | GET | `/dashboard/role-city-distribution` | none | role_city_distribution (:167) | jobs |
| 25 | GET | `/worker/profile` | JWT | get_worker_profile (worker_routes.py:24) | user doc |
| 26 | POST | `/worker/profile` | JWT | update_worker_profile (:38) | Gemini + Mongo |
| 27 | GET | `/worker/reskilling` | JWT | get_reskilling (:110) | user doc |
| 28 | POST | `/worker/reskilling` | JWT | create_reskilling (:127) | Gemini + Mongo |

(28 rows including `GET /`; 27 API routes excluding it. `GET /dashboard/*` are all unauthenticated.)

#### `backend/api/auth_routes.py` (113 lines)
- Models: `SignupRequest{email: EmailStr, name: str, password: str}` [19-22]; `LoginRequest{email: EmailStr, password: str}` [24-26].
- `POST /auth/signup` (status 201) [28-59]: email lowercased and stripped [31]; if a user exists, HTTP 400 `"Email already registered"` [35-39]; hash password [42]; insert exactly this document [45-58]: `email`, `name`, `password` (bcrypt hash), `job_role: None`, `city: None`, `years_of_experience: None`, `role_description: None`, `skills: []`, `risk_score: None`, `created_at: utcnow()`. Returns `{"message": "User registered successfully"}`. No password policy or length check.
- `POST /auth/login` [62-100]: lowercases/strips email; logs `Login attempt: <email>`; unknown user or wrong password both return 401 `"Invalid credentials"` [74-87]; success returns `{"access_token": <jwt>, "token_type": "bearer"}` [97-100].
- `GET /auth/me` [103-113]: returns `name, email, job_role, city, years_of_experience, role_description, risk_score` from the user doc via `.get`.

#### `backend/api/chatbot_routes.py` (37 lines)
- `ChatbotQuery{worker_profile: dict = {}, question: str}` [11-13].
- `POST /chatbot/query` [16-37]: although typed `Optional[dict]`, `Depends(get_current_user)` raises 401 for anonymous callers, so auth is effectively required. Looks up the fresh user doc by email, pops `_id`, passes `handle_query(query.model_dump(), user_data=<doc>)` [26-33]. Any exception becomes HTTP 502 `"Chatbot failed: <exc>"` [34-35]. Returns `{"response": <whatever handle_query returns>}`. Note: `user_data` includes the password hash, which is then available to chatbot code [INFERRED from 30-31, no field removal except `_id`].

#### `backend/api/courses_routes.py` (130 lines)
- `GET /courses` [32-55]: query `source` (optional), `domain` (optional), `limit` (default 100, `le=500`), `offset` (default 0, `ge=0`). If `source` -> `get_courses_by_source(source)` else `get_all_courses()`. If `domain`: case-insensitive substring match on `c.get("domain","")`. Response `{total, offset, limit, courses: slice[offset:offset+limit]}`.
- `GET /courses/stats` [58-64]: returns `get_stats()` unchanged.
- `GET /courses/for-skills` [67-84]: required `skills` (comma-separated), `max_results` default 20, `le=50`. Splits and strips; empty list returns `{"courses": [], "skills_queried": []}`; else `{"courses": query_courses_for_skills(list, max_results=...), "skills_queried": list}`.
- `GET /courses/reskilling` [87-112]: required `target_role`; optional `current_skills` (comma string), `max_weeks` (int), `max_results` default 10, `le=30`. Returns `{"target_role", "max_weeks", "courses": query_courses_for_reskilling(target_role=, current_skills=list, max_weeks=, max_results=)}`.
- `POST /scrape/courses` [115-131]: query bools `swayam=True`, `nptel=True`; schedules `run_courses_scraper(swayam=, nptel=)` as a FastAPI background task; returns `{"status": "started", "message": "Course scrape running in background. Check /courses/stats for progress.", "sources": {"swayam", "nptel"}}`.

#### `backend/api/dashboard_routes.py` (179 lines)
All handlers assume `get_all_jobs()` returns a list of dicts with keys `city`, `title`, `skills` (list), `company` (Part B documents the loader).
- `GET /dashboard/skill-gap` [17-19] and `GET /dashboard/hiring-trends` [47-49]: return the result of `compute_skill_gap()` / `compute_hiring_trends()` unchanged.
- `GET /dashboard/stats` [21-45]: loops all jobs counting `city` (default ""), each skill, and `title` (default ""). Returns `{"total_jobs": N, "top_city": most common city or "N/A", "most_in_demand_skill": ..., "most_common_role": ...}`. Empty-string city/title are counted too and could win [INFERRED from 31, 34].
- `GET /dashboard/skill-trends?year=<int, optional>` [51-53]: `compute_skill_trends(year=year)`. `GET /dashboard/skill-trend-years` [55-57]: `{"years": get_available_job_years()}`.
- `GET /dashboard/vulnerability` [59-107]: `vuln_data = compute_vulnerability_index()`; `role_risks = vuln_data.get("role_risks", {})` [62-63]. For each job: `role = str(title).strip().lower()`, `city = str(city or "Unknown").strip()` (default "Unknown" only if key missing), skip empty role; dedupe on `(role, city)`; row `{"job_role": role.title(), "city": city.title(), "ai_risk_score": round(role_risks.get(role, 0))}` [65-79]. Sort by `ai_risk_score` descending, keep top 100 [84-86]. `regions` = mean of `ai_risk_score` per city over those 100 rows only (not over all jobs) [89-100]. Response `{"table": [...], "regions": {city: float}}`. Unknown roles score 0.
- `GET /dashboard/vulnerability-regions` [109-111]: returns the whole `compute_vulnerability_index()` dict (keys include at least `role_risks`, see Part B).
- `GET /dashboard/latest-jobs` [113-115]: `get_latest_jobs(50)`.
- `GET /dashboard/scraped-jobs?refresh=<bool, default True>` [117-132]: if `refresh` (default true), run `run_scraper()` synchronously in the request, catching any exception into `scrape_error` string. Returns `{"total": len(get_all_jobs()), "jobs": [], "scrape_error": str|None, "scrape_stats": <run_scraper return>|None}`. So by default every call triggers a live scrape (blocking).
- `GET /dashboard/top-cities` [134-138]: Counter of truthy `city`; top 10 as `[{"name": city, "demand": count}]`.
- `GET /dashboard/industry-distribution` [140-145]: Counter of `str(company or "Unknown").strip()` (note `.get("company","Unknown")` default); top 5 as `[{"name", "value"}]`, empty names dropped. Company is used as an industry proxy (comment at 143).
- `GET /dashboard/top-roles` [147-151]: Counter of stripped truthy `title`; top 10 as `[{"role", "count"}]`.
- `GET /dashboard/city-role-distribution?city=` [153-165]: case-insensitive exact match on city; top 10 titles as `[{"name": role, "value": count}]`.
- `GET /dashboard/role-city-distribution?role=` [167-179]: case-insensitive exact match on title; top 10 cities, same shape.
- Unused imports: `json`, `Path`, `users_collection`.

#### `backend/api/worker_routes.py` (161 lines)
- `WorkerProfile{job_role: str, city: str, years_of_experience: float, role_description: str, skills: List[str]}` (all required) [16-21].
- `GET /worker/profile` [24-36]: returns `job_role, city, years_of_experience, role_description, skills (default []), gemini_risk_score, reasoning, reskilling_path, gemini_analysis` via `.get`.
- `POST /worker/profile` [38-105]:
  1. Build legacy dict `{"job_title": job_role, "city", "experience_years": years_of_experience, "writeup": role_description, "skills"}` [42-48].
  2. `parsed = parse_worker_profile(legacy)` [50] (Part B).
  3. If skills were supplied: `parsed["skills"] = list(set(parsed.get("skills", []) + profile.skills))` [53-54] (unordered, case-sensitive).
  4. `gemini_analysis = gemini_analyze_worker(job_title=, city=, experience=, skills=profile.skills or parsed.skills)` [63-68]. `gemini_score = gemini_analysis.get("risk_score")` [77]; the sync at [80-81] is a no-op (re-assigns the same value).
  5. `users_collection.update_one({"email": current_user["email"]}, {"$set": {name, email, job_role, city, years_experience (NOTE spelling), role_description, skills, gemini_risk_score, gemini_analysis, reasoning (= gemini_analysis["explanation"]), updated_at}}, upsert=True)` [83-99].
  6. Returns `{"parsed_profile": parsed, "gemini_analysis": gemini_analysis}` [102-105].
  - The old deterministic risk path (`compute_vulnerability_index`, `compute_worker_risk`, `generate_reskilling_path(parsed)`) is commented out [56-60]; the imports at lines 7 and 10 are unused.
- `GET /worker/reskilling` [110-124]: returns the stored `reskilling_result` if truthy, else `{recommendation_type: None, summary: "No reskilling analysis generated yet. Click 'Generate' to create one.", recommended_skills: [], recommended_courses: [], recommended_jobs: [], learning_path: [], error: None}`.
- `POST /worker/reskilling` [127-161]: if the user has no `job_role`, returns (HTTP 200) the same empty structure with `summary "Please fill in your Worker Analysis profile first."` and `error "No worker profile found. Submit your profile on the Worker Analysis page first."` [130-140]. Else `generate_reskilling_path(job_title=job_role, city=city or "", experience=float(years_experience or 0), skills=skills, gemini_analysis=stored)` [142-148]; saves `{"reskilling_result": result, "reskilling_updated_at": utcnow()}` with `$set` (no upsert) [153-159]; returns the result.

#### Data-model inconsistencies found in A.6 (important for reimplementation)
1. Signup writes `years_of_experience`; profile save writes `years_experience`. `GET /auth/me` and `GET /worker/profile` read `years_of_experience`, so after saving a profile they still return the signup value `None`. `POST /worker/reskilling` reads `years_experience` (the saved one). [FACT auth_routes.py:51, worker_routes.py:90, 29, 145]
2. `risk_score` is created `None` at signup and never written afterwards; the saved score is `gemini_risk_score`. `GET /auth/me` returns `risk_score` (always None). [FACT auth_routes.py:54,112; worker_routes.py:93]
3. `GET /worker/profile` reads `reskilling_path`, but nothing writes it (the stored key is `reskilling_result`). [FACT worker_routes.py:34, 156]

### A.7 Legacy pipeline helper modules

- `backend/pipeline/dummy_scraper.py` (30 lines): `get_dummy_jobs()` returns 3 fixed dicts `{title, city, skills[], description, ai_mentions, date}`: BPO Voice Executive/Pune (ai_mentions False, 2025-12-01), AI Content Reviewer/Pune (True, 2025-12-05), Data Analyst/Indore (True, 2025-12-10) [4-30]. Unused import `datetime`.
- `backend/pipeline/job_cleaner.py` (21 lines): `clean_jobs(jobs)` maps scraped dicts to dataset-schema keys: `jobtitle = title or query_role or ""`, `company`, `industry = ""`, `joblocation_address = location or query_city or ""`, `experience`, `postdate = utcnow "%Y-%m-%d %H:%M:%S +0000"` (scrape time, not posting time), `jobdescription = description`, `skills` [3-21].
- `backend/pipeline/skill_extractor.py` (7 lines): `extract_skills(jobs)` ensures `skills` is a list; non-lists are `str().split(",")` and stripped; mutates and returns [1-7].
- `backend/pipelines/job_pipeline.py` (15 lines): `run_job_pipeline()` calls `scrapers.naukri.naukri_scraper.run_scraper()`, logs and returns its stats; runnable as a script [8-15]. Usage (verified by grep): `job_cleaner.clean_jobs` and `skill_extractor.extract_skills` are imported only by `scrapers/naukri/naukri_scraper.py` (inside `run_scraper`); `dummy_scraper`, `ai_signal_detector` (empty) and `pipelines/job_pipeline.py` are not imported by any other module.

### A.8 Environment variables in Part A

| Name | Default | Where | Purpose |
|---|---|---|---|
| `MONGO_URI` | none (required) | db/mongo.py:9 | MongoDB connection string |
| `DATABASE_NAME` | `skills_mirage_db` | db/mongo.py:10 | Mongo database name |
| `JWT_SECRET_KEY` | `supersecretsaxkey` | utils/jwt_handler.py:18 | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | :19 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_HOURS` | `24` | :20 | token lifetime |

(`GEMINI_API_KEY` etc. are read in Parts B/C.)

### A.9 Data stores touched in Part A

- MongoDB: db `skills_mirage_db`, collection `users`. Fields seen: `_id, email, name, password, job_role, city, years_of_experience, years_experience, role_description, skills, risk_score, created_at, updated_at, gemini_risk_score, gemini_analysis, reasoning, reskilling_result, reskilling_updated_at`. No indexes are created in code (so no unique index on email) [INFERRED: none found in Part A].
- SQLite `backend/db/chat_data.db`: tables `courses`, `jobs` (A.4).
- CSV inputs of `init_db.py`: `dataset/courses.csv`, `dataset/naukri_jobs.csv`.

### A.10 Open questions for later parts
- What dict shape does `get_all_jobs()` return and from which file(s)? (Part B)
- What keys does `compute_vulnerability_index()` return beyond `role_risks`? (Part B)
- Which code actually uses `chat_data.db`, and what produced the 775-row jobs table? (Parts B, E)

Reference: `Asterrage2209/Mackahined` @ `d29294999a35f93c7d30ecf0d138b17b9c1dc158`. Paths relative to repo root; line numbers are real. Tags: [FACT file:line], [INFERRED], [NOT DETERMINABLE].

Files: `backend/data/dataset_manager.py` (222 lines), `backend/data/courses_dataset.py` (277), `backend/data/raw_jobs.json`, `backend/intelligence/{hiring_trends,skill_trends,vulnerability_index}.py`, `backend/worker_engine/{worker_parser,risk_score,worker_gemini,reskilling_engine}.py`, `backend/chatbot/{gemini_client,prompt_builder,query_router}.py`.

### B.1 Job data access: `backend/data/dataset_manager.py`

Role: the single in-memory store for the jobs dataset, backed by one CSV, used by almost every dashboard endpoint.

- `DATASET_PATH = <repo>/dataset/naukri_jobs.csv` (`Path(__file__).parents[2]`) [9]. Module globals `_jobs_df`, `_courses_df`, and an `RLock` `_df_lock` [11-15].
- `_SCHEMA_COLS` (the 14 canonical job columns) [17-21]: `company, education, experience, industry, jobdescription, jobid, joblocation_address, jobtitle, numberofpositions, payrate, postdate, site_name, skills, uniq_id`.
- `_AI_KEYWORDS` = `chatgpt, openai, generative ai, machine learning, automation, llm, gpt, ai tools` [23-26].
- `load_dataset()` [29-49]: if the CSV is missing, an empty DataFrame with the schema columns; else `pd.read_csv(path, dtype=str).fillna("")` (whole file into memory, all columns as strings); logs sample roles/cities; on any exception an empty DataFrame.
- `load_courses_dataset()` [52-66]: reads `<repo>/dataset/courses.csv` (`dtype=str`, `fillna("")`), empty DataFrame if missing or failing.
- `_parse_skills(s)` [69-76]: if the string starts with `[` and ends with `]` it tries `ast.literal_eval`; otherwise (or on failure) strips `[]` and splits on commas, trimming and dropping empties. Note it does not strip quotes in the fallback.
- `get_all_jobs()` [79-95]: under the lock loads the dataset if needed; returns `[]` if empty; converts the ENTIRE DataFrame with `to_dict("records")` and then for every row (outside the lock) sets: `skills` = parsed list; `city` = first comma-separated token of `joblocation_address` (trimmed), or `"Unknown"` if empty; `title` = `jobtitle`; `ai_mentions` = list of `_AI_KEYWORDS` found in the lower-cased `jobdescription`. This is recomputed on every call: there is no cache of the converted list.
- `get_all_courses()` [98-110]: reloads `courses.csv` from disk on EVERY call (comment 100), converts to records and replaces `skill_tags` with a lower-cased, trimmed list split on commas. It does not convert `duration_weeks` (stays a string) and there is no `duration` key.
- `append_jobs(new_jobs)` [113-161]: under the lock; builds a DataFrame from the scraper dicts; renames `title→jobtitle`, `description→jobdescription`, `location→joblocation_address` only if the new name is absent (127-134); joins list `skills` into a comma-separated string (136-139); adds missing schema columns as `""` (142-144); keeps only schema columns in schema order (146); concatenates onto the in-memory DataFrame; `drop_duplicates(subset=["jobtitle","company","postdate"], keep="first")` (153-155); if the row count grew, replaces the in-memory frame and calls `_save_async(copy)` (158-161). Dedupe key is title + company + postdate.
- `_save_async(snapshot)` [164-181]: daemon thread writes `<csv>.tmp.csv` then atomically replaces `naukri_jobs.csv`, i.e. the scraper rewrites the whole 52 MB CSV after every new batch.
- `get_latest_jobs(limit=100)` [184-207]: sorts the frame by `postdate` descending (string sort, NaN last), takes the head, and returns dicts `{jobtitle, company, location (first token of joblocation_address or "Unknown"), skills (string; joined with ", " if a list), experience, postdate}`.
- `save_dataset()` [210-219]: synchronous full CSV write.
- On import: `load_dataset()` and `load_courses_dataset()` run immediately [222-223].
- Returned job dict shape (all values strings unless noted): the 14 CSV columns plus `skills` (list), `city`, `title`, `ai_mentions` (list).

### B.2 Courses store: `backend/data/courses_dataset.py`

A second, separate store for `dataset/courses.csv` (used by the courses routes and the main.py startup check). Note the project has two parallel readers of the same CSV (this and `dataset_manager.get_all_courses`) with different output shapes.

- `DATASET_PATH = <repo>/dataset/courses.csv` [24]. Schema [26-36]: `name, source, domain, url, institution, duration_weeks, difficulty, skill_tags (comma string), syllabus_weeks (JSON string list)`.
- `load_dataset()` [46-58]; `is_empty()` [61-66]; `get_course_count()` [69-74]; `save_dataset()` [77-86]; `_save_async()` atomic write via `.tmp.csv` [89-101] (same pattern as jobs).
- `append_courses(new_courses)` [108-141]: ensure schema columns, concat, `drop_duplicates(subset=["name","source"], keep="first")`, async save if rows were added, else logs "No new courses".
- `get_all_courses()` [148-162]: records with `skill_tags` -> list (trimmed, original case), `syllabus_weeks` -> list (JSON, else comma-split), `duration_weeks` -> int or None.
- `query_courses_for_skills(skills, max_results=20)` [165-195]: lower-cased skill set; per course `searchable` = lower-cased tags UNION lower-cased whitespace-split words of `name + " " + domain`; `overlap` = size of intersection; keep courses with overlap > 0; sort by overlap descending (stable); return the top `max_results` course dicts.
- `query_courses_for_reskilling(target_role, current_skills, max_weeks=None, max_results=10)` [198-224]: search terms = lower-cased words of `target_role` plus lower-cased current skills; candidates = `query_courses_for_skills(terms, max_results=50)`; if `max_weeks` given, keep courses whose `duration_weeks` is None or `<= max_weeks` (a duration of 0 is treated as 999 because of `or 999`) [221]; return the first `max_results`.
- `get_courses_by_source(source)` [227-230]: filter on `source.upper()` equality.
- `get_stats()` [233-246]: `{"total", "swayam", "nptel", "domains": unique domain list}`; empty data returns zeros and `[]`.
- Helpers [253-273]: `_parse_tags`, `_parse_syllabus`, `_safe_int` (handles "", "None", floats like "12.0"). `load_dataset()` runs on import [277].

### B.3 `backend/data/raw_jobs.json`
List of 40 job dicts (verified), one scraper output snapshot with both naming styles: `jobtitle, company, joblocation_address, experience, skills (list), job_url, jobdescription (truncated "..."), title, location, description, ai_mentions (list), query_role, query_city` (e.g. `query_role="all_roles"`, `query_city="india"`). The only reference to this file is `OUTPUT_FILE` in `scrapers/naukri/naukri_scraper.py:37` (Part C), where the scraper writes it.

### B.4 Intelligence modules

#### `backend/intelligence/hiring_trends.py` (20 lines)
`compute_hiring_trends()`: for each job, `postdate` string; month key = first 7 chars if they match `^\d{4}-\d{2}$`, else the literal `"Recent"` [9-17]. Returns `[{"month": m, "job_count": c}]` sorted by month string ascending (so `"Recent"` sorts after digits) [19].

#### `backend/intelligence/skill_trends.py` (94 lines)
- `_extract_year(v)`: first 4 chars if digits -> int else None [4-8]. `get_available_job_years()`: sorted unique years, descending [11-18].
- `compute_skill_trends(year=None)` [21-63]: optionally filter jobs to that year. No jobs -> `{"rising_skills": [], "declining_skills": []}`. Otherwise "trend" is NOT time-based: jobs are split by list position, `midpoint = max(1, len(jobs)//2)`; `previous_group = jobs[:midpoint]`, `recent_group = jobs[midpoint:]` (assumes newer rows are at the end of the CSV; comment 33-35). Skill counts per group via `Counter.update(job["skills"])` (case-sensitive; every skill occurrence counted); `change = recent_count - previous_count`; sorted by change descending. `rising` = top 10 with change > 0 as `{"name", "growth": "+N", "color": "from-blue-500 to-cyan-400"}`; `declining` = LAST 10 entries of the sorted list with change < 0 as `{"name", "decline": "-N"}`. Returns `{"rising_skills", "declining_skills"}`. The `color` value is a Tailwind class string used by the frontend.
- `compute_skill_gap()` [65-94]: `demand` = count of each lower-cased job skill across all jobs; `supply` = count of each lower-cased course `skill_tag` over `dataset_manager.get_all_courses()`; for each job skill: `{"skill", "market_demand": demand, "training_supply": supply (0 if none), "gap": demand - supply}`; sorted by gap descending; returns the top 10. Gap is a raw difference, not a ratio.

#### `backend/intelligence/vulnerability_index.py` (125 lines): AI-vulnerability scoring (deterministic, keyword based)
Constants [4-15]: structural weights `W_SUSCEP=0.30, W_REPET=0.25, W_COMPLEX=0.20, W_HUMAN=0.15, W_ADAPT=0.10`; final weights `W_STRUCTURAL=0.55, W_HIRING=0.20, W_AI=0.15, W_REPLACE=0.10`.

`compute_vulnerability_index()` [22-125], per job (jobs with an empty role are skipped, 43-44):
1. `role = (jobtitle or title).strip().lower()`; `city = job.get("city","Unknown")` [40-41].
2. `text_corpus = lower(jobdescription) + " " + lower(" ".join(skills))` [46-48].
3. `_score_factor(keywords, text)` = number of DISTINCT listed keywords that appear as substrings (not occurrence counts) [18-19].
4. Structural factors [52-68]:
   - susceptibility keywords `data entry, manual, routine, processing, clerks, support, sorting, qa`; `suscep = min(100, hits*25)`
   - repetition `repeatable, daily, pipeline, maintain, scheduled, monitor`; `repet = min(100, hits*20)`
   - complexity `strategy, architect, design, research, innovate, lead, decision`; `complex_risk = 100 - min(100, hits*30)`
   - human interaction `client, stakeholder, negotiation, manage, team, mentor, therapy, teach`; `human_risk = 100 - min(100, hits*25)`
   - adaptability `agile, dynamic, startup, fast-paced, cross-functional`; `adapt_risk = 100 - min(100, hits*20)`
   - `structural = 0.30*suscep + 0.25*repet + 0.20*complex_risk + 0.15*human_risk + 0.10*adapt_risk`
5. Market signals [78-96]: `hiring_risk` is always 0 (`trend = 0` hard-coded, comment 81 admits hiring_trends returns monthly stats, not per-role data), so the 20% hiring weight does nothing; `ai_risk = min(100, hits(chatgpt, copilot, ai assistant, automation, generative ai, gpt) * 20)`; `replace_risk = min(100, 50 if role contains any of ["data entry","call center","content writer"] + 20 if role contains any of ["ai analyst","automation specialist","ai reviewer"])`.
6. `final = 0.55*structural + 0.20*hiring_risk + 0.15*ai_risk + 0.10*replace_risk`, clamped to `[5, 95]` [100-107].
7. Aggregates: list of final scores per `role` and per `city` [109-110]. Output `role_risks = {role: round(mean)}` and `region_risks = {city: round(mean)}` excluding city `"Unknown"` [112-117]. Returns `{"role_risks", "region_risks"}` [123-125].
- The function also calls `compute_hiring_trends()` (unused result) [25]; iterating all jobs with ~30 substring scans each means every call of `/dashboard/vulnerability*` is a full-dataset pass. A role with no keyword hits gets `structural = 0.20*100 + 0.15*100 + 0.10*100 = 45`, final `= 24.75` [INFERRED arithmetic from the constants].

### B.5 Worker engine

#### `backend/worker_engine/worker_parser.py` (20 lines)
`parse_worker_profile(profile)` reads `profile["writeup"]` and appends `"excel"` if the lower-cased write-up contains "excel", `"crm"` if it contains "crm", `"customer_support"` if it contains "customer". Returns `{"role": job_title, "city", "experience": experience_years, "skills": [...]}` [1-20]. (Very naive; only three skills.)

#### `backend/worker_engine/risk_score.py` (32 lines): legacy deterministic worker risk (now unused)
`compute_worker_risk(profile)`: `base = role_risks.get(role.lower(), 50)`; `+ region_risks.get(city, 0) * 0.1`; `- min(25, experience*2.5)`; `+ 15` if experience < 1; clamp `[5,95]`; `round`. Only imported (unused) by `worker_routes.py` [FACT risk_score.py:4-32; worker_routes.py:7]. This is the formula the Gemini prompt (B.5 next) tells the model to follow.

#### `backend/worker_engine/worker_gemini.py` (111 lines): Gemini AI-risk analysis
- Env var `GEMINI_API_KEY_WORKERANALYSIS` (separate key); missing key returns a fallback dict `{risk_score: None, risk_level: "unknown", pivot_roles: [], new_skills: [], explanation: "Gemini worker analysis is not configured. Set GEMINI_API_KEY_WORKERANALYSIS.", raw_response: ""}` [37-47].
- Model `gemini-2.5-flash` via `google.genai.Client(api_key=...).models.generate_content(model, contents=full_prompt)` [60-64]; no generation config, temperature or system role (the "system prompt" is concatenated text).
- Prompt `SYSTEM_PROMPT` [11-29] (single string): tells the model it receives 4 inputs (job title, city, years of experience, known skills) and must compute the risk of AI taking over the job; if very high suggest pivot roles; if moderate suggest more skills; if low reassure. It embeds the formula `Risk = Base Risk + (Regional Adjust × 0.1) - (Exp Reduction) + (Entry Penalty)` with explanations (base from role automation vulnerability; experience reduction up to 25; entry penalty 15 for under 1 year), a "Pivot Role Logic" paragraph (BPO profiles are prioritised for AI Content Moderation, other roles pivot toward Data Analytics), and a mandatory JSON-only response schema `{risk_score (0-100), risk_level (high|moderate|low), pivot_roles[], new_skills[], explanation}`. Important: the model is NOT given the base risk or regional values, so it invents them; the score is non-deterministic.
- User section [50-55]: lines `Current Job Title: …`, `City: …`, `Years of Experience: …`, `Known Skills: a, b` (or `None provided`), appended after `User Inputs:`.
- Parsing `_parse_gemini_response` [82-111]: greedy regex `\{[\s\S]*\}` over the raw text; `json.loads`; returns `{risk_score, risk_level (default "unknown"), pivot_roles, new_skills, explanation, raw_response}`; on a JSON error or no match, returns the default with `explanation = raw text`. No schema validation and no clamping of `risk_score` (a string would pass through).
- Request exceptions return the fallback dict with `explanation "Gemini request failed: <exc>"` [67-76].

#### `backend/worker_engine/reskilling_engine.py` (272 lines): Gemini reskilling plan
- Env var `GEMINI_API_KEY_RESKILLING` (third key); missing -> `_error_response("Gemini reskilling is not configured. Set GEMINI_API_KEY_RESKILLING.")` [150-153].
- `generate_reskilling_path(job_title, city, experience, skills, gemini_analysis=None)` [139-230]:
  1. `trends = compute_skill_trends()` (all years); `rising = trends["rising_skills"][:10]`, `declining = [...][:10]` [156-158].
  2. Target skill pool: user skills + `gemini_analysis.new_skills` + `gemini_analysis.pivot_roles` (role names mixed in with skills) + names of rising skills; de-duplicated with `set` [161-166].
  3. `_find_matching_courses(pool, 30)` [80-104]: over `dataset_manager.get_all_courses()`; overlap = size of (lower pool ∩ lower tags); keep overlap > 0; sort descending; return up to 30 dicts `{name, source, url, duration (get("duration") → "" because the CSV column is `duration_weeks`), skill_tags (comma string)}`. Only exact tag equality, no fuzzy match.
  4. `_find_matching_jobs(pool, 20)` [110-133]: over `get_all_jobs()` (whole dataset), overlap = lower pool ∩ lower job skills; sort descending; return up to 20 `{title, company, location (city), skills (first 10 joined)}`.
  5. Prompt = `SYSTEM_PROMPT` + `--- Worker Profile ---` (title, city, experience, skills) + optional `--- AI Risk Assessment ---` (score/100, level, pivot roles, new skills, explanation) + `--- Market Hiring Trends ---` (JSON of rising and declining lists) + `--- Available Training Courses (matched to target skills) ---` (JSON of the first 20 matched courses, indent 2) + `--- Relevant Job Openings (matched to target skills) ---` (JSON of the first 15 jobs) [173-214].
  6. `SYSTEM_PROMPT` [25-74]: career-guidance AI; inputs: profile, AI-risk assessment, rising/declining skills, course list, job list; rule: INCREASING demand in the worker's field -> recommend UPSKILLING, DECLINING -> RESKILLING; match each recommended skill to the given courses; match skills to the given jobs; produce a weekly learning path; respond ONLY with JSON `{recommendation_type: "upskilling"|"reskilling", summary, recommended_skills[{skill, reason}], recommended_courses[{name, source, url, duration, matched_skills[]}], recommended_jobs[{title, company, location, required_skills[], match_reason}], learning_path[{week: "Week 1-2", title, description}]}`.
  7. Same model `gemini-2.5-flash`, same call style; exceptions -> `_error_response("Gemini request failed: <exc>")` [217-227].
  8. `_parse_response` [236-259]: greedy-regex JSON; returns the six keys plus `raw_response` and `error: None` (recommendation_type default `"reskilling"`); on failure returns `_error_response("Could not parse Gemini response.")` with `raw_response` set and `summary` replaced by the raw text.
  9. `_error_response(msg)` [262-272] returns the empty structure `{recommendation_type: None, summary: msg, recommended_skills: [], recommended_courses: [], recommended_jobs: [], learning_path: [], raw_response: "", error: msg}`.
- Note: the stored `reskilling_result` is this whole dict including `raw_response` (the full LLM text) and is saved to Mongo as is.

### B.6 Chatbot

#### `backend/chatbot/gemini_client.py` (59 lines)
- `ask_gemini(prompt)` [7-21]: key from `GEMINI_API_KEY` or `GOOGLE_API_KEY`; missing key returns the STRING `"Gemini is not configured. Set GEMINI_API_KEY and try again."` (not an error); model `gemini-2.5-flash`; exceptions returned as the string `"Gemini request failed: <exc>"`; empty text -> `"No response text returned by Gemini."`. Errors are therefore returned as normal chat text (HTTP 200).
- `generate_sql_query(user_prompt, schema_definition)` [23-36]: prompt tells the model it converts natural language to safe, read-only SQLite queries, to respond with ONLY the SQL and no Markdown, gives the schema (from `sqlite_master`), and says the question may be English or Hindi.
- `generate_natural_response(user_prompt, sql_results, worker_profile=None)` [38-59]: prompt with optional worker-profile context, the user question, the database results (JSON-like text), instruction to give a concise summary mentioning only existing data, and a MANDATORY LANGUAGE RULE: reply entirely in the same language as the question (English or Hindi), no mixing.

#### `backend/chatbot/prompt_builder.py` (16 lines)
`build_prompt(query)` returns a short template (worker profile + question + "Answer using labour market insights."). It is not imported anywhere in the repository [FACT grep over backend and frontend/src].

#### `backend/chatbot/query_router.py` (254 lines): intent routing
- `DB_PATH = backend/db/chat_data.db` [9].
- Keyword lists [13-36]: `_RISK_KEYWORDS` (about 25 English and Hindi-transliterated phrases such as "risk score", "my risk", "vulnerability", "ai risk", "jokhim", "mera risk") and `_IMPROVEMENT_KEYWORDS` (about 35, e.g. "improve", "reduce risk", "career path", "future", "reskill", "upskill", "learning path", "course", "recommend", "timeline", "kya seekhu", "kaise improve", "path").
- `_classify_intent(question)` [41-55]: lower-case substring tests; improvement keywords are checked FIRST, then risk keywords, else `data_query`. (Broad words like "future", "course", "path" capture many questions, including dataset questions mentioning courses.)
- `handle_query(query, user_data=None)` [228-254]: `question = query["question"]`; `worker_profile = query["worker_profile"]`; classify; route:
  - `risk_explanation` -> `_handle_risk_explanation(question, user_data)` [60-103]: reads `user_data.gemini_analysis` (risk_score, risk_level, explanation, pivot_roles, new_skills) and `job_role`; if no analysis or `risk_score is None`, returns a canned message telling the user to fill the Worker Analysis page and click "Analyze Risk & Opportunities"; else builds a context sentence and a prompt ("career guidance AI assistant... answer using ONLY the analysis data below... Do NOT say I don't know") with the language rule, and calls `ask_gemini`.
  - `improvement_guidance` -> `_handle_improvement_guidance` [106-167]: builds risk context from `gemini_analysis` and reskilling context from `reskilling_result` (if it has `recommendation_type`; includes summary, skills, first 8 courses, first 8 jobs, learning path as JSON); if both empty returns a canned instruction (submit profile, then "Generate Reskilling Path"); else a prompt with user profile (job role and skills), risk analysis, reskilling recommendations, question, and the language rule; `ask_gemini`.
  - `data_query` -> `_handle_data_query(question, worker_profile)` [193-223] inside try/except returning `"Error processing query: <e>"` [251-254]: (1) schema text = `CREATE` statements from `sqlite_master` of `chat_data.db` (or "Database missing…") [172-180, 195-197]; (2) `generate_sql_query` -> Gemini returns SQL; `clean_sql` strips ```sql fences [182-190, 199-200]; (3) safety: if the upper-cased SQL contains `DROP`, `DELETE`, `UPDATE`, or `INSERT` as substrings, returns "Query blocked due to safety restrictions." [203-205] (no check for ALTER, PRAGMA, ATTACH, CREATE; the connection is read-write; a column named `updated…` would be blocked); (4) execute with `sqlite3`, `fetchall` [207-211]; (5) format: first 20 rows as list of dicts, `str(...)[:3000]`; prefix `Found N results (showing top 20):` if more than 20; "No records found matching the criteria." if none [213-221]; (6) `generate_natural_response(question, formatted, worker_profile)` -> Gemini.
- The `worker_profile` passed to the data path comes from the CLIENT request body, not from Mongo [INFERRED from chatbot_routes.py:33 and query_router.py:238].
- The Mongo `user_data` handed to the router includes the password hash (A.6), but the code reads only `gemini_analysis`, `reskilling_result`, `job_role`, `skills`.

### B.7 Gemini usage summary

| Feature | Function | Env var | Model | Input | Output handling |
|---|---|---|---|---|---|
| Worker AI-risk analysis | `worker_gemini.analyze_worker` | `GEMINI_API_KEY_WORKERANALYSIS` | gemini-2.5-flash | title, city, experience, skills | JSON regex parse, fallback dict |
| Reskilling plan | `reskilling_engine.generate_reskilling_path` | `GEMINI_API_KEY_RESKILLING` | gemini-2.5-flash | profile + risk result + trends + 20 courses + 15 jobs | JSON regex parse, error dict |
| Chatbot (all intents) | `gemini_client.ask_gemini` | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | gemini-2.5-flash | intent-specific prompts | raw text returned |

Calls are synchronous inside FastAPI sync handlers; there is no retry, timeout, rate limiting, caching, or token accounting.

### B.8 Calls into other modules (interface table)

| Caller | Callee | Module | Args | Return use |
|---|---|---|---|---|
| dashboard_routes.vulnerability | compute_vulnerability_index | intelligence.vulnerability_index | none | `role_risks` map |
| reskilling_engine | compute_skill_trends | intelligence.skill_trends | none | rising/declining lists |
| reskilling_engine | get_all_jobs / get_all_courses | data.dataset_manager | none | full job / course lists |
| skill_trends | get_all_jobs / get_all_courses | data.dataset_manager | none | counts |
| vulnerability_index | compute_hiring_trends | intelligence.hiring_trends | none | unused |
| risk_score | compute_vulnerability_index | intelligence.vulnerability_index | none | role/region maps (module unused) |
| query_router | ask_gemini, generate_sql_query, generate_natural_response | chatbot.gemini_client | prompts | text |
| main.py / courses_routes | courses_dataset functions | data.courses_dataset | see A | see A |
| naukri scraper (Part C) | append_jobs | data.dataset_manager | list of job dicts | writes CSV |

### B.9 Data-processing facts (no judgement)
- Jobs: one CSV (`dataset/naukri_jobs.csv`, ~52 MB) is loaded fully into a pandas DataFrame of strings at import. Every request that touches jobs re-converts all rows to Python dicts and re-parses skills, city, and AI mentions. `/dashboard/vulnerability*` scans every job across ~30 keywords on each call. Hiring and skill trends, skill gap, top-N lists, stats, and the reskilling job match are all single-process Python loops/Counters over the full list.
- Courses: `courses.csv` (~133 KB) is re-read from disk on every `get_all_courses()` call in `dataset_manager`.
- Writes: scraped jobs/courses are appended in memory and the entire CSV is rewritten by a daemon thread.
- Nothing is cached, indexed, or computed offline in batch; there is no scheduled job-metrics precomputation.

### B.10 Bugs and oddities in Part B
1. Vulnerability: `hiring_risk` is always 0 (hard-coded), so 20% of the nominal weight is dead. [vulnerability_index.py:82-83]
2. Skill "trend" compares first half vs second half of the CSV ROWS, not time periods; correctness depends on CSV row order. [skill_trends.py:36-38]
3. Reskilling course `duration` is always empty (column is `duration_weeks`). [reskilling_engine.py:100 vs courses_dataset.py:32]
4. Course matching mixes role names (`pivot_roles`) with skill tags, so role names rarely match. [reskilling_engine.py:163-166]
5. SQL guard is a weak substring blacklist; the DB connection is read-write. [query_router.py:203]
6. Three different Gemini env var names; chatbot errors returned as normal text.
7. `_extract_year` / trends use `postdate` strings; scraper writes scrape time as `postdate` (see A.7, Part C), so trends can reflect scrape time, not posting time. [INFERRED]
8. `get_all_jobs()` is O(N) per request with no cache.

### B.11 Open questions
- How many rows does `naukri_jobs.csv` actually have, and what is its real column list? (Part E)
- Which function in the scraper produces `postdate`, and is it posting time or scrape time? (Part C)

Reference: `Asterrage2209/Mackahined` @ `d29294999a35f93c7d30ecf0d138b17b9c1dc158`. Paths relative to repo root; line numbers are real. Tags: [FACT file:line], [INFERRED], [NOT DETERMINABLE].

Files: `backend/scrapers/naukri/{naukri_urls,naukri_parser,naukri_scraper}.py`, `backend/scrapers/utils/{http_client,selenium_client,skill_extractor}.py`, `backend/scrapers/courses/{courses_scraper,swayam_scraper,nptel_scraper}.py`, empty `__init__.py` files, `dataset/update_course_skills.py`, `backend/test_*.py`, `backend/out.txt`, `backend/test_out.txt`.

### C.1 Job scraping (Naukri.com)

#### Overview
Selenium (headless Chrome) loads Naukri search-result pages, BeautifulSoup (lxml) parses the job cards, results are written to `data/raw_jobs.json` and appended to the main jobs CSV through the cleaning pipeline. Triggered ONLY by `GET /dashboard/scraped-jobs` (default `refresh=true`) or by running `pipelines/job_pipeline.py` / the scraper module as a script; no scheduler runs it [FACT dashboard_routes.py:117-123; main.py:41-48 schedules only courses].

#### `backend/scrapers/naukri/naukri_urls.py` (64 lines): URL builders
- `build_search_url(role, city, page)` [1-8]: spaces replaced by `-`; if city is `india` or `all`: `https://www.naukri.com/{role}-jobs` (page 1) or `...-jobs-{page}`; else `https://www.naukri.com/{role}-jobs-in-{city}-{page}`.
- `build_city_search_url(city, page)` [11-20]: for india/all: page 1 `https://www.naukri.com/jobs`, else `https://www.naukri.com/jobs-in-india?k=jobs&l=india&pageNo={page}`; other cities: `.../jobs-in-{city}` or `...?pageNo={page}`. (Not used by the scraper; only the candidates function is.)
- `build_city_search_url_candidates(city, page)` [23-65]: ordered candidate URLs tried until one yields cards. india/all page 1: `/jobs`, `/jobs-in-india?k=jobs&l=india&pageNo=1`, `/india-jobs`; pages 2+: `/jobs-in-india?k=jobs&l=india&pageNo={page}` first, then `/jobs-{page}`, `/india-jobs-{page}`. Other cities page 1: `/jobs-in-{city}`, `...?k=jobs&l={city}&pageNo=1`, `/{city}-jobs`; pages 2+: three analogous patterns. Comments document that some patterns 404 and that order was changed to avoid 20 s timeouts.

#### `backend/scrapers/naukri/naukri_parser.py` (117 lines): HTML to dict
- Card container selectors tried in order, first with matches wins [9-17]: `div.cust-job-tuple`, `div.srp-jobtuple-wrapper`, `article.jobTuple`, `div[class*='jobTuple']`, `div[class*='job-tuple']`, `li.jobTuple`.
- Field selector lists (first matching element wins) [28-33]: title `a.title, a[title], h2.title, a.jobTitle`; company `a.comp-name, a.subTitle, span.comp-name, div.comp-name`; location `span.locWdth, span.loc-wrap, span.location, li.location`; experience `span.expwdth, span.exp-wrap, span.experience, li.experience`; description `span.job-desc, div.job-desc, p.job-desc`; skills (first selector with results) `li.tag-li, li.dot, li.skill-li, span.skill-tag` [83-89].
- `extract_job_cards(html)` [49-105]: parse; pick the first card selector with results; if none, log a warning with an 800-char HTML preview; for each card return `{jobtitle, company, joblocation_address, experience, skills (list), job_url (href of title), jobdescription, title, location, description}` (duplicate legacy keys `title/location/description`). Missing elements give `None`.
- `extract_job_description(html)` [108-118]: first match of `span.job-desc, section.job-desc, div.styles_JDC__dang-inner-html, div.dang-inner-html, [data-testid='job-description']`; unused by the scraper (detail pages are never fetched; `failed_job_pages` and `detail_desc_missing` are always 0).
- Consequence: `jobdescription` is only the short card snippet (about 90 characters ending in "..."), as seen in `data/raw_jobs.json` [INFERRED from the sample].

#### `backend/scrapers/utils/selenium_client.py` (138 lines)
- `CARD_WAIT_SELECTORS = ["div.cust-job-tuple", "div.srp-jobtuple-wrapper"]` [16-19].
- `create_driver(headless=True)` [22-79]: Chrome with `--headless=new`, `--no-sandbox`, `--disable-dev-shm-usage`, window 1920x1080, `--disable-gpu`, anti-automation flags (excludeSwitches enable-automation, useAutomationExtension False, `--disable-blink-features=AutomationControlled`, a fixed Chrome/122 macOS user agent), images and media blocked (CSS and fonts deliberately NOT blocked, with an explanatory comment), several background-feature disables; page load strategy `normal`; after creation runs JS to hide `navigator.webdriver`. Needs Chrome + a driver available to Selenium.
- `fetch_rendered_html(driver, url, wait_selector="body", timeout=20)` [82-127]: `driver.get(url)`; waits up to `timeout / 2` s for each card selector in turn; if neither appears, logs a warning, sleeps 1.5 s, and returns the current `page_source` anyway. (`wait_selector` is unused.)
- `create_driver_pool(size=3, headless=True)` [130-139]: list of independent drivers.

#### `backend/scrapers/utils/http_client.py` (24 lines)
`fetch(url)` with `requests.get`, a randomly chosen one of two User-Agents, 15 s timeout, `raise_for_status`, then a random 1.5 to 3.5 s sleep. Not imported by the Naukri scraper [INFERRED: grep shows the scraper uses selenium_client].

#### `backend/scrapers/utils/skill_extractor.py` (22 lines)
`AI_KEYWORDS` = `chatgpt, openai, generative ai, machine learning, automation, llm, gpt, ai tools`; `detect_ai_mentions(text)` returns the list of those found in lower-cased text.

#### `backend/scrapers/naukri/naukri_scraper.py` (401 lines): orchestrator
- Constants [20-51]: `ROLES = [data analyst, data scientist, bpo, software engineer, ai engineer]`; `CITIES = ["india"]`; `MAX_PAGES = 5`; `SCRAPER_JOB_LIMIT = 150` (unused); `DRIVER_POOL_SIZE = 3`; `OUTPUT_FILE = data/raw_jobs.json`; `DEBUG_HTML_DIR = data/debug_html`; `BLOCK_HINTS` (captcha, verify you are human, access denied, request cannot be processed, unusual traffic, forbidden, cloudflare, akamai, security check). The module calls `logging.basicConfig` at import with level from `SCRAPER_LOG_LEVEL` (default INFO) [40-44].
- `DriverPool` [60-82]: thread-safe `queue.Queue` of drivers; `acquire` blocks, `release`, `quit_all`.
- `_looks_blocked`, `_matched_block_hints` [89-96]; `_save_debug_html` [99-105]; `_enrich(job, role, city)` adds `ai_mentions = detect_ai_mentions(description)`, `query_role`, `query_city` [108-112].
- `_fetch_city_page(pool, city, page, max_pages, save_debug)` [119-165]: borrow a driver; try each candidate URL: fetch rendered HTML, parse cards, first URL with cards wins; if none, mark failed, optionally save debug HTML and log block hints; always release the driver; returns `{page, cards, failed, candidates, html}`.
- `_fetch_role_page` [168-194]: same for the role-based URL (`build_search_url`).
- `_scrape_city_sequential(pool, city, max_pages, save_debug)` [201-249]: pages 1..max_pages strictly sequential; each page failure/empty increments counters; jobs enriched with role `"all_roles"`; sleeps 1.5 s between pages; returns jobs plus stats (`failed_search_pages, failed_job_pages=0, total_search_pages, empty_card_pages, detail_desc_missing=0`). Note: despite the 3-driver pool, only one page is fetched at a time, so only one driver is ever used (`ThreadPoolExecutor`, `as_completed` imported but unused) [FACT 8, 210-238].
- `_scrape_role_city_matrix_sequential` [252-303]: fallback over (role x city x page) sequentially, 1.5 s sleeps.
- `run_scraper()` [310-398]:
  1. Config from env: `SCRAPER_ROLES` (comma list, default ROLES), `SCRAPER_CITIES` (default `["india"]`), `SCRAPER_MAX_PAGES` (default 5), `SCRAPER_ALL_ROLES_FOR_CITY` (default "1"), `SCRAPER_TARGET_CITY`, `SCRAPER_SAVE_DEBUG_HTML` (default "0"), `SCRAPER_HEADLESS` (default on), `SCRAPER_DRIVER_POOL_SIZE` (default 3) [314-321].
  2. A module-level non-blocking lock: if a run is active, returns `{"total_jobs": 0, "mode": "skipped_busy", "run_id": ...}` [323-325].
  3. Creates the Chrome pool [336-337]. Mode "all roles for city" (default): city-wide scrape for `target_city` or each of `cities`; if 0 jobs, falls back to the role-city matrix [344-363]; else matrix mode [364-368].
  4. `finally`: quits all drivers and releases the lock [370-373].
  5. Overwrites `data/raw_jobs.json` with the list of jobs (`indent=2`) [375-378].
  6. Pipeline: `append_jobs(extract_skills(clean_jobs(jobs)))` inside try/except that only logs errors [380-386].
  7. Returns `{total_jobs, failed_search_pages, failed_job_pages, total_search_pages, empty_card_pages, detail_desc_missing, mode ("all_roles_city" or "role_city_matrix"), target_city, output_file, run_id, duration_sec}` [388-398].
- Runtime scale (documented in comments only): up to 5 pages x about 20 cards = about 100 jobs per run [30]; `data/raw_jobs.json` holds 40 jobs [FACT verified count in Part B].

#### Data produced by the scraper pipeline
1. Card dict (parser) -> 2. `clean_jobs` maps to dataset keys and stamps `postdate` with the SCRAPE time (`utcnow`, format `%Y-%m-%d %H:%M:%S +0000`) and `industry = ""` and drops `job_url`/`ai_mentions`/`query_*` [FACT pipeline/job_cleaner.py:5-18] -> 3. `extract_skills` ensures a list -> 4. `append_jobs` renames/pads to 14 schema columns, dedupes on (jobtitle, company, postdate), and rewrites `dataset/naukri_jobs.csv`.
- Because `postdate` is the scrape time, the dedupe key changes on every run, so the same job scraped in two runs is stored twice [INFERRED from job_cleaner.py:5 and dataset_manager.py:153]. Monthly "hiring trends" and year filters then reflect scrape times for scraped rows [INFERRED].
- `chat_data.db` is NOT updated by scraping.

### C.2 Course scraping

#### `backend/scrapers/courses/courses_scraper.py` (152 lines): orchestrator
- `OUTPUT_FILE = data/courses_raw.json` (3 levels up) [31]; module lock [33].
- `_normalize_course(c)` [36-53]: output keys `name, source, domain, url, institution` (stripped strings), `duration_weeks` (int or None), `difficulty`, `skill_tags` as a comma-joined string, `syllabus_weeks` as a JSON string.
- `run_courses_scraper(swayam=True, nptel=True, max_per_source=200)` [56-137]: non-blocking lock (busy -> stats with `mode "skipped_busy"`); scrape SWAYAM then NPTEL each in its own try/except; normalise courses that have a name; overwrite `data/courses_raw.json`; call `courses_dataset.append_courses(normalized)` (dedupe on name+source, async CSV rewrite); return `{total_courses, swayam_count, nptel_count, duration_sec, run_id, output_file}`.
- `run_courses_scraper_background(max_per_source=200)` [140-149]: daemon thread for the startup trigger.
- Callers: startup if the CSV has fewer than 200 courses; weekly APScheduler job with `max_per_source=50`; `POST /scrape/courses` [A.1, A.6].

#### `backend/scrapers/courses/swayam_scraper.py` (369 lines, "v4")
- Source: published Google Sheet CSV (base URL with a fixed `2PACX-...` id and `gid` per tab) for coordinators `CEC, IIMB, NITTTR, AICTE, INI, UGC, IGNOU` (seven gids) [28-43]. No HTML scraping.
- `_get(url)` [95-104]: 3 attempts, 15 s timeout, 1.5 s sleep between failures; returns None.
- Noise filtering [57-92, 107-156]: a large set `_NOISE_PATTERNS` (discipline names, abbreviations like cse/ece, degree names, audience words), degree regex, min/max tag length (3 and 60), sentence markers (" would ", " should ", " is ", ...), generic words, "exposure to ...", "etc", URL fragments; `_is_noise(tag)` returns True for any of these.
- `_clean_skill_tags` dedupes case-insensitively; `_extract_skills_from_text` splits on `,` or `;`, strips `*` and `.`, drops noise [159-184].
- `_find_columns(header_row)` maps header cells to fields by substring: title ("course title" or "title"), discipline, institution ("university/institute/host"), level (excluding "ncrf"), duration, industry sectors, url ("preview" + "url"), language, program ("program" + "aligned") [189-216]. `_parse_duration` takes the first number and casts `int(float(x))` [219-226].
- `_parse_sheet_tab(csv_text, coordinator)` [231-331]: header row = first of the first 5 rows containing "course title" or "preview"; skip titles shorter than 3 characters or without any Latin letters; URL = regex `(https://[^\s,;]+/preview)` else "" if not http; skill tags = title (if not noise) + discipline terms + industry-sector terms + "program aligned" terms, cleaned and capped at 15; course dict `{name, source "SWAYAM", domain (discipline unless noise, else "<coordinator> Course"), url, institution, duration_weeks, difficulty (= level), skill_tags, syllabus_weeks []}`.
- `scrape_swayam(max_courses=300)` [334-370]: fetch tabs in order, stop once `len(all) >= max_courses`, dedupe by lower-cased name, truncate to `max_courses`.

#### `backend/scrapers/courses/nptel_scraper.py` (416 lines, "v3")
- Course list: NPTEL tab (`gid=3134725`) of the same Google Sheet; IDs extracted with regexes `nptel\.ac\.in/([a-z0-9_]+)/preview` and `(noc\d{2}_[a-z0-9]+)`, de-duplicated preserving order [129-147]. If the sheet is unreachable, a hard-coded `FALLBACK_COURSE_IDS` list of 49 IDs (noc25_*, noc24_*) is used [40-61, 405-407].
- Each course page `https://onlinecourses.nptel.ac.in/{id}/preview` is fetched with `requests` (timeout 12 s, 3 retries) and parsed with BeautifulSoup/lxml; a `DELAY = 0.6` s sleep before every course [63-71, 384-417].
- `_parse_preview` [271-381]: name = first `<h1>`; institution = text after the last `|` in a string starting with "By"; domain = first `<li>` of the "Category" table cell; `duration_weeks` = first integer in the "Duration" cell; `difficulty` = "Level" cell text; skill tags = course name + remaining Category items + regex captures of INTENDED AUDIENCE / INDUSTRY SUPPORT / PREREQUISITES text (`[^\n*]{5,200}`) split on `, ; /`, cleaned and capped at 15; syllabus = up to 16 "Week N ..." entries (from the "course layout" heading, else a text regex).
- Noise filter `_is_noise` is a near-copy of the SWAYAM one (code duplication) [150-209].
- `scrape_nptel(max_courses=200)` [400-417]: IDs `[:max_courses]`, sequential.
- Result in the committed DB: NPTEL 200, SWAYAM 198 rows [A.4].

### C.3 `dataset/update_course_skills.py` (100 lines): offline enrichment script
`update_course_skills(jobs_csv, courses_csv)` [8-90]: (1) read both CSVs; (2) build the set of unique job skills from the jobs CSV `skills` column (comma split, lower-cased; keep if length > 1 or in `c, r, java, sql, css, html`) [14-19]; (3) sort skills by length descending [22]; (4) for each course, text = `lower(name) + " " + lower(domain)`; skills of length <= 4 matched with regex word boundaries, longer skills by substring; matches stored title-cased [51-68]; (5) if none, apply a keyword fallback table (`cyber, eco, environ, commerce, psych, german, animat, socio, histor, art, arts, film, physical educ, geo, politi, litera, hindi, bio, math` mapped to 3-4 skills each, first matching key wins) [25-45, 71-76]; (6) else assign `Research, Communication Skills, Analytical Skills` [79-81]; (7) write `skill_tags` as `", ".join(set)` (unordered) and overwrite the courses CSV [84-87]. Script entry resolves paths next to itself [92-100]. This explains why the CSV `skill_tags` are job-skill-like terms rather than scraped tags. Output tags use ", " (comma + space), which `get_all_courses` handles by stripping.

### C.4 Tests and logs (all manual scripts, no assertions)
- `backend/test_auth.py` (50 lines): requests against `http://localhost:8000/auth`: signup (payload includes extra fields `job_role, city, years_of_experience, role_description` that the signup model ignores), login, `/me`; prints results, exit codes by outcome.
- `backend/test_chatbot.py` (27 lines): loads `backend/.env`, calls `handle_query` with a Hinglish question and a sample profile.
- `backend/test_parser.py` (7 lines): runs `extract_job_cards` on one embedded Naukri card HTML (useful as a fixture: shows card markup with classes `cust-job-tuple`, `title`, `comp-name`, `expwdth`, `locWdth`, `job-desc`, `tag-li`, and a `job-post-day` span "3 days ago" that the parser does NOT read).
- `backend/test_scrapers.py` (31 lines): scrapes 5 courses from each source and prints tags.
- `backend/out.txt`, `backend/test_out.txt` (UTF-16 logs): saved output of the chatbot test showing a Gemini `429 RESOURCE_EXHAUSTED` (free-tier quota; model name `gemini-2.0-flash`, so an older version of the code) turned into an SQL syntax error `near "Gemini"`. This reveals a real failure mode: when the Gemini call fails, `ask_gemini` returns its error STRING, which `_handle_data_query` then executes as SQL [FACT query_router.py:199-209; gemini_client.py:18-19].
- No automated test framework (no pytest config, no CI).

### C.5 Environment variables found in Part C

| Name | Default | Where | Purpose |
|---|---|---|---|
| `SCRAPER_LOG_LEVEL` | INFO | naukri_scraper.py:40 | log level |
| `SCRAPER_ROLES` | (ROLES list) | :314 | comma list of roles |
| `SCRAPER_CITIES` | india | :315 | comma list of cities |
| `SCRAPER_MAX_PAGES` | 5 | :316 | pages per query |
| `SCRAPER_ALL_ROLES_FOR_CITY` | 1 | :317 | city-wide mode |
| `SCRAPER_TARGET_CITY` | "" | :318 | single city override |
| `SCRAPER_SAVE_DEBUG_HTML` | 0 | :319 | save failed-page HTML |
| `SCRAPER_HEADLESS` | on | :320 | headless Chrome |
| `SCRAPER_DRIVER_POOL_SIZE` | 3 | :321 | Chrome instances |

### C.6 Observations (facts, no judgement)
- Job source: Naukri.com public search pages via Selenium; course source: a public Google Sheet (SWAYAM, NPTEL list) and NPTEL preview pages via `requests`.
- Anti-bot measures present: UA spoofing, `navigator.webdriver` hiding, 1.5 s delays, block-hint logging. No proxy rotation.
- Scraping happens inside the API process (a request handler for jobs; background threads for courses), not as a separate batch job.
- All scraper writes go to local files (`data/raw_jobs.json`, `data/courses_raw.json`, `dataset/*.csv`).
- Scraper output (`jobdescription` snippet only, no salary, no education, no job id) fills only 6 of the 14 schema columns; the rest are `""`. [INFERRED from clean_jobs:9-18 and append_jobs padding]

### C.7 Open questions
- Is `scrape_all_roles_for_city` mode (roles ignored) the only mode used in practice? (Default is "1", so yes unless env overrides.)
- Do the committed courses CSV's tags come from `update_course_skills.py` runs? (Part E will compare the data.)

## 6. Frontend, page by page and component by component
Reference: `Asterrage2209/Mackahined` @ `d29294999a35f93c7d30ecf0d138b17b9c1dc158`. Paths relative to `frontend/` unless stated; line numbers are real. Tags: [FACT file:line], [INFERRED], [NOT DETERMINABLE].

### D.1 Project setup

- Tooling [FACT package.json]: scripts `dev` (`vite`), `build` (`vite build`), `lint` (`eslint .`), `preview` [6-11]. ES modules (`"type": "module"`).
- Runtime dependencies (all floating caret ranges) [12-23]: `react ^18.3.1`, `react-dom ^18.3.1`, `react-router-dom ^7.13.1`, `recharts ^3.7.0`, `lucide-react ^0.577.0`, `papaparse ^5.5.3`, `clsx ^2.1.1`, `tailwind-merge ^3.5.0`, `d3-scale ^4.0.2`, `react-simple-maps ^3.0.0`. Dev: `vite ^5.4.10`, `@vitejs/plugin-react ^4.3.3`, `typescript ~5.6.2`, `tailwindcss ^3.4.19`, `postcss ^8.5.8`, `autoprefixer ^10.4.27`, `eslint ^9.13.0`, `typescript-eslint ^8.11.0`, react-hooks and react-refresh ESLint plugins, `@types/*`.
- Unused dependencies [INFERRED from grep of src]: `clsx`, `tailwind-merge`, `d3-scale`, `react-simple-maps` (the README advertises maps, but no map component exists). `papaparse` is used only by `utils/jobDataLoader.ts`, which nothing imports.
- `vite.config.ts` [1-7]: only the React plugin; no proxy, no alias, no env handling.
- `tailwind.config.cjs` [1-23] content globs `index.html`, `src/**/*.{js,ts,jsx,tsx}`; custom colors `background #0b1120`, `secondary #111827`, `card #1f2937`, `accent #3b82f6`, `textPrimary #e5e7eb`, `textSecondary #9ca3af`; font `Inter, system-ui, sans-serif`. `tailwind.backup.js` is a UTF-16 near-copy of this file (dead). `postcss.config.cjs`: tailwindcss + autoprefixer.
- `tsconfig.app.json`: strict, `noUnusedLocals`, `noUnusedParameters`, target ES2020, bundler resolution, `jsx: react-jsx`, includes `src` [3-25]. `tsconfig.node.json` covers `vite.config.ts`. ESLint flat config: js recommended + typescript-eslint recommended + react-hooks rules + react-refresh warning [eslint.config.js:7-27].
- Env var: `VITE_API_BASE_URL` (`.env.example` value `http://127.0.0.1:8000`); code falls back to `http://localhost:8000` [services/api.ts:1]. Note the backend CORS allows only `http://localhost:5173` and `:3000` (A.1); using `127.0.0.1` as the page origin would be blocked [INFERRED].
- `index.html`: title is still "Vite + React + TS", favicon `/vite.svg` [4-7]. `src/index.css` Tailwind layers plus custom classes `.card`, `.card-glow`, `.btn-primary`, `.btn-secondary`, `.input-field` [18-40]. `src/App.css` is the unused Vite template CSS (not imported).
- Committed build artifacts and logs (all UTF-16): `build_errors.txt`, `build_output.txt`, `error_log.txt`, `out.txt`, `dev_output.txt`, `eslint_report.json` (about 106 KB). They show the production build FAILED at the time (TypeScript errors such as a wrong import path `../../context/AuthContext` in `DashboardLayout.tsx`, unused imports/variables) [FACT build_errors.txt:1-4; build_output.txt]. The current source imports `../context/AuthContext` correctly (DashboardLayout.tsx:2), so these logs are stale [INFERRED]; whether the current tree passes `tsc` is [NOT DETERMINABLE] without running it. Visible possible TS issues: unused imports in `AIVulnerability.tsx` (e.g. `YAxis` is not imported now) cannot be confirmed statically.
- `frontend/.npm-cache/` (599 tracked files, about 88 MB on disk) is an npm cache committed by mistake [FACT git ls-files]. `frontend/src/data/naukri_jobs.csv` (about 52 MB) is a tracked byte-identical copy of `dataset/naukri_com-job_sample.csv` (same MD5 verified) and is unused (see D.6).

### D.2 App shell and routing

#### `src/main.tsx` (10 lines)
`createRoot(#root).render(<StrictMode><App/></StrictMode>)`; imports `index.css` [1-10].

#### `src/App.tsx` (46 lines)
- Wraps everything in `AuthProvider` and `BrowserRouter` [24-25].
- `ProtectedRoute({children})`: `isAuthenticated ? children : <Navigate to="/login" />` [15-20]; comment says it is a soft prototype check (no token validation).
- Route table [27-39]:

| Path | Element | Protected |
|---|---|---|
| `/` | `LandingPage` | no |
| `/login` | `Login` | no |
| `/register` | `Register` | no |
| `/dashboard` (layout) | `DashboardLayout` | yes |
| `/dashboard` (index) | `Overview` | yes |
| `/dashboard/hiring-trends` | `HiringTrends` | yes |
| `/dashboard/skills` | `SkillsIntelligence` | yes |
| `/dashboard/vulnerability` | `AIVulnerability` | yes |
| `/dashboard/worker` | `WorkerIntelligence` | yes |
| `/dashboard/reskilling` | `ReskillingPath` | yes |
| `/dashboard/chatbot` | `Chatbot` | yes |

No 404 route.

#### `src/context/AuthContext.tsx` (49 lines)
- State `user` (initially `null`) [14]. `useEffect` on mount reads `localStorage` keys `token` and `user` and, if both exist, `setUser(JSON.parse(userData))` [16-22]. `login(token, userData)` writes both keys and sets state [24-28]; `logout()` removes both and clears state [30-34]. `isAuthenticated = !!user` [37].
- `useAuth()` throws if used outside the provider [43-49].
- Race condition [INFERRED]: on a hard refresh of `/dashboard/...`, the first render has `user === null`, so `ProtectedRoute` redirects to `/login` before the effect restores the user; the user must log in again (the login page does not redirect authenticated users).
- The JWT itself is never decoded or validated client-side; expiry (24 h) is not handled; a 401 from the API is not intercepted anywhere.

#### `src/layout/DashboardLayout.tsx` (119 lines)
- `Sidebar` [14-82]: product name "Skills Mirage"; group "Core Intelligence" (Dashboard, Hiring Trends, Skills Intelligence, AI Vulnerability Index) and group "Worker Action" (Worker Analysis, Reskilling Paths, AI Chatbot) as `Link` lists with lucide icons; logout button calls `useAuth().logout` (does not navigate). No active-route highlighting.
- `TopBar` [84-101]: "System Live" badge, shows `user.name` (fallback "Administrator") and the static text "Hackathon Demo".
- `DashboardLayout` [103-117]: flex layout with sidebar, top bar, and `<Outlet/>` inside a `max-w-7xl` scroll container.
- `LandingPage.tsx` (84 lines): marketing page with nav (Login/Sign Up or Go to Dashboard depending on `isAuthenticated`), hero text ("Navigate the future of Workforce Intelligence"), CTA buttons and a three-card feature section (Market Signals, AI Vulnerability Index, Reskilling Paths). Static content.

### D.3 Auth pages
- `pages/auth/Login.tsx` (97 lines): controlled `email`/`password` form; `loginApi({email, password})`; on success `login(data.access_token, {name: email.split('@')[0], email})` and `navigate('/dashboard')` [20-25]. It does NOT call `/auth/me`, so the stored `user` is just the email prefix. Errors shown as the raw `Error.message` (format `HTTP <status>: <body text>`). Shows "Authenticating..." while loading.
- `pages/auth/Register.tsx` (115 lines): fields full name, email, password (no confirm, no strength rule); `signupApi({email, name, password})`; on success shows "Account created successfully" and navigates to `/login` after 1500 ms [21-28].

### D.4 API client: `src/services/api.ts` (248 lines)

- `API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'` [1].
- `fetchWithAuth(url, options)` adds `Authorization: Bearer <localStorage token>` when a token exists [3-10]. `toJson<T>(res)` throws `Error("HTTP <status>: <text or statusText>")` if `!res.ok`, else `res.json()` [12-18].
- Every API call the frontend makes:

| Function | Method + URL | Auth header | Body | Returned type (declared) | Used by |
|---|---|---|---|---|---|
| `getHiringTrendsApi` | GET `/dashboard/hiring-trends` | yes | | `any[]` | jobAnalytics -> Overview, HiringTrends |
| `getSkillGapApi` | GET `/dashboard/skill-gap` | yes | | `any[]` | SkillsIntelligence |
| `getSkillTrendsApi(year?)` | GET `/dashboard/skill-trends[?year=N]` | yes | | `{rising_skills, declining_skills}` | Overview, SkillsIntelligence |
| `getSkillTrendYearsApi` | GET `/dashboard/skill-trend-years` | yes | | `number[]` (reads `.years`) | Overview |
| `getVulnerabilityApi` | GET `/dashboard/vulnerability` | yes | | declared `any[]` (actually `{table, regions}`) | wrapper only (page uses raw fetch) |
| `getVulnerabilityRegionsApi` | GET `/dashboard/vulnerability-regions` | yes | | `any` | `getVulnerabilityRegions` wrapper (unused by pages) |
| `getDashboardStatsApi` | GET `/dashboard/stats` | yes | | `{total_jobs, top_city, most_in_demand_skill, most_common_role}` | Overview |
| `getLatestJobsApi` | GET `/dashboard/latest-jobs` | yes | | `any[]` | LatestJobs |
| `getTopCitiesApi` | GET `/dashboard/top-cities` | yes | | `any[]` | HiringTrends, DynamicInsights |
| `getIndustryDistributionApi` | GET `/dashboard/industry-distribution` | yes | | `any[]` | wrapper only (no page) |
| `getTopRolesApi` | GET `/dashboard/top-roles` | yes | | `any[]` | DynamicInsights |
| `getRoleDistributionApi(city)` | GET `/dashboard/city-role-distribution?city=` (URL-encoded) | yes | | `any[]` | DynamicInsights |
| `getCitySpreadApi(role)` | GET `/dashboard/role-city-distribution?role=` | yes | | `any[]` | DynamicInsights |
| `getScrapedJobsApi(refresh=true)` | GET `/dashboard/scraped-jobs?refresh=true|false` | yes | | `{total, jobs, scrape_error, scrape_stats}` | `refreshJobsData` -> Overview refresh button |
| `getWorkerProfileApi` | GET `/worker/profile` | yes | | `WorkerProfileResponse` | WorkerIntelligence |
| `analyzeWorkerApi(data)` | POST `/worker/profile` | yes | JSON `{job_role, city, years_of_experience, role_description, skills[]}` | `{parsed_profile, gemini_analysis}` | WorkerIntelligence |
| `chatbotQueryApi(data)` | POST `/chatbot/query` | yes | JSON `{worker_profile, question}` | `{response}` | Chatbot |
| `signupApi(data)` | POST `/auth/signup` | no | JSON `{email, name, password}` | `{message}` | Register |
| `loginApi(data)` | POST `/auth/login` | no | JSON `{email, password}` | `{access_token, token_type}` | Login |
| `getReskillingApi` | GET `/worker/reskilling` | yes | | `ReskillingResponse` | ReskillingPath |
| `generateReskillingApi` | POST `/worker/reskilling` | yes | none | `ReskillingResponse` | ReskillingPath |

- Never called by the frontend: `/auth/me`, all `/courses*` endpoints, `/scrape/courses`, `/dashboard/skill-gap` is used but `/dashboard/vulnerability-regions` is only wrapped.
- TypeScript types defined [20-31, 117-141, 148-156, 167-170, 199-236]: `ScrapedJob`, `WorkerAnalyzePayload`, `GeminiAnalysis {risk_score: number|null, risk_level, pivot_roles[], new_skills[], explanation, raw_response}`, `WorkerProfileResponse`, `WorkerAnalyzeResponse`, `ChatbotQueryPayload`, `RecommendedSkill`, `RecommendedCourse`, `RecommendedJob`, `LearningStep`, `ReskillingResponse {recommendation_type: 'upskilling'|'reskilling'|null, summary, recommended_skills[], recommended_courses[], recommended_jobs[], learning_path[], error}`.

#### `src/services/jobAnalytics.ts` (100 lines): thin adapters over api.ts
- `refreshJobsData()` triggers `getScrapedJobsApi(true)` (a live scrape) [19-22].
- `getDashboardSummary()` -> `{totalJobs, topCity, topSkill, topRole}` [24-32].
- `getHiringTrends()` maps `{month, job_count}` to `{name, value}` [34-41].
- `getTopSkills(year?)` maps rising skills to `{name, dev: parseInt(growth without '+') || 0}` [43-50] (so the "Top Skills Demand" chart actually shows trend growth, not demand).
- `getSkillTrends`, `getSkillTrendYears`, `getSkillGapApiWrapper`, `getVulnerabilityRows` pass through; `getVulnerabilityRegions()` converts `region_risks` map to a sorted array `{name, risk}` (unused) [68-76]; `getLatestJobs`, `getTopCities`, `getIndustryDistribution`, `getTopRoles`, `getRoleDistribution(city)`, `getCitySpread(role)` pass through.

### D.5 Pages

All dashboard pages use the same pattern: `useEffect` -> call service -> set state with a `mounted` guard -> show a loading text -> render Recharts charts or tables. Chart libraries: Recharts (`AreaChart, LineChart, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid`). Icons: lucide-react. Dark theme via Tailwind custom colors.

#### `Overview.tsx` (261 lines): route `/dashboard`
- State: `summary`, `hiringData`, `skillsData`, `skillYears`, `selectedSkillYear` (`number | 'all' | null`), `loading`, `isRefreshing`, `refreshTrigger` [71-78].
- On mount (parallel): `getDashboardSummary`, `getHiringTrends`, `getSkillTrendYears`; sets `selectedSkillYear` to `years[0]` (the newest year) or `'all'` [84-95]. Second effect on `selectedSkillYear` loads `getTopSkills(year or undefined)` [106-124]. Because the newest year is 2026, the default skills chart uses only the 2026 (scraped) rows (see E data facts).
- "Refresh Data" button [126-174]: awaits `refreshJobsData()` (blocking live Selenium scrape, can take a minute or more), reloads summary, hiring trends, years and top skills, then increments `refreshTrigger` so child widgets reload.
- UI: four `StatCard`s (Total Jobs Scraped with `toLocaleString()`, Top Hiring City, Most In Demand Skill, Most Common Role; static trend badges "Active/Leading/Rising/Popular", names title-cased with IT/AI/ERP/QA kept upper-case) [177-182]; "Hiring Trends Over Time" `AreaChart` (x = month name, y = job count, gradient fill) [185-209]; "Top Skills Demand" `BarChart` with a year `<select>` ("All years" + each year), x labels rotated -90 and truncated to 15 characters by `CustomOverviewTick` [211-252]; then `<LatestJobs refreshTrigger/>` and `<DynamicInsights refreshTrigger/>` [255-256].
- Stat-card color classes are built dynamically (`bg-${color}-500/10`), which Tailwind's JIT cannot detect unless the full class names appear elsewhere [INFERRED from Overview.tsx:52-53 and tailwind.config content scanning].

#### `LatestJobs.tsx` (86 lines) component
Prop `refreshTrigger`. Calls `getLatestJobs()` (50 newest by `postdate` string). Table columns: Job Title (`jobtitle`), Company, Location (`location || city || 'Unknown'`), Experience (`|| 'N/A'`), Skills (string), Posted Date (`postdate.split(' ')[0]`). Empty state "No scraped jobs available yet" [5-85]. Header says "Latest Scraped Jobs" although most rows come from the historical CSV.

#### `DynamicInsights.tsx` (224 lines) component
- Loads `getTopCities()` and `getTopRoles()` for two dropdowns, defaulting to the first city (`.name`) and first role (`.role`) [44-68].
- City selection effect -> `getRoleDistribution(selectedCity)` -> bar chart "Role Distribution" (`dataKey="value"`) [72-88]; role selection effect -> `getCitySpread(selectedRole)` -> bar chart "City Spread" [92-108]. Both effects re-run on `refreshTrigger`. Empty-state messages "No roles found for this city." / "No cities found for this role.". Custom rotated, 15-char truncated ticks.
- Mismatch to note [INFERRED]: roles in the dropdown come from `/dashboard/top-roles` (exact `title` strings) and the backend filter is an exact case-insensitive match, which works for these values.

#### `HiringTrends.tsx` (115 lines): route `/dashboard/hiring-trends`
- Loads `getHiringTrends()` and `getTopCities()` once [22-48]. Maps trends to `{name, jobs: value, active: Math.round(value * 0.8)}` (the "Estimated Active Roles" line is fabricated as 80% of postings) [32]. City names formatted by `formatCityName`: take the part before `/` or `,`; "delhi ncr"/"ncr" -> "Delhi NCR"; else capitalise first letter [8-14].
- Charts: dual-axis `LineChart` "Aggregate Job Postings" (left axis jobs, right axis active) and vertical `BarChart` "City Demand Comparison" (`dataKey="demand"`, bar size 24) [66-110]. An empty `<div>` placeholder where filters were meant to be (comment 26: filtering not implemented).

#### `SkillsIntelligence.tsx` (179 lines): route `/dashboard/skills`
- Loads `getSkillGapApiWrapper()` and `getSkillTrends()` (no year) [35-36]. Formats skill names (split on whitespace or `-`, title-case, keep IT/AI/ML/ERP/QA/AWS upper-case) [7-16].
- Gap data: filter `training_supply > 0`, add `visualization_supply = training_supply * 10`, sort by `market_demand` descending, keep 10 [41-50].
- UI: "Top Rising Skills" list (name + `growth` badge), "Top Declining Skills" list (name + `decline`), and "Market Skill Gap Map": grouped `BarChart` in a 2000 px wide scroll container with `market_demand` and `visualization_supply` bars (legend text "Companies Demand" / "Training Supply") [124-174]. The tooltip shows the raw skill; the supply bar is exaggerated 10x and labelled "Training Supply Index" [157-160].

#### `AIVulnerability.tsx` (174 lines): route `/dashboard/vulnerability`
- Does NOT use `services/api.ts`: it calls `fetch(<API base>/dashboard/vulnerability)` directly with the bearer token [38-46], logs the response, sets `rows = data.table` and `regionRows` = top 8 of `Object.entries(data.regions)` sorted by score descending [52-60]. No `catch` (only `finally`), and no `response.ok` check.
- UI: "Risk Assessment Table" (Job Role, City, AI Risk Score) with color/icon thresholds `>= 60` red, `>= 30` amber, else green [17-27, 96-106]; "Risk by Region" `AreaChart` (x = city, y = mean score, gradient `#f43f5e`) [113-135]; "Methodology" card with the formula text (Structural x 0.55, Hiring Trends x 0.20, AI Mention Rate x 0.15, Role Replacement x 0.10) and four structural factors (Vulnerability 30%, Repetition 25%, Complexity 20%, Human Factor 15%; the fifth, adaptability 10%, is not listed) and "normalized to a 5-95 scale" [137-167].

#### `WorkerIntelligence.tsx` (323 lines): route `/dashboard/worker`
- Form state `{title, city, experience, description, skills}` initialised from `localStorage['worker_form_draft']` and saved back on every change [20-39].
- On mount `getWorkerProfileApi()` OVERWRITES the form with backend values (`job_role`, `city`, `years_of_experience?.toString()`, `role_description`, `skills.join(', ')`) and sets `geminiAnalysis` from `profile.gemini_analysis` [42-63]. Because the backend returns `years_of_experience` from the signup value (None) rather than the saved `years_experience` (A.6 #1), the experience field is blank after reload [INFERRED].
- Submit: `analyzeWorkerApi({job_role, city, years_of_experience: Number(experience || 0), role_description, skills: comma-split, trimmed, non-empty})` -> `setGeminiAnalysis(res.gemini_analysis)`; errors shown inline [65-86]. All fields except skills are `required`.
- Display [92-307]: red dismissible banner if `risk_score > 85`; "AI Risk Assessment" card with level badge (high/moderate/low; unknown falls back to moderate styling), score `Math.round(risk_score)/100`, progress bar (width `clamp(0..100)`), explanation; "Recommended New Skills" chips; "Suggested Pivot Roles" numbered list; "Methodology" card showing a formula `(Automation Probability x 0.4) + (Skill Replaceability x 0.3) + (Task Repetition Level x 0.2) + (AI Tool Adoption Rate x 0.1)` [283-290]. This formula matches neither the backend vulnerability index nor the Gemini prompt formula (three different formulas exist in the product) [FACT WorkerIntelligence.tsx:285-290 vs worker_gemini.py:12 vs vulnerability_index.py:100-105].

#### `ReskillingPath.tsx` (270 lines): route `/dashboard/reskilling`
- On mount `getReskillingApi()`; only stores the result if `recommendation_type` is truthy [20-35]. "Generate/Regenerate" button calls `generateReskillingApi()` (POST), stores the result, shows `res.error` if present [37-49].
- Display when `recommendation_type` present [113-264]: badge (upskilling green, reskilling purple) + summary; "Recommended Skills" cards (skill chip + reason); "Learning Timeline" alternating vertical timeline (icons cycle through 5 lucide icons; first step "Start Here", last step check icon; shows `week`, `title`, `description`); "Recommended Courses" (name, source badge, duration, matched-skill chips, "Open" external link); "Recommended Jobs" (title, company, location, match reason, required-skill chips, index badge). Empty and loading states included.
- Note: courses' `duration` is always empty in practice because the backend sends an empty `duration` to Gemini (B.5).

#### `Chatbot.tsx` (123 lines): route `/dashboard/chatbot`
- State `messages` (id, role `user|assistant`, content), `input`, `isTyping`; auto-scroll on change [15-26].
- `handleSend`: appends the user message, calls `chatbotQueryApi({worker_profile: {}, question})` (the profile is always an empty object; personalisation relies on the server reading the user document), appends `res.response || 'No response.'`, or `Error: <message>` on failure [28-46]. Initial assistant message: "I'm the Skills Mirage Assistant. Ask about AI vulnerability, role transitions, or learning paths." Plain-text rendering (no markdown), though backend replies use markdown (`**Worker Analysis**`) [FACT query_router.py:73]. No conversation history is sent to the server (stateless per question).

### D.6 Unused / dead frontend code
- `utils/jobDataLoader.ts` (69 lines): Papa Parse of the bundled 52 MB CSV in the browser (maps `jobtitle`, `skills` set, `city`, `industry`, `experience`, `company`, `postdate`, `month`, `year`); `loadJobs()` is exported but never imported [FACT grep]. The CSV import `?url` still ships the 52 MB file in the repo. This is a leftover of an earlier client-side-analytics design [INFERRED].
- `App.css`, `tailwind.backup.js`, `react.svg`, `vite.svg`, wrappers `getIndustryDistribution`, `getVulnerabilityRows`, `getVulnerabilityRegions`, `refreshJobsData` partially, and unused dependencies (D.1).

### D.7 Frontend behaviours that matter for a reimplementation
1. Authentication: JWT in `localStorage['token']`, user object in `localStorage['user']`; bearer header on every protected call; no refresh, no 401 handling.
2. All analytics are computed server-side; the browser only renders. The frontend makes 1 to 5 API calls per page; the dashboard home triggers up to 8 calls (3 + 1 + 1 + 1 + 2 + 2).
3. The "Refresh Data" action is a synchronous scrape through the API.
4. Display-only fabrications: HiringTrends "Estimated Active Roles" (0.8 x), Overview static trend badges, Skills gap "supply x 10" scaling.
5. Names and labels the UI expects from the API are listed in D.4 and must be preserved or remapped.

## 7. Data

### 7.1 Files
| File | Size | Rows | Role |
|---|---|---|---|
| `dataset/naukri_jobs.csv` | 52.3 MB | 22,979 | Main jobs store read by `dataset_manager.py`; also rewritten after each scrape |
| `dataset/naukri_com-job_sample.csv` | 52.3 MB | 22,000 | Original sample dataset (2015-2017 Naukri postings); byte-identical to `frontend/src/data/naukri_jobs.csv` (same MD5) |
| `dataset/naukri_jobs_scraped.csv` | 229 KB | 775 | Snapshot of scraped 2026 rows (this is what `chat_data.db` `jobs` was built from: 775 rows, same date range) |
| `dataset/courses.csv` | 133 KB | 398 | Courses store (NPTEL 200, SWAYAM 198) |
| `data/courses_raw.json` | 232 KB | 398 | Backup written by the courses scraper (same schema, `skill_tags` as comma string, `syllabus_weeks` as JSON string) |
| `data/raw_jobs.json` | small | 40 | Last scrape output (list of dicts) |
| `data/courses.json`, `data/jobs_raw.json`, `data/jobs_processed.json`, `backend/config.py` etc. | 0 bytes | | empty placeholders |
| `backend/db/chat_data.db` | | courses 398, jobs 775 | SQLite used only by the chatbot data intent |

### 7.2 Jobs schema (14 columns, all strings in the app)
`company, education, experience, industry, jobdescription, jobid, joblocation_address, jobtitle, numberofpositions, payrate, postdate, site_name, skills, uniq_id`.
Non-null counts in `naukri_jobs.csv` (of 22,979): company 22,975; education 19,976; experience 22,973; industry 21,966; jobdescription 22,972; jobid 21,971; joblocation_address 22,476; jobtitle 22,977; numberofpositions 4,454; payrate 21,874; postdate 22,954; site_name 3,985; skills 22,448 (531 empty); uniq_id 21,971. Average description length 1,906 characters.
- Format notes: `skills` is a comma-separated string with no spaces after commas in many rows (e.g. `Excellent Negotiation Skills,Communication Skills,...`); `joblocation_address` is a comma-separated list of cities (first token = "city" in the app); top first-tokens: `Bengaluru/Bangalore` 5,902, `Mumbai` 3,881, `Bengaluru` 2,052 (so Bengaluru appears under two spellings); `experience` strings like `2-6 Yrs`; `postdate` like `2026-03-06 03:54:19 +0000`.
- Composition of the main file (computed by matching on jobtitle+company+postdate): 21,971 rows come from the original sample (years 2015 5,649; 2016 16,126; 2017 173) and about 1,006 rows are 2026 (774 from the scraped CSV at the top of the file plus 234 later rows dated 2026-03-06/07 appended at the bottom); 25 rows have no postdate. 2026-only rows are the ones with `industry`, `education`, `payrate`, `jobid` empty and with 84-character description snippets.
- Consequences [INFERRED from the code and these facts]: (a) the dashboard year dropdown defaults to 2026, i.e. about 1,006 rows; "All years" is dominated by 2015-2016 data; (b) the "latest jobs" (sorted by `postdate`) are scraped rows; (c) `compute_skill_trends` splits by row position, so the older half contains the 774 scraped rows from the top of the file mixed with 2015-2016 rows, and the newer half ends with the 234 later scraped rows, so "rising/declining skills" compare mixed-era halves and are not a real time trend.
- `naukri_jobs_scraped.csv` columns identical; only company, experience, jobdescription (84 chars avg), joblocation_address, jobtitle, postdate (16 distinct values), skills are filled.

### 7.3 Courses schema (9 columns)
`name, source (SWAYAM|NPTEL), domain (85 distinct), url, institution, duration_weeks (4.0 to 18.0, mean 11.43, 5 null), difficulty (UG 171, Undergraduate/Postgraduate 106, Undergraduate 57, Postgraduate 37, PG 20, UG/PG 6), skill_tags (comma-separated, average 2.3 tags, max 5), syllabus_weeks (JSON list; "[]" in 208 rows)`. About 61 rows contain the generic fallback tag "Research", consistent with the offline `update_course_skills.py` enrichment (C.3) having been run on this file [INFERRED]. `duration_weeks` is stored as a float string like `12.0`.

### 7.4 MongoDB
Database `skills_mirage_db`, collection `users`: documents as in A.9 (fields: email, name, bcrypt password, job_role, city, years_of_experience (signup) / years_experience (profile), role_description, skills[], risk_score (never set), gemini_risk_score, gemini_analysis{risk_score,risk_level,pivot_roles,new_skills,explanation,raw_response}, reasoning, reskilling_result{recommendation_type,summary,recommended_skills[],recommended_courses[],recommended_jobs[],learning_path[],raw_response,error}, created_at, updated_at, reskilling_updated_at). No indexes defined in code.

## 8. Key logic and algorithms (reimplementation specification)

### 8.1 Job record normalisation (`dataset_manager.get_all_jobs`)
For each CSV row (all fields strings): `skills` = parse list (literal-eval if it looks like a Python list, else split on commas, strip, drop empty); `city` = text before the first comma of `joblocation_address`, trimmed (`"Unknown"` if empty); `title` = `jobtitle`; `ai_mentions` = AI keywords found in lower-cased `jobdescription`, keywords `chatgpt, openai, generative ai, machine learning, automation, llm, gpt, ai tools`.

### 8.2 Dashboard statistics
- Stats: counts over all jobs; `top_city`, `most_in_demand_skill`, `most_common_role` = most frequent value (case-sensitive; empty strings count) or "N/A".
- Top cities (10), top roles (10, by exact `title`), top companies as "industry" (5), roles-by-city (10, case-insensitive city match), cities-by-role (10, case-insensitive role match). Output shapes in A.6.
- Hiring trend: group by the first 7 characters of `postdate` if they match `YYYY-MM`, else bucket "Recent"; sort by month string ascending.
- Skill trend: optional filter by `postdate` year; split the list in two halves by position (`mid = max(1, n//2)`); count skills per half (case-sensitive); change = recent - previous; sort descending; rising = top 10 with change > 0, declining = last 10 with change < 0.
- Skill gap: demand = job-skill counts (lower-cased); supply = course `skill_tags` counts (lower-cased); gap = demand - supply; top 10 by gap.

### 8.3 AI Vulnerability Index (per job, then averaged)
Constants and keyword lists are in B.4. Formula: `structural = 0.30*suscep + 0.25*repet + 0.20*(100-complex_raw) + 0.15*(100-human_raw) + 0.10*(100-adapt_raw)`; `final = clamp(0.55*structural + 0.20*0 + 0.15*ai_risk + 0.10*replace_risk, 5, 95)`; role score = rounded mean of final over all jobs of that lower-cased title; region score = rounded mean over jobs of that city (excluding "Unknown"). `/dashboard/vulnerability` returns up to 100 unique (role, city) rows sorted by role score and `regions` as the mean of those rows per city.

### 8.4 Worker risk and pivots (LLM, non-deterministic)
POST `/worker/profile` calls Gemini with title, city, years, skills; the prompt includes a formula and pivot logic but gives the model no data; the model returns JSON `{risk_score 0-100, risk_level, pivot_roles[], new_skills[], explanation}`. Stored as `gemini_analysis` and `gemini_risk_score`. A deterministic alternative (`risk_score.compute_worker_risk`: base role risk or 50, + 0.1 x region risk, - min(25, 2.5 x years), + 15 if under 1 year, clamp 5-95) exists but is unused.

### 8.5 Reskilling plan (LLM with retrieval)
Pool = user skills + Gemini new skills + Gemini pivot role names + top-10 rising skill names. Retrieve up to 30 courses by exact tag overlap (only 20 are sent) and up to 20 jobs by exact skill overlap (only 15 sent). Prompt = instruction block + profile + risk assessment + rising/declining lists + course JSON + job JSON. Rule inside the prompt: field demand increasing -> upskilling, decreasing -> reskilling (the model decides; no code computes demand direction). Response JSON schema in B.5. Persist the whole result in Mongo.

### 8.6 Chatbot routing
Lower-case substring intent classification: improvement keywords first, then risk keywords, else data query. Data query pipeline: DB schema text -> Gemini produces SQL -> strip fences -> blacklist check (DROP/DELETE/UPDATE/INSERT) -> execute on SQLite -> first 20 rows (max 3,000 characters) -> Gemini summarises in the user's language (English or Hindi). Risk/improvement intents build a prompt from the stored `gemini_analysis` / `reskilling_result`.

### 8.7 Scrapers
Jobs: Selenium, Naukri "jobs in india" pages 1-5, wait for card selectors, parse card fields, 1.5 s between pages, results get `postdate = now`. Courses: SWAYAM from seven Google Sheet tabs; NPTEL from a sheet tab of course IDs (fallback list of 49 IDs) and per-course preview pages; tag noise filters; weekly refresh with 50 per source, startup refresh if under 200 courses. Details in Part C.

### 8.8 Auth
bcrypt via passlib; JWT HS256, 24 h, payload `{user_id, email, exp}`; `get_current_user` reloads the user from Mongo on each call.

## 9. Data volume and processing locations (facts only)
| Where | What happens | Tool | Memory pattern | Trigger/frequency | Data touched |
|---|---|---|---|---|---|
| Backend import time | load jobs CSV and courses CSV | pandas `read_csv(dtype=str)` | whole file in RAM as strings | once per process | 22,979 rows x 14 cols (52 MB file) |
| Each dashboard request | convert all rows to dicts, parse skills/city/AI mentions | Python loops | full list rebuilt each call (no cache) | per request | all rows |
| `/dashboard/vulnerability*` | ~30 keyword substring scans per job, aggregation | Python loops | all rows | per request (twice if both endpoints called) | all rows |
| `/dashboard/skill-gap`, trends, stats, top-N | Counter aggregations | Python | all rows | per request | all rows; courses CSV re-read from disk each call |
| Reskilling | job/course matching by set overlap | Python loops | all jobs and courses | per user request | all rows |
| Scraping jobs | Selenium page loads, parse, CSV append and rewrite | Chrome + BS4 + pandas | whole frame rewritten by daemon thread | on demand (default on every `/scraped-jobs`) | about 100 new rows per run |
| Courses scrape | HTTP fetch and parse | requests + BS4 | small | startup if < 200 courses, weekly, manual | about 100 rows per run |
| Chatbot SQL | NL->SQL on SQLite | sqlite3 | up to 20 rows returned | per question | 398 + 775 rows |
| Gemini calls | 1 to 2 per user action | HTTPS | | per user action | prompts up to about 20 courses + 15 jobs |
Everything runs in one Python process on one machine; no queue, no batch precomputation, no distributed component.

## 10. Key flows
1. Signup/login: Register -> POST `/auth/signup` (insert user) -> Login -> POST `/auth/login` (verify bcrypt, issue JWT) -> `AuthContext.login` stores token and `{name: email prefix, email}` -> `/dashboard`.
2. Dashboard load (Overview): parallel GET `/dashboard/stats`, `/hiring-trends`, `/skill-trend-years`; then GET `/skill-trends?year=<newest>`; child widgets GET `/latest-jobs`, `/top-cities`, `/top-roles`, then `/city-role-distribution?city=<first>` and `/role-city-distribution?role=<first>`.
3. Refresh data: button -> GET `/dashboard/scraped-jobs?refresh=true` -> `run_scraper()` (blocking, Chrome pool of 3) -> `append_jobs` -> CSV rewrite -> frontend reloads widgets.
4. Worker analysis: form -> POST `/worker/profile` -> `parse_worker_profile` (3 keyword skills) -> merge skills -> `analyze_worker` (Gemini) -> `update_one($set..., upsert)` -> response `{parsed_profile, gemini_analysis}` -> UI cards.
5. Reskilling: POST `/worker/reskilling` -> `generate_reskilling_path` (skill trends + course/job matching + Gemini) -> store in Mongo -> UI timeline.
6. Chatbot: POST `/chatbot/query {worker_profile: {}, question}` -> fresh user doc -> `handle_query` -> intent route -> Gemini (+ SQLite) -> `{response}` text.
7. Course scrape: startup lifespan (if < 200 courses) and weekly job -> `run_courses_scraper` -> CSV append (dedupe name+source) + `data/courses_raw.json`.

## 11. Configuration, environment and run instructions
Documented steps [FACT README.md:37-94]: backend `cd backend`, create venv, `pip install -r requirements.txt`, ensure `.env` has MongoDB URI and Gemini key, `uvicorn main:app --reload` (port 8000); frontend `cd frontend`, `npm install`, set `VITE_API_BASE_URL`, `npm run dev` (port 5173).
Environment variables across the project:
| Variable | Used in | Required? |
|---|---|---|
| `MONGO_URI` | db/mongo.py | yes (no default) |
| `DATABASE_NAME` | db/mongo.py | no (`skills_mirage_db`) |
| `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_HOURS` | utils/jwt_handler.py | no (insecure default secret) |
| `GEMINI_API_KEY_WORKERANALYSIS` | worker_engine/worker_gemini.py | yes for worker analysis |
| `GEMINI_API_KEY_RESKILLING` | worker_engine/reskilling_engine.py | yes for reskilling |
| `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) | chatbot/gemini_client.py | yes for chatbot |
| `SCRAPER_*` (8 variables) | scrapers/naukri/naukri_scraper.py | no |
| `VITE_API_BASE_URL` | frontend/services/api.ts | no (fallback `http://localhost:8000`) |
README mentions only "MongoDB URI, Gemini API key"; the code needs three separate Gemini keys. No `backend/.env.example` exists (only `frontend/.env.example`).
Run-time prerequisites not in the README: Google Chrome installed for scraping; Python 3.10+; a reachable MongoDB; internet access for Gemini, Google Sheets, nptel, naukri; `dataset/*.csv` present (they are committed). First start: `main.py` triggers a background course scrape if `courses.csv` has fewer than 200 rows (it has 398, so no).
Undocumented: the `init_db.py` step to build `chat_data.db` (a DB is committed); how to run tests (none automated).

## 12. Fragile, missing or inconsistent
Security:
- Default JWT secret `supersecretsaxkey` in code [jwt_handler.py:18]; no password policy; CORS fixed to localhost; no rate limiting; unauthenticated endpoints include `GET /dashboard/scraped-jobs` (launches Chrome scraping on every call by default), `POST /scrape/courses`, and all `/dashboard/*`.
- Chatbot passes the full user document (including the password hash) to `handle_query`; the SQL guard is a substring blacklist on a read-write connection; Gemini error text is executed as SQL when the API fails (reproduced in committed `backend/out.txt`).
- Tokens in `localStorage`; no 401 handling; page refresh logs the user out (race in `AuthContext`).
Data model bugs: `years_of_experience` vs `years_experience`; `risk_score` never written; `reskilling_path` read but never written (A.6).
Logic issues: `hiring_risk` hard-coded 0; skill "trend" compares row halves of a mixed-era CSV; scrape-time stored as `postdate` so duplicate jobs re-insert each run; two spellings of Bengaluru; role names mixed into skill matching; course `duration` always empty in prompts; three conflicting risk formulas (UI, Gemini prompt, backend index).
Repo hygiene: 599 committed `.npm-cache` files (88 MB), three copies of a 52 MB CSV (`dataset/naukri_jobs.csv`, `dataset/naukri_com-job_sample.csv`, `frontend/src/data/naukri_jobs.csv` which is byte-identical to the sample), committed SQLite DB, UTF-16 logs, empty placeholder files (`backend/config.py`, `backend/db/database.py`, `backend/db/models.py`, `backend/utils/city_mapper.py`, `role_normalizer.py`, `skill_taxonomy.py`, `backend/pipeline/ai_signal_detector.py`, `data/courses.json`, `jobs_raw.json`, `jobs_processed.json`, `context.md`), a root `package-lock.json` without a package.json, unused deps (`scikit-learn`, `numpy`, `clsx`, `tailwind-merge`, `d3-scale`, `react-simple-maps`), the Vite template title/CSS left in place, stale build logs showing a failed build.
Reliability: Gemini calls have no timeout/retry; scraper depends on fragile CSS selectors and a specific Chrome; Google Sheet ID and tab gids hard-coded; `users_collection = None` on connection error is not handled; per-request O(N) processing; first-use import side effects (CSV load, `basicConfig`) at module import.
Docs mismatch: README says "asynchronous web scraping modules" and "heatmaps"; the code is synchronous and has no heatmap or map component; README says the DB stores "authentication tokens" (it does not).

## 13. Weaknesses and improvement candidates (candidates only; no selection made)
| # | Weakness (evidence) | Why it matters | Effort |
|---|---|---|---|
| W1 | All analytics recomputed per request in one process over a 52 MB CSV loaded in RAM (B.9) | Latency and memory grow with data; cannot scale or parallelise | high |
| W2 | Scraping runs inside the API request and rewrites the whole CSV (C.1, B.1) | Blocking, fragile, data races; no history | med |
| W3 | Skill "trend" is a positional half-split of mixed-era data (B.4, E 7.2) | The headline "rising/declining skills" is not a real time trend | med |
| W4 | `postdate` for scraped rows is scrape time (A.7) | Corrupts monthly trends and dedupe | low |
| W5 | Vulnerability index is keyword counting with a dead 20% weight (B.4) | Low explanatory value; inconsistent with the LLM score | med |
| W6 | Worker risk comes from an LLM with no grounding data and three conflicting formulas (B.5, D.5) | Non-reproducible scores | med |
| W7 | Courses and jobs matched only by exact string equality (B.5) | Poor recommendations | med |
| W8 | Data-model inconsistencies in Mongo (A.6) | Visible UI bugs (blank experience, null risk) | low |
| W9 | Security gaps (E 12) | Unsafe for any real deployment | low-med |
| W10 | No tests, no CI, floating dependencies, no `.env.example` for the backend | Hard to reproduce | low |
| W11 | Duplicated stores (two course readers, three CSV copies, SQLite copy of jobs) | Inconsistent data views | med |
| W12 | No real-time or streaming ingestion; no job de-duplication across runs | Data quality | med |
| W13 | Chatbot NL-to-SQL is unsafe and fails open (E 12) | Reliability and safety | low-med |
These are candidates only; the team decides later (decision #4 in HOW_WE_WORK.md).

## 14. Component inventory
| ID | Component | Path(s) | Purpose |
|---|---|---|---|
| C01 | FastAPI app and scheduler | `backend/main.py` | app, CORS, routers, weekly course job |
| C02 | Auth router and JWT | `backend/api/auth_routes.py`, `backend/utils/jwt_handler.py` | signup, login, current user |
| C03 | MongoDB client | `backend/db/mongo.py` | users collection |
| C04 | Dashboard router | `backend/api/dashboard_routes.py` | 14 analytics endpoints |
| C05 | Jobs store | `backend/data/dataset_manager.py` | in-memory jobs/courses frames, append, save |
| C06 | Courses store | `backend/data/courses_dataset.py` | courses frame, queries, stats |
| C07 | Hiring and skill analytics | `backend/intelligence/hiring_trends.py`, `skill_trends.py` | monthly counts, skill trend, skill gap |
| C08 | Vulnerability index | `backend/intelligence/vulnerability_index.py` | keyword risk scoring |
| C09 | Worker router | `backend/api/worker_routes.py` | profile and reskilling endpoints |
| C10 | Worker parser | `backend/worker_engine/worker_parser.py` | 3-keyword skill extraction |
| C11 | Gemini worker risk | `backend/worker_engine/worker_gemini.py` | LLM risk, pivots, skills |
| C12 | Reskilling engine | `backend/worker_engine/reskilling_engine.py` | retrieval + LLM plan |
| C13 | Legacy risk formula | `backend/worker_engine/risk_score.py` | unused deterministic score |
| C14 | Chatbot router and clients | `backend/api/chatbot_routes.py`, `backend/chatbot/*.py` | intents, NL->SQL, Gemini |
| C15 | SQLite chat DB | `backend/db/chat_data.db`, `backend/db/init_db.py` | courses/jobs tables for the chatbot |
| C16 | Naukri scraper | `backend/scrapers/naukri/*`, `backend/scrapers/utils/selenium_client.py` | Selenium job scraping |
| C17 | Job pipeline helpers | `backend/pipeline/job_cleaner.py`, `skill_extractor.py`, `backend/pipelines/job_pipeline.py` | normalise scraped jobs |
| C18 | Course scrapers | `backend/scrapers/courses/*` | SWAYAM sheets and NPTEL pages |
| C19 | Course skill enrichment | `dataset/update_course_skills.py` | offline tag assignment |
| C20 | Datasets | `dataset/*.csv`, `data/*.json` | jobs and courses data |
| C21 | Courses router | `backend/api/courses_routes.py` | 5 course endpoints |
| C22 | Frontend shell | `frontend/src/App.tsx`, `main.tsx`, `context/AuthContext.tsx`, `layout/DashboardLayout.tsx` | routing, auth state, layout |
| C23 | Frontend API layer | `frontend/src/services/*` | fetch wrappers and adapters |
| C24 | Dashboard pages | `Overview`, `HiringTrends`, `SkillsIntelligence`, `AIVulnerability`, `LatestJobs`, `DynamicInsights` | charts and tables |
| C25 | Worker pages | `WorkerIntelligence`, `ReskillingPath`, `Chatbot` | worker UI |
| C26 | Auth and landing pages | `LandingPage`, `auth/Login`, `auth/Register` | public pages |
| C27 | Test and log scripts | `backend/test_*.py`, `*.txt` logs | manual checks |

## 15. Not determined / open questions
- [NOT DETERMINABLE] Whether the current frontend passes `tsc`/`vite build` (committed logs are stale).
- [NOT DETERMINABLE] Real Naukri/Google Sheet availability and whether selectors still match today.
- [NOT DETERMINABLE] Gemini output quality, rate limits and cost (committed log shows a 429 quota error for an older model name).
- [NOT DETERMINABLE] MongoDB hosting details beyond the "Atlas" log text; Python and Node versions used.
- Question: did `naukri_jobs.csv` get its 234 non-sample rows from a second scrape that was appended (consistent with `append_jobs`)? [INFERRED yes]
- Question for the team: licence status of the reference (none found) and of the underlying Naukri 2015-2017 dataset (provenance not stated in the repo).
