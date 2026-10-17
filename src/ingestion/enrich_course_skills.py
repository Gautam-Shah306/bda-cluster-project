"""Assign job-market skill tags to courses (reimplements reference C19, deterministic).

For each course the text ``name + domain`` is searched for known job skills (taken from
the jobs CSV): short skills (<= 4 chars) match on word boundaries, longer ones as
substrings. Courses with no match get tags from a keyword table, else a generic trio.
Unlike the reference, tags are written in a fixed order (sorted), not set order.

Usage: python -m src.ingestion.enrich_course_skills --courses IN.jsonl --jobs-csv JOBS.csv --out OUT.jsonl
"""
import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.common.logging_setup import get_logger  # noqa: E402
from src.ingestion.storage import read_jsonl, write_jsonl  # noqa: E402

logger = get_logger("enrich_course_skills")
SHORT_ALLOWED = {"c", "r", "java", "sql", "css", "html"}
GENERIC_TAGS = ["Research", "Communication Skills", "Analytical Skills"]
# Our own keyword table (the reference's exact mapping is not in the analysis).
KEYWORD_TAGS: dict[str, list[str]] = {
    "cyber": ["Cyber Security", "Network Security", "Risk Management"],
    "eco": ["Economics", "Data Analysis", "Research"],
    "commerce": ["Accounting", "Finance", "Business Development"],
    "psych": ["Psychology", "Counselling", "Research"],
    "math": ["Mathematics", "Statistics", "Analytical Skills"],
    "bio": ["Biology", "Research", "Laboratory Skills"],
    "film": ["Video Editing", "Content Creation", "Creative Writing"],
    "politi": ["Policy Analysis", "Research", "Communication Skills"],
    "histor": ["Research", "Writing", "Critical Thinking"],
    "hindi": ["Hindi", "Communication Skills", "Writing"],
}


def load_job_skills(jobs_csv: Path) -> list[str]:
    """Unique lower-cased job skills (length > 1 or in the short allow-list), longest first."""
    skills: set[str] = set()
    with jobs_csv.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            for s in (row.get("skills") or "").split(","):
                s = s.strip().lower()
                if len(s) > 1 or s in SHORT_ALLOWED:
                    skills.add(s)
    return sorted(skills, key=lambda s: (-len(s), s))


def match_skills(text: str, skills: list[str]) -> list[str]:
    """Skills found in ``text`` (word-boundary match when short, substring otherwise)."""
    text = text.lower()
    found = []
    for s in skills:
        if len(s) <= 4:
            if re.search(rf"\b{re.escape(s)}\b", text):
                found.append(s.title())
        elif s in text:
            found.append(s.title())
    return found


def enrich(course: dict, skills: list[str]) -> dict:
    """Return a copy of a course with ``skill_tags`` replaced by the enrichment result."""
    text = f"{course.get('name', '')} {course.get('domain', '')}"
    tags = match_skills(text, skills)
    if not tags:
        low = text.lower()
        for key, mapped in KEYWORD_TAGS.items():
            if key in low:
                tags = mapped
                break
    if not tags:
        tags = GENERIC_TAGS
    out = dict(course)
    out["skill_tags"] = ", ".join(sorted(set(tags)))
    return out


def main() -> None:
    """Command-line entry point."""
    ap = argparse.ArgumentParser(description="Enrich scraped courses with job skills")
    ap.add_argument("--courses", type=Path, required=True)
    ap.add_argument("--jobs-csv", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.resolve() == args.courses.resolve():
        logger.error("FAIL: --out must differ from --courses (write a new file, then review)")
        sys.exit(1)
    skills = load_job_skills(args.jobs_csv)
    rows = [enrich(c, skills) for c in read_jsonl(args.courses)]
    logger.info("Enriched %d courses using %d job skills -> %s", write_jsonl(args.out, rows), len(skills), args.out)


if __name__ == "__main__":
    main()
