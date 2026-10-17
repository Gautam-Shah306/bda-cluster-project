"""FastAPI router for course-related endpoints.

Serves courses from MongoDB res_courses collection (precomputed by the pipeline).
Falls back to an empty list if the collection is empty or not yet loaded.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Query

from src.common.mongo_client import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_courses() -> list:
    """Fetch all courses from the res_courses MongoDB collection."""
    try:
        db = get_db()
        return list(db["res_courses"].find({}, {"_id": 0}).sort("seq", 1))
    except Exception as exc:
        logger.error("Error fetching courses from MongoDB: %s", exc)
        return []


@router.get("/courses")
def list_courses(
    source: Optional[str] = Query(None, description="Filter by source: SWAYAM or NPTEL"),
    domain: Optional[str] = Query(None, description="Filter by domain/discipline"),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
):
    """Return all courses, optionally filtered by source or domain. Paginated via limit/offset."""
    courses = _get_courses()

    if source:
        courses = [c for c in courses if c.get("source", "").upper() == source.upper()]
    if domain:
        domain_lower = domain.lower()
        courses = [c for c in courses if domain_lower in c.get("domain", "").lower()]

    total = len(courses)
    page = courses[offset: offset + limit]
    return {"total": total, "offset": offset, "limit": limit, "courses": page}


@router.get("/courses/stats")
def courses_stats():
    """Dataset statistics – total count and breakdown by source."""
    courses = _get_courses()
    by_source: dict = {}
    for c in courses:
        src = c.get("source", "Unknown")
        by_source[src] = by_source.get(src, 0) + 1
    domains = list({c.get("domain", "") for c in courses if c.get("domain")})
    return {"total": len(courses), "by_source": by_source, "domains": domains}


@router.get("/courses/for-skills")
def courses_for_skills(
    skills: str = Query(..., description="Comma-separated skill names"),
    max_results: int = Query(20, le=50),
):
    """Return courses that match the requested skill names."""
    skill_list = [s.strip().lower() for s in skills.split(",") if s.strip()]
    if not skill_list:
        return {"courses": [], "skills_queried": []}
    courses = _get_courses()
    results = []
    for c in courses:
        tags = [t.lower() for t in (c.get("skill_tags_orig", "") or "").split(",") if t.strip()]
        if any(sk in tags for sk in skill_list):
            results.append(c)
        if len(results) >= max_results:
            break
    return {"courses": results, "skills_queried": skill_list}


@router.get("/courses/reskilling")
def courses_for_reskilling(
    target_role: str = Query(..., description="Target job role"),
    current_skills: Optional[str] = Query(None),
    max_weeks: Optional[int] = Query(None),
    max_results: int = Query(10, le=30),
):
    """Return courses relevant for transitioning to target_role."""
    courses = _get_courses()
    role_lower = target_role.lower()
    results = []
    for c in courses:
        tags = (c.get("skill_tags_orig", "") or "").lower()
        if role_lower in tags or any(w in tags for w in role_lower.split()):
            if max_weeks is None or (c.get("duration_int") or 0) <= max_weeks:
                results.append(c)
        if len(results) >= max_results:
            break
    return {"target_role": target_role, "max_weeks": max_weeks, "courses": results}


@router.post("/scrape/courses")
def trigger_courses_scrape():
    """Scraping is disabled in this deployment."""
    return {
        "status": "disabled",
        "message": "Course scraping is not available in this deployment.",
    }