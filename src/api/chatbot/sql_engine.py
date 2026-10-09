"""SQL engine for the chatbot: lazy Spark session, SQL validation and safe execution."""
import threading
import time
import re
import os
from typing import List, Tuple, Dict, Any

from src.common.spark_session import get_spark
from src.common.config import get_path
from src.common.logging_setup import get_logger

logger = get_logger("sql_engine")

_session = None
_lock = threading.RLock()
_status = "idle"

def is_started() -> bool:
    """Check if the Spark session is currently started."""
    with _lock:
        return _session is not None

def warmup_status() -> str:
    """Return the warm-up status: idle, running, ready, failed or disabled."""
    with _lock:
        return _status

def set_warmup_disabled():
    """Mark the warm-up as disabled (CHATBOT_WARMUP turned it off)."""
    global _status
    with _lock:
        _status = "disabled"

def warm_up_enabled() -> bool:
    """Return False when CHATBOT_WARMUP is 0, false, no or off (default: on)."""
    val = os.environ.get("CHATBOT_WARMUP", "1").strip().lower()
    if val in ("0", "false", "no", "off"):
        return False
    return True

def _warm_up_worker():
    """Build the Spark session in the background; log the outcome and never raise."""
    global _status
    logger.info("Chatbot warm-up started")
    start_t = time.time()
    try:
        get_session()
        elapsed = time.time() - start_t
        with _lock:
            _status = "ready"
        logger.info(f"Chatbot warm-up finished in {elapsed:.2f} s")
    except Exception as e:
        with _lock:
            _status = "failed"
        logger.error(f"Chatbot warm-up failed: {str(e)}")

def warm_up() -> threading.Thread | None:
    """Start the background warm-up thread; return it, or None when not needed."""
    global _status
    with _lock:
        if _session is not None or _status == "running":
            return None
        _status = "running"
        t = threading.Thread(target=_warm_up_worker, name="chatbot-warmup", daemon=True)
        t.start()
        return t

def get_session():
    """Lazily initialize and return the Spark session with temp views."""
    global _session
    with _lock:
        if _session is not None:
            return _session
            
        start_time = time.time()
        session = get_spark("chatbot_sql")
        
        try:
            # Create temp views
            jobs_path = get_path("processed/jobs")
            courses_path = get_path("processed/courses")
            
            jobs_df = session.read.parquet(str(jobs_path))
            jobs_df.createOrReplaceTempView("raw_jobs")
            session.sql("""
                CREATE OR REPLACE TEMP VIEW jobs AS 
                SELECT company, education, experience, industry, jobdescription, jobid, joblocation_address, jobtitle, numberofpositions, payrate, postdate, site_name, concat_ws(',', skills) AS skills, uniq_id
                FROM raw_jobs
            """)
            
            courses_df = session.read.parquet(str(courses_path))
            courses_df.createOrReplaceTempView("raw_courses")
            session.sql("""
                CREATE OR REPLACE TEMP VIEW courses AS 
                SELECT name, source, domain, url, institution, duration_weeks, difficulty, concat_ws(', ', skill_tags) AS skill_tags, to_json(syllabus_weeks) AS syllabus_weeks
                FROM raw_courses
            """)
            
            _session = session
            elapsed = time.time() - start_time
            logger.info(f"Chatbot Spark session started in {elapsed:.2f} seconds.")
            return _session
        except Exception as e:
            try:
                session.stop()
            except:
                pass
            raise

def shutdown():
    """Stop the Spark session safely."""
    global _session, _status
    with _lock:
        if _session is not None:
            old_session = _session
            _session = None
            try:
                old_session.stop()
            except Exception as e:
                logger.warning(f"Error stopping Spark session: {str(e)}")
        _status = "idle"

def schema_text() -> str:
    """Return the schema descriptions for the LLM prompt."""
    return (
        "jobs(company STRING, education STRING, experience STRING, industry STRING, jobdescription STRING, jobid STRING, joblocation_address STRING, jobtitle STRING, numberofpositions STRING, payrate STRING, postdate STRING, site_name STRING, skills STRING, uniq_id STRING)\n"
        "courses(name STRING, source STRING, domain STRING, url STRING, institution STRING, duration_weeks INT, difficulty STRING, skill_tags STRING, syllabus_weeks STRING)\n"
        "Notes: 'skills' is a comma-separated string. 'postdate' looks like '2026-03-06 03:54:19 +0000'. 'duration_weeks' is an integer in weeks."
    )

def clean_sql(text: str) -> str:
    """Clean the SQL string from LLM formatting."""
    text = text.strip()
    # Remove markdown code fences
    text = re.sub(r'^```[a-zA-Z]*\n', '', text)
    text = re.sub(r'\n```$', '', text)
    text = text.strip()
    
    # Remove trailing semicolons and whitespace
    text = re.sub(r';+\s*$', '', text)
    text = text.strip()
    return text

def validate_sql(sql: str) -> bool:
    """Validate the SQL query for safety restrictions."""
    if not sql:
        return False
        
    sql_upper = sql.upper().strip()
    if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
        return False
        
    if ";" in sql:
        return False
        
    # Check for disallowed formats in path references
    path_regex = r"\b(parquet|csv|json|orc|text|avro|jdbc|binaryfile|delta)\b`?\s*\.\s*`"
    if re.search(path_regex, sql, re.IGNORECASE):
        return False
        
    # Check for Java reflection calls
    reflect_regex = r'\b(reflect|java_method|try_reflect)\s*\('
    if re.search(reflect_regex, sql, re.IGNORECASE):
        return False
        
    return True

def _normalize_path(p: str) -> str:
    """Normalise a file URI or path for prefix comparison."""
    p = p.replace('\\', '/')
    if p.startswith('file:///'):
        p = p[8:]
    elif p.startswith('file:/'):
        p = p[6:]
    p = p.lower()
    return p.rstrip('/')

def check_input_files(df) -> bool:
    """Verify that all input files belong to the allowed directories."""
    files = df.inputFiles()
    if not files:
        return True
        
    allowed_jobs = _normalize_path(str(get_path("processed/jobs")))
    allowed_courses = _normalize_path(str(get_path("processed/courses")))
    
    for f in files:
        norm_f = _normalize_path(f)
        if not (norm_f == allowed_jobs or norm_f.startswith(allowed_jobs + "/") or
                norm_f == allowed_courses or norm_f.startswith(allowed_courses + "/")):
            return False
            
    return True

def run_query(sql: str) -> Tuple[List[Dict[str, Any]], int, bool]:
    """Execute the SQL query securely and return the results."""
    with _lock:
        session = get_session()
        df = session.sql(sql)
        
        if not check_input_files(df):
            raise PermissionError("blocked")
            
        rows = df.limit(1001).collect()
        total = min(len(rows), 1000)
        more_than_1000 = len(rows) > 1000
        
        results = [row.asDict(recursive=True) for row in rows[:20]]
        return results, total, more_than_1000