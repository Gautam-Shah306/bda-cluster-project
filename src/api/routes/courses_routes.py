"""Courses routes."""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from src.common.mongo_client import get_db

router = APIRouter(prefix="", tags=["Courses"])  # prefix is handled, wait, endpoints are /courses, /courses/stats etc. So prefix="/courses"

def get_all_courses() -> list:
    """Load all courses from res_courses sorted by seq."""
    docs = get_db()["res_courses"].find(
        {},
        {"_id": 0, "seq": 0, "course_id": 0}
    ).sort("seq", 1)
    return list(docs)

def query_courses_for_skills(skills: list, max_results: int) -> list:
    """Find courses matching skills."""
    wanted = {s.lower() for s in skills}
    courses = get_all_courses()
    
    scored_courses = []
    for c in courses:
        tags = set(t.lower() for t in c.get("skill_tags", []))
        
        name = c.get("name") or ""
        domain = c.get("domain") or ""
        words = set((name + " " + domain).lower().split())
        
        searchable = tags.union(words)
        overlap = len(wanted & searchable)
        
        if overlap > 0:
            scored_courses.append((overlap, c))
            
    # Sort stable by overlap descending
    scored_courses.sort(key=lambda x: x[0], reverse=True)
    
    return [c for overlap, c in scored_courses][:max_results]


def query_courses_for_reskilling(target_role: str, current_skills: list, max_weeks: Optional[int], max_results: int) -> list:
    """Find courses for reskilling."""
    terms = target_role.lower().split() + [s.lower() for s in current_skills]
    candidates = query_courses_for_skills(terms, max_results=50)
    
    if max_weeks is not None:
        filtered = []
        for c in candidates:
            dw = c.get("duration_weeks")
            if dw is None:
                filtered.append(c)
            else:
                # duration_weeks of 0 counts as 999
                eff_dw = dw or 999
                if eff_dw <= max_weeks:
                    filtered.append(c)
        candidates = filtered
        
    return candidates[:max_results]


@router.get("/courses")
def get_courses(
    source: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> dict:
    """Get courses with filters."""
    courses = get_all_courses()
    
    if source:
        courses = [c for c in courses if (c.get("source") or "") == source.upper()]
        
    if domain:
        domain_lower = domain.lower()
        courses = [c for c in courses if domain_lower in (c.get("domain") or "").lower()]
        
    total = len(courses)
    filtered = courses[offset:offset+limit]
    
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "courses": filtered
    }

@router.get("/courses/stats")
def get_courses_stats() -> dict:
    """Get course statistics."""
    courses = get_all_courses()
    if not courses:
        return {"total": 0, "swayam": 0, "nptel": 0, "domains": []}
        
    total = len(courses)
    swayam = sum(1 for c in courses if (c.get("source") or "") == "SWAYAM")
    nptel = sum(1 for c in courses if (c.get("source") or "") == "NPTEL")
    
    domains = {c.get("domain") for c in courses if c.get("domain")}
    sorted_domains = sorted(list(domains))
    
    return {
        "total": total,
        "swayam": swayam,
        "nptel": nptel,
        "domains": sorted_domains
    }

@router.get("/courses/for-skills")
def get_courses_for_skills(
    skills: str = Query(...),
    max_results: int = Query(20, ge=1, le=50)
) -> dict:
    """Get courses matching specific skills."""
    skills_list = [s.strip() for s in skills.split(",")]
    skills_list = [s for s in skills_list if s]
    
    if not skills_list:
        return {"courses": [], "skills_queried": []}
        
    matched = query_courses_for_skills(skills_list, max_results)
    
    return {
        "courses": matched,
        "skills_queried": skills_list
    }

@router.get("/courses/reskilling")
def get_courses_reskilling(
    target_role: str = Query(...),
    current_skills: Optional[str] = Query(None),
    max_weeks: Optional[int] = Query(None),
    max_results: int = Query(10, ge=1, le=30)
) -> dict:
    """Get reskilling courses."""
    current_list = []
    if current_skills:
        current_list = [s.strip() for s in current_skills.split(",")]
        current_list = [s for s in current_list if s]
        
    courses = query_courses_for_reskilling(target_role, current_list, max_weeks, max_results)
    
    return {
        "target_role": target_role,
        "max_weeks": max_weeks,
        "courses": courses
    }

@router.post("/scrape/courses")
def scrape_courses(
    swayam: bool = Query(True),
    nptel: bool = Query(True)
) -> dict:
    """Scrape courses (disabled)."""
    return {
        "status": "disabled",
        "message": "Course scraping runs as a separate ingestion step.",
        "sources": {
            "swayam": swayam,
            "nptel": nptel
        }
    }
