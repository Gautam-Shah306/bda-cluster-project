"""Parse Naukri search-result HTML into job dicts (selectors per REFERENCE_ANALYSIS C.1)."""
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from bs4.element import Tag

CARD_SELECTORS = [
    "div.cust-job-tuple",
    "div.srp-jobtuple-wrapper",
    "article.jobTuple",
    "div[class*='jobTuple']",
    "div[class*='job-tuple']",
    "li.jobTuple",
]
TITLE = "a.title, a[title], h2.title, a.jobTitle"
COMPANY = "a.comp-name, a.subTitle, span.comp-name, div.comp-name"
LOCATION = "span.locWdth, span.loc-wrap, span.location, li.location"
EXPERIENCE = "span.expwdth, span.exp-wrap, span.experience, li.experience"
DESCRIPTION = "span.job-desc, div.job-desc, p.job-desc"
SKILL_SELECTORS = ["li.tag-li", "li.dot", "li.skill-li", "span.skill-tag"]


def _text(card: Tag, selector: str) -> str:
    """Return the stripped text of the first element matching a selector, or ''."""
    el = card.select_one(selector)
    return el.get_text(" ", strip=True) if el else ""


def _skills(card: Tag) -> list[str]:
    """Return skills from the first skill selector that matches anything."""
    for sel in SKILL_SELECTORS:
        found = [e.get_text(strip=True) for e in card.select(sel)]
        found = [s for s in found if s]
        if found:
            return found
    return []


def find_cards(soup: BeautifulSoup) -> list[Tag]:
    """Return job cards using the first card selector that matches."""
    for sel in CARD_SELECTORS:
        cards = soup.select(sel)
        if cards:
            return cards
    return []


def parse_jobs(html: str, scraped_at: datetime | None = None) -> list[dict]:
    """Parse one results page into dicts with the raw jobs CSV column names.

    ``postdate`` is the SCRAPE time in the reference format (reference weakness W4,
    kept for compatibility, D-034); the same moment is also stored in ``scraped_at``
    so the two can be told apart later. Cards without a title are skipped.
    """
    stamp = (scraped_at or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M:%S +0000")
    jobs: list[dict] = []
    for card in find_cards(BeautifulSoup(html, "lxml")):
        title = _text(card, TITLE)
        if not title:
            continue
        link = card.select_one(TITLE)
        jobs.append(
            {
                "jobtitle": title,
                "company": _text(card, COMPANY),
                "joblocation_address": _text(card, LOCATION),
                "experience": _text(card, EXPERIENCE),
                "jobdescription": _text(card, DESCRIPTION),
                "skills": ",".join(_skills(card)),
                "postdate": stamp,
                "scraped_at": stamp,
                "job_url": link.get("href", "") if link else "",
            }
        )
    return jobs
