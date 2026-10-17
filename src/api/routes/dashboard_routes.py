"""FastAPI routes for dashboard analytics served directly from MongoDB res_* collections.

All data is precomputed by the Hadoop/Spark batch pipeline and stored in MongoDB.
"""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Query

from src.common.logging_setup import get_logger
from src.common.mongo_client import get_db

log = get_logger(__name__)
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _coll(name: str):
    return get_db()[name]


def _to_list(collection_name: str) -> list:
    return list(_coll(collection_name).find({}, {"_id": 0}).sort("seq", 1))


@router.get("/stats")
async def stats() -> dict:
    docs = _to_list("res_stats")
    if not docs:
        return {"total_jobs": 0, "top_city": "N/A", "most_in_demand_skill": "N/A", "most_common_role": "N/A"}
    return docs[0]


@router.get("/skill-gap")
async def skill_gap() -> list:
    return _to_list("res_skill_gap")


@router.get("/hiring-trends")
async def hiring_trends() -> list:
    return _to_list("res_hiring_trends")


@router.get("/skill-trends")
async def skill_trends(year: Optional[int] = Query(None)) -> dict:
    year_filter = str(year) if year else "all"
    docs = list(_coll("res_skill_trends").find({"year_filter": year_filter}, {"_id": 0}).sort("seq", 1))
    rising = [d for d in docs if d.get("type") == "rising"]
    declining = [d for d in docs if d.get("type") == "declining"]
    return {"rising_skills": rising, "declining_skills": declining}


@router.get("/skill-trend-years")
async def skill_trend_years() -> dict:
    docs = _to_list("res_skill_years")
    years = [d["year"] for d in docs if "year" in d]
    return {"years": sorted(years, reverse=True)}


@router.get("/vulnerability")
async def vulnerability() -> dict:
    table = _to_list("res_vuln_table")
    from collections import defaultdict
    city_scores = defaultdict(list)
    for row in table:
        city = row.get("city", "")
        score = row.get("ai_risk_score", 0)
        if city:
            city_scores[city].append(score)
    regions = {
        city: round(sum(scores) / len(scores), 2)
        for city, scores in city_scores.items()
        if scores
    }
    return {"table": table, "regions": regions}


@router.get("/vulnerability-regions")
async def vulnerability_regions() -> dict:
    role_docs = list(_coll("res_vuln_roles").find({}, {"_id": 0}))
    region_docs = list(_coll("res_vuln_regions").find({}, {"_id": 0}))
    role_risks = {d["role"]: d["score"] for d in role_docs}
    region_risks = {d["city"]: d["score"] for d in region_docs}
    return {"role_risks": role_risks, "region_risks": region_risks}


@router.get("/latest-jobs")
async def latest_jobs() -> list:
    return _to_list("res_latest_jobs")


@router.get("/scraped-jobs")
async def scraped_jobs(refresh: bool = Query(True)) -> dict:
    doc = get_db()["res_stats"].find_one({}, {"_id": 0})
    total = doc.get("total_jobs", 0) if doc else 0
    return {"total": total, "jobs": [], "scrape_error": None, "scrape_stats": None}


@router.get("/top-cities")
async def top_cities() -> list:
    return _to_list("res_top_cities")


@router.get("/industry-distribution")
async def industry_distribution() -> list:
    return _to_list("res_industry")


@router.get("/top-roles")
async def top_roles() -> list:
    return _to_list("res_top_roles")


@router.get("/city-role-distribution")
async def city_role_distribution(city: str = Query(...)) -> list:
    docs = list(
        get_db()["res_city_roles"].find(
            {"city_lower": city.strip().lower()}, {"_id": 0}
        ).sort("count", -1).limit(10)
    )
    return [{"name": d.get("role", ""), "value": d.get("count", 0)} for d in docs]


@router.get("/role-city-distribution")
async def role_city_distribution(role: str = Query(...)) -> list:
    docs = list(
        get_db()["res_role_cities"].find(
            {"role_lower": role.strip().lower()}, {"_id": 0}
        ).sort("count", -1).limit(10)
    )
    return [{"name": d.get("city", ""), "value": d.get("count", 0)} for d in docs]
