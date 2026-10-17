"""Pure parsers for course sources: NPTEL preview pages and SWAYAM Google-Sheet CSV tabs.

The page layout is taken from REFERENCE_ANALYSIS C.2; no live page was available when
this was written, so the HTML tests use synthetic pages built from that description.
Re-check against a real page before relying on it (see docs/DECISIONS.md D-034).
"""
import csv
import io
import json
import re

from bs4 import BeautifulSoup

MAX_TAGS = 15
_SENTENCE_MARKERS = (" would ", " should ", " is ", " are ", " will ", " can ")
_GENERIC = {"etc", "etc.", "others", "other", "all", "general", "nil", "none", "na", "n/a"}


def is_noise_tag(tag: str) -> bool:
    """True when a candidate skill tag is too short/long, a sentence, a URL or generic."""
    t = tag.strip().lower()
    if not (3 <= len(t) <= 60) or t in _GENERIC:
        return True
    if "http" in t or "www." in t or t.startswith("exposure to"):
        return True
    return any(m in f" {t} " for m in _SENTENCE_MARKERS)


def clean_tags(candidates: list[str]) -> list[str]:
    """Strip, drop noise, de-duplicate case-insensitively (keeping first spelling), cap at 15."""
    seen: set[str] = set()
    out: list[str] = []
    for raw in candidates:
        tag = raw.strip().strip("*. ")
        if not tag or is_noise_tag(tag) or tag.lower() in seen:
            continue
        seen.add(tag.lower())
        out.append(tag)
        if len(out) >= MAX_TAGS:
            break
    return out


def split_terms(text: str) -> list[str]:
    """Split free text on commas, semicolons and slashes."""
    return [p for p in re.split(r"[,;/]", text) if p.strip()]


def _cell_after(soup: BeautifulSoup, label: str) -> str:
    """Return the text of the cell that follows a cell whose text equals ``label``."""
    for cell in soup.find_all(["td", "th"]):
        if cell.get_text(strip=True).lower().rstrip(":") == label.lower():
            nxt = cell.find_next_sibling(["td", "th"])
            if nxt:
                return nxt.get_text("\n", strip=True)
    return ""


def _first_int(text: str) -> int | None:
    """Return the first integer in a string, or None."""
    m = re.search(r"\d+", text)
    return int(m.group()) if m else None


def parse_nptel_preview(html: str, course_id: str) -> dict | None:
    """Parse one NPTEL preview page; None when the page has no course title."""
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1")
    name = h1.get_text(" ", strip=True) if h1 else ""
    if not name:
        return None
    institution = ""
    for s in soup.stripped_strings:
        if s.lower().startswith("by ") and "|" in s:
            institution = s.rsplit("|", 1)[1].strip()
            break
    category = [c.strip() for c in _cell_after(soup, "Category").split("\n") if c.strip()]
    domain = category[0] if category else ""
    candidates = [name] + category[1:]
    page_text = soup.get_text("\n")
    for label in ("INTENDED AUDIENCE", "INDUSTRY SUPPORT", "PREREQUISITES"):
        m = re.search(label + r"\s*:?\s*([^\n*]{5,200})", page_text, re.IGNORECASE)
        if m:
            candidates.extend(split_terms(m.group(1)))
    weeks = [w.strip() for w in re.findall(r"Week\s*\d+[^\n]*", page_text)][:16]
    return {
        "name": name,
        "source": "NPTEL",
        "domain": domain,
        "url": f"https://onlinecourses.nptel.ac.in/{course_id}/preview",
        "institution": institution,
        "duration_weeks": _first_int(_cell_after(soup, "Duration")),
        "difficulty": _cell_after(soup, "Level"),
        "skill_tags": ", ".join(clean_tags(candidates)),
        "syllabus_weeks": json.dumps(weeks, ensure_ascii=False),
    }


def nptel_ids_from_sheet(csv_text: str) -> list[str]:
    """Extract NPTEL course ids (e.g. noc25_cs10) from a sheet tab, keeping first-seen order."""
    found = re.findall(r"nptel\.ac\.in/([a-z0-9_]+)/preview", csv_text) + re.findall(r"(noc\d{2}_[a-z0-9]+)", csv_text)
    return list(dict.fromkeys(found))


def _find_header(rows: list[list[str]]) -> int:
    """Index of the header row (first of the first five containing 'course title' or 'preview')."""
    for i, row in enumerate(rows[:5]):
        joined = " ".join(row).lower()
        if "course title" in joined or "preview" in joined:
            return i
    return -1


def _col(header: list[str], *needles: str, exclude: str = "") -> int:
    """Index of the first header cell containing all needles (and not ``exclude``), else -1."""
    for i, h in enumerate(header):
        hl = h.lower()
        if all(n in hl for n in needles) and not (exclude and exclude in hl):
            return i
    return -1


def parse_swayam_tab(csv_text: str, coordinator: str) -> list[dict]:
    """Parse one SWAYAM sheet tab into course dicts."""
    rows = list(csv.reader(io.StringIO(csv_text)))
    h = _find_header(rows)
    if h < 0:
        return []
    header = rows[h]
    c_title = _col(header, "course title") if _col(header, "course title") >= 0 else _col(header, "title")
    c_disc, c_inst = _col(header, "discipline"), _col(header, "institute")
    if c_inst < 0:
        c_inst = _col(header, "university")
    c_level, c_dur = _col(header, "level", exclude="ncrf"), _col(header, "duration")
    c_ind, c_url = _col(header, "industry"), _col(header, "preview", "url")
    if c_url < 0:
        c_url = _col(header, "preview")

    def cell(row: list[str], idx: int) -> str:
        return row[idx].strip() if 0 <= idx < len(row) else ""

    courses: list[dict] = []
    for row in rows[h + 1:]:
        title = cell(row, c_title)
        if len(title) < 3 or not re.search(r"[A-Za-z]", title):
            continue
        m = re.search(r"(https://[^\s,;]+/preview)", " ".join(row))
        discipline = cell(row, c_disc)
        candidates = [title] + split_terms(discipline) + split_terms(cell(row, c_ind))
        courses.append(
            {
                "name": title,
                "source": "SWAYAM",
                "domain": discipline or f"{coordinator} Course",
                "url": m.group(1) if m else (cell(row, c_url) if cell(row, c_url).startswith("http") else ""),
                "institution": cell(row, c_inst),
                "duration_weeks": _first_int(cell(row, c_dur)),
                "difficulty": cell(row, c_level),
                "skill_tags": ", ".join(clean_tags(candidates)),
                "syllabus_weeks": "[]",
            }
        )
    return courses
