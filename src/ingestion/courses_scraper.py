"""Fetch SWAYAM and NPTEL course data and store one dated run under raw/scraped_courses.

The course list lives in a published Google Sheet whose address is NOT in the repo
(the reference hard-coded it). Provide it through the environment:
    COURSES_SHEET_BASE_URL   e.g. https://docs.google.com/spreadsheets/d/e/<id>/pub
    COURSES_SWAYAM_TABS      e.g. CEC:111,IIMB:222  (coordinator:gid pairs)
    COURSES_NPTEL_TAB        gid of the NPTEL id tab
Usage: python -m src.ingestion.courses_scraper [--max-per-source 50]
"""
import argparse
import os
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.common.logging_setup import get_logger  # noqa: E402
from src.ingestion.course_parsers import nptel_ids_from_sheet, parse_nptel_preview, parse_swayam_tab  # noqa: E402
from src.ingestion.storage import course_key, existing_keys, run_folder, write_jsonl  # noqa: E402

logger = get_logger("courses_scraper")
TIMEOUT = 15
NPTEL_DELAY = 0.6


def get_text(url: str, retries: int = 3) -> str | None:
    """GET a URL with retries; None when every attempt fails."""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0 (course-ingestion)"})
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as exc:
            logger.warning("GET failed (%d/%d) %s: %s", attempt, retries, url, exc)
            time.sleep(1.5)
    return None


def sheet_url(base: str, gid: str) -> str:
    """CSV export URL of one tab of a published sheet."""
    return f"{base.rstrip('/')}?gid={gid}&single=true&output=csv"


def scrape_swayam(base: str, tabs: str, limit: int) -> list[dict]:
    """Scrape SWAYAM tabs in order until ``limit`` unique courses are collected."""
    seen: set[str] = set()
    out: list[dict] = []
    for pair in filter(None, (p.strip() for p in tabs.split(","))):
        coordinator, _, gid = pair.partition(":")
        text = get_text(sheet_url(base, gid))
        if text is None:
            continue
        for c in parse_swayam_tab(text, coordinator):
            if c["name"].lower() not in seen:
                seen.add(c["name"].lower())
                out.append(c)
        if len(out) >= limit:
            break
    return out[:limit]


def scrape_nptel(base: str, gid: str, limit: int) -> list[dict]:
    """Scrape NPTEL preview pages for the ids listed in the sheet tab."""
    text = get_text(sheet_url(base, gid))
    ids = nptel_ids_from_sheet(text or "")[:limit]
    out: list[dict] = []
    for cid in ids:
        time.sleep(NPTEL_DELAY)
        html = get_text(f"https://onlinecourses.nptel.ac.in/{cid}/preview")
        course = parse_nptel_preview(html, cid) if html else None
        if course:
            out.append(course)
    return out


def main() -> None:
    """Command-line entry point."""
    ap = argparse.ArgumentParser(description="Scrape SWAYAM and NPTEL courses")
    ap.add_argument("--max-per-source", type=int, default=50)
    args = ap.parse_args()
    base = os.environ.get("COURSES_SHEET_BASE_URL", "")
    if not base:
        logger.error("FAIL: COURSES_SHEET_BASE_URL is not set (see the module docstring)")
        sys.exit(1)
    courses: list[dict] = []
    if os.environ.get("COURSES_SWAYAM_TABS"):
        courses += scrape_swayam(base, os.environ["COURSES_SWAYAM_TABS"], args.max_per_source)
    if os.environ.get("COURSES_NPTEL_TAB"):
        courses += scrape_nptel(base, os.environ["COURSES_NPTEL_TAB"], args.max_per_source)
    seen = existing_keys("raw/scraped_courses", "courses.jsonl", course_key)
    fresh = []
    for c in courses:
        if course_key(c) not in seen:
            seen.add(course_key(c))
            fresh.append(c)
    out = run_folder("raw/scraped_courses") / "courses.jsonl"
    logger.info("Wrote %d new courses (%d fetched) to %s", write_jsonl(out, fresh), len(courses), out)


if __name__ == "__main__":
    main()
