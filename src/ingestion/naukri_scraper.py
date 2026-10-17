"""Scrape Naukri.com search pages with headless Chrome and store one dated run.

Usage (repo root, Chrome installed, ``pip install -r requirements-ingestion.txt``):
    python -m src.ingestion.naukri_scraper [--pages 5] [--city india] [--headed]

Environment: SCRAPER_MAX_PAGES, SCRAPER_CITY, SCRAPER_HEADLESS (0 to show the browser).
Scraping a site may be restricted by its terms of service (open question 19 in the
handoff); run it sparingly and respect the delays below.
"""
import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.common.logging_setup import get_logger  # noqa: E402
from src.ingestion.naukri_parser import parse_jobs  # noqa: E402
from src.ingestion.storage import existing_keys, job_key, run_folder, write_jsonl  # noqa: E402

logger = get_logger("naukri_scraper")

CARD_WAIT = "div.cust-job-tuple, div.srp-jobtuple-wrapper"
PAGE_DELAY_SECONDS = 1.5
BLOCK_HINTS = ("captcha", "verify you are human", "access denied", "unusual traffic", "security check")


def page_urls(city: str, page: int) -> list[str]:
    """Candidate URLs for one results page, tried in order until one has cards."""
    base = "https://www.naukri.com"
    if city in ("india", "all"):
        if page == 1:
            return [f"{base}/jobs", f"{base}/jobs-in-india?k=jobs&l=india&pageNo=1"]
        return [f"{base}/jobs-in-india?k=jobs&l=india&pageNo={page}", f"{base}/jobs-{page}"]
    if page == 1:
        return [f"{base}/jobs-in-{city}", f"{base}/jobs-in-{city}?k=jobs&l={city}&pageNo=1"]
    return [f"{base}/jobs-in-{city}?k=jobs&l={city}&pageNo={page}", f"{base}/jobs-in-{city}-{page}"]


def make_driver(headless: bool):
    """Create a Chrome driver (imported lazily so parsing tests need no Selenium)."""
    from selenium import webdriver

    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    for arg in ("--no-sandbox", "--disable-dev-shm-usage", "--window-size=1920,1080", "--disable-gpu"):
        opts.add_argument(arg)
    opts.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    return webdriver.Chrome(options=opts)


def fetch_html(driver, url: str, timeout: int = 10) -> str:
    """Load a URL and wait for job cards; return the page source either way."""
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    driver.get(url)
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, CARD_WAIT)))
    except TimeoutException:
        logger.warning("No job cards appeared at %s", url)
    return driver.page_source


def scrape(city: str, pages: int, headless: bool) -> list[dict]:
    """Scrape pages 1..pages sequentially and return the parsed jobs."""
    driver = make_driver(headless)
    jobs: list[dict] = []
    try:
        for page in range(1, pages + 1):
            found: list[dict] = []
            for url in page_urls(city, page):
                html = fetch_html(driver, url)
                found = parse_jobs(html)
                if found:
                    break
                if any(h in html.lower() for h in BLOCK_HINTS):
                    logger.warning("Block page suspected at %s", url)
            logger.info("Page %d: %d jobs", page, len(found))
            jobs.extend(found)
            time.sleep(PAGE_DELAY_SECONDS)
    finally:
        driver.quit()
    return jobs


def store(jobs: list[dict]) -> int:
    """Drop jobs already stored by earlier runs (and duplicates within this run), then write."""
    seen = existing_keys("raw/scraped_jobs", "jobs.jsonl", job_key)
    fresh: list[dict] = []
    for job in jobs:
        key = job_key(job)
        if key in seen:
            continue
        seen.add(key)
        fresh.append(job)
    out = run_folder("raw/scraped_jobs") / "jobs.jsonl"
    count = write_jsonl(out, fresh)
    logger.info("Wrote %d new jobs (%d scraped, %d duplicates) to %s", count, len(jobs), len(jobs) - count, out)
    return count


def main() -> None:
    """Command-line entry point."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pages", type=int, default=int(os.environ.get("SCRAPER_MAX_PAGES", "5")))
    ap.add_argument("--city", default=os.environ.get("SCRAPER_CITY", "india"))
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    args = ap.parse_args()
    headless = not args.headed and os.environ.get("SCRAPER_HEADLESS", "1") != "0"
    try:
        jobs = scrape(args.city.lower().replace(" ", "-"), args.pages, headless)
    except Exception as exc:  # scraping failures must not leave a half-written run
        logger.error("FAIL: scrape failed: %s", exc)
        sys.exit(1)
    store(jobs)


if __name__ == "__main__":
    main()
