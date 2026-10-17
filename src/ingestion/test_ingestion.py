"""Tests for the ingestion parsers, storage and enrichment (run: pytest src/ingestion)."""
import json
from datetime import datetime, timezone

from src.ingestion import storage
from src.ingestion.course_parsers import clean_tags, nptel_ids_from_sheet, parse_nptel_preview, parse_swayam_tab
from src.ingestion.enrich_course_skills import enrich, load_job_skills, match_skills
from src.ingestion.naukri_parser import parse_jobs

CARD = """
<div class="srp-jobtuple-wrapper">
  <a class="title" href="https://www.naukri.com/job-1">Data Analyst</a>
  <a class="comp-name">Acme</a>
  <span class="locWdth">Pune, Mumbai</span>
  <span class="expwdth">2-5 Yrs</span>
  <span class="job-desc">Analyse data...</span>
  <ul><li class="tag-li">SQL</li><li class="tag-li">Excel</li></ul>
</div>
<div class="srp-jobtuple-wrapper"><span class="locWdth">No title here</span></div>
"""


def test_parse_jobs_fields_and_skip_untitled():
    jobs = parse_jobs(CARD, datetime(2026, 3, 7, 6, 48, 45, tzinfo=timezone.utc))
    assert len(jobs) == 1
    j = jobs[0]
    assert j["jobtitle"] == "Data Analyst" and j["company"] == "Acme"
    assert j["joblocation_address"] == "Pune, Mumbai" and j["experience"] == "2-5 Yrs"
    assert j["skills"] == "SQL,Excel"
    assert j["postdate"] == j["scraped_at"] == "2026-03-07 06:48:45 +0000"
    assert j["job_url"] == "https://www.naukri.com/job-1"


def test_parse_jobs_no_cards():
    assert parse_jobs("<html><body>nothing</body></html>") == []


def test_clean_tags_filters_noise_and_dedupes():
    tags = clean_tags(["Python", "python", "ab", "This course is for everyone", "etc", "http://x.y", "Machine Learning"])
    assert tags == ["Python", "Machine Learning"]


NPTEL = """
<html><body><h1>Intro to Python</h1><p>By Prof A | IIT Madras</p>
<table><tr><td>Category</td><td><ul><li>Computer Science</li><li>Programming</li></ul></td></tr>
<tr><td>Duration</td><td>12 weeks</td></tr><tr><td>Level</td><td>UG/PG</td></tr></table>
<p>INTENDED AUDIENCE: Students, Engineers</p><p>Week 1: Basics</p><p>Week 2: Loops</p></body></html>
"""


def test_parse_nptel_preview():
    c = parse_nptel_preview(NPTEL, "noc25_cs01")
    assert c is not None
    assert c["name"] == "Intro to Python" and c["source"] == "NPTEL"
    assert c["institution"] == "IIT Madras" and c["domain"] == "Computer Science"
    assert c["duration_weeks"] == 12 and c["difficulty"] == "UG/PG"
    assert c["url"].endswith("/noc25_cs01/preview")
    assert "Programming" in c["skill_tags"] and "Engineers" in c["skill_tags"]
    assert json.loads(c["syllabus_weeks"]) == ["Week 1: Basics", "Week 2: Loops"]


def test_parse_nptel_preview_without_title():
    assert parse_nptel_preview("<html></html>", "x") is None


def test_nptel_ids_dedupe_in_order():
    text = "a nptel.ac.in/noc24_ab01/preview b noc25_cs02 c noc24_ab01"
    assert nptel_ids_from_sheet(text) == ["noc24_ab01", "noc25_cs02"]


SHEET = (
    "junk row\n"
    "Course Title,Discipline,University/Institute,Level,Duration,Industry Sectors,Preview URL\n"
    "Intro to Marketing,Management,IIM B,PG,8 weeks,Retail; FMCG,https://swayam.gov.in/c1/preview\n"
    "ab,Skip,X,UG,1,,\n"
)


def test_parse_swayam_tab():
    rows = parse_swayam_tab(SHEET, "IIMB")
    assert len(rows) == 1
    c = rows[0]
    assert c["name"] == "Intro to Marketing" and c["duration_weeks"] == 8 and c["difficulty"] == "PG"
    assert c["url"] == "https://swayam.gov.in/c1/preview" and c["institution"] == "IIM B"
    assert "Management" in c["skill_tags"] and "Retail" in c["skill_tags"]


def test_parse_swayam_tab_no_header():
    assert parse_swayam_tab("a,b\n1,2\n", "CEC") == []


def test_enrich_and_matching(tmp_path):
    jobs = tmp_path / "jobs.csv"
    jobs.write_text('skills\n"SQL,Python,Machine Learning"\n"c,R,x"\n', encoding="utf-8")
    skills = load_job_skills(jobs)
    assert "x" not in skills and "c" in skills and skills[0] == "machine learning"
    assert match_skills("Python for SQL and machine learning", skills) == ["Machine Learning", "Python", "Sql"]
    assert match_skills("Cricket", skills) == []  # 'c' only matches as a whole word
    assert enrich({"name": "Applied Economics", "domain": ""}, skills)["skill_tags"] == "Data Analysis, Economics, Research"
    assert enrich({"name": "Zzz", "domain": "Qqq"}, skills)["skill_tags"] == "Analytical Skills, Communication Skills, Research"


def test_storage_dedupe_across_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "local_folder", lambda name: tmp_path / name)
    rows = [{"jobtitle": "A", "company": "B", "joblocation_address": "C"}]
    out = storage.run_folder("raw/scraped_jobs", "2026-10-01") / "jobs.jsonl"
    assert storage.write_jsonl(out, rows) == 1
    keys = storage.existing_keys("raw/scraped_jobs", "jobs.jsonl", storage.job_key)
    assert storage.job_key({"jobtitle": " a ", "company": "B", "joblocation_address": "c"}) in keys
