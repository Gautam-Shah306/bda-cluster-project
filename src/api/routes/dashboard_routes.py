"""Dashboard routes."""
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Query

from src.common.mongo_client import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_collection(name: str):
    """Helper to get a MongoDB collection."""
    return get_db()[name]

def query_docs(collection_name: str, filter_query: dict = None, sort_field: str = "seq") -> list:
    """Helper to query documents without _id and seq."""
    if filter_query is None:
        filter_query = {}
    docs = get_collection(collection_name).find(filter_query, {"_id": 0, "seq": 0})
    if sort_field:
        docs = docs.sort(sort_field, 1)
    return list(docs)

@router.get("/latest-jobs")
def get_latest_jobs() -> list:
    """Get latest 50 jobs."""
    docs = get_db()["res_latest_jobs"].find({}, {"_id": 0, "seq": 0, "row_id": 0}).sort("seq", 1)
    return list(docs)

@router.get("/skill-gap")
def get_skill_gap() -> list:
    """Get skill gap data."""
    docs = query_docs("res_skill_gap")
    return [{"skill": d["skill"], "market_demand": d["market_demand"], "training_supply": d["training_supply"], "gap": d["gap"]} for d in docs]

@router.get("/stats")
def get_stats() -> dict:
    """Get global stats."""
    docs = query_docs("res_stats")
    if not docs:
        return {"total_jobs": 0, "top_city": "N/A", "most_in_demand_skill": "N/A", "most_common_role": "N/A"}
    return docs[0]

@router.get("/hiring-trends")
def get_hiring_trends() -> list:
    """Get hiring trends."""
    return query_docs("res_hiring_trends")

@router.get("/skill-trends")
def get_skill_trends(year: Optional[int] = Query(None)) -> dict:
    """Get skill trends for a given year (or all)."""
    year_key = str(year) if year is not None else "all"
    docs = query_docs("res_skill_trends", {"year_key": year_key}, sort_field="rank")
    rising = []
    declining = []
    for d in docs:
        if d["kind"] == "rising":
            rising.append({"name": d["name"], "growth": f"+{d['change']}", "color": "from-blue-500 to-cyan-400"})
        elif d["kind"] == "declining":
            declining.append({"name": d["name"], "decline": str(d["change"])})
    return {"rising_skills": rising, "declining_skills": declining}

@router.get("/skill-trend-years")
def get_skill_trend_years() -> dict:
    """Get available years for skill trends."""
    docs = get_collection("res_skill_years").find({}, {"_id": 0, "seq": 0}).sort("seq", 1)
    years = [d["year"] for d in docs if "year" in d]
    return {"years": years}

@router.get("/vulnerability")
def get_vulnerability() -> dict:
    """Get vulnerability table and region averages based on the table."""
    docs = query_docs("res_vuln_table")
    table = []
    city_scores = defaultdict(list)
    for d in docs:
        role = d["role_key"].title()
        city = d["city"].title()
        score = d["ai_risk_score"]
        table.append({"job_role": role, "city": city, "ai_risk_score": score})
        city_scores[city].append(score)
        
    regions = {city: sum(scores)/len(scores) for city, scores in city_scores.items()}
    return {"table": table, "regions": regions}

@router.get("/vulnerability-regions")
def get_vulnerability_regions() -> dict:
    """Get full vulnerability regions."""
    role_docs = query_docs("res_vuln_roles")
    region_docs = query_docs("res_vuln_regions")
    
    role_risks = {d.get("role_key"): d.get("risk") for d in role_docs if "role_key" in d}
    region_risks = {d.get("city"): d.get("risk") for d in region_docs if "city" in d}
    
    return {"role_risks": role_risks, "region_risks": region_risks}

@router.get("/scraped-jobs")
def get_scraped_jobs(refresh: bool = True) -> dict:
    """Get scraped jobs status."""
    stats = get_stats()
    total = stats.get("total_jobs", 0)
    return {"total": total, "jobs": [], "scrape_error": None, "scrape_stats": None}

@router.get("/top-cities")
def get_top_cities() -> list:
    """Get top cities."""
    return query_docs("res_top_cities")

@router.get("/industry-distribution")
def get_industry_distribution() -> list:
    """Get industry distribution."""
    return query_docs("res_industry")

@router.get("/top-roles")
def get_top_roles() -> list:
    """Get top roles."""
    return query_docs("res_top_roles")

@router.get("/city-role-distribution")
def get_city_role_distribution(city: str = Query(..., description="The city name")) -> list:
    """Get role distribution for a city."""
    city_key = city.strip().lower()
    return query_docs("res_city_roles", {"city_key": city_key}, sort_field="rank")

@router.get("/role-city-distribution")
def get_role_city_distribution(role: str = Query(..., description="The role name")) -> list:
    """Get city distribution for a role."""
    role_key = role.strip().lower()
    return query_docs("res_role_cities", {"role_key": role_key}, sort_field="rank")
