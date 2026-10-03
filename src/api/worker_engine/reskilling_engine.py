"""Worker reskilling engine."""
import json
import re
from typing import List, Dict, Tuple, Set, Any

from src.common.mongo_client import get_db
from src.api.worker_engine.gemini_client import generate_text, mask_secrets, GeminiNotConfigured

SYSTEM_PROMPT = """You are an AI career guidance assistant analyzing a worker's profile, automation risk, market trends, available training courses, and job openings.
Based on the market demand, if the worker's field or target roles are seeing INCREASING demand, recommend "upskilling". If they are seeing DECLINING demand, recommend "reskilling".
You must recommend skills that align with the provided courses and job openings. The recommended courses and jobs must be selected ONLY from the provided lists.
Create a week-by-week learning path (e.g., "Week 1-2") tailored to the recommended skills.

You must reply ONLY with valid JSON matching this exact structure (no markdown formatting, no prose):
{
  "recommendation_type": "<upskilling|reskilling>",
  "summary": "<your overall recommendation summary>",
  "recommended_skills": [{"skill": "<skill_name>", "reason": "<reasoning>"}],
  "recommended_courses": [{"name": "<course_name>", "source": "<source>", "url": "<url>", "duration": "<duration text>", "matched_skills": ["<skill1>"]}],
  "recommended_jobs": [{"title": "<job_title>", "company": "<company_name>", "location": "<location>", "required_skills": ["<skill1>"], "match_reason": "<reasoning>"}],
  "learning_path": [{"week": "<e.g. Week 1-2>", "title": "<phase title>", "description": "<description>"}]
}"""

def error_response(msg: str, raw: str = "") -> dict:
    return {
        "recommendation_type": None,
        "summary": msg,
        "recommended_skills": [],
        "recommended_courses": [],
        "recommended_jobs": [],
        "learning_path": [],
        "raw_response": raw,
        "error": msg
    }

def build_pool(skills: List[str], gemini_analysis: Dict[str, Any], rising_names: List[str]) -> Set[str]:
    pool = set()
    items = []
    if skills:
        items.extend(skills)
    if gemini_analysis:
        items.extend(gemini_analysis.get("new_skills") or [])
        items.extend(gemini_analysis.get("pivot_roles") or [])
    if rising_names:
        items.extend(rising_names)
        
    for item in items:
        if isinstance(item, str):
            pool.add(item.lower())
    return pool

def get_trends() -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    db = get_db()
    rising = []
    declining = []
    
    for doc in db["res_skill_trends"].find({"year_key": "all"}).sort("rank", 1):
        if doc.get("kind") == "rising" and len(rising) < 10:
            rising.append({
                "name": doc["name"],
                "growth": f"+{doc['change']}",
                "color": "from-blue-500 to-cyan-400"
            })
        elif doc.get("kind") == "declining" and len(declining) < 10:
            declining.append({
                "name": doc["name"],
                "decline": str(doc["change"])
            })
    return rising, declining

def find_matching_courses(pool: Set[str], limit: int = 30) -> List[Dict[str, str]]:
    db = get_db()
    overlaps = {}
    for doc in db["res_reskill_index"].find({"kind": "course", "skill": {"$in": list(pool)}}):
        for cid in doc.get("ids", []):
            overlaps[cid] = overlaps.get(cid, 0) + 1
            
    valid = [(cid, count) for cid, count in overlaps.items() if count > 0]
    valid.sort(key=lambda x: (-x[1], x[0]))
    top_cids = [x[0] for x in valid[:limit]]
    
    if not top_cids:
        return []
        
    course_docs = {d["course_id"]: d for d in db["res_reskill_courses"].find({"course_id": {"$in": top_cids}})}
    dur_docs = {d["course_id"]: d.get("duration_weeks") for d in db["res_courses"].find({"course_id": {"$in": top_cids}})}
    
    result = []
    for cid in top_cids:
        doc = course_docs.get(cid)
        if not doc:
            continue
        duration_weeks = dur_docs.get(cid)
        duration_text = ""
        if duration_weeks is not None:
            if duration_weeks == 1:
                duration_text = "1 week"
            else:
                duration_text = f"{duration_weeks} weeks"
                
        result.append({
            "name": doc.get("name", ""),
            "source": doc.get("source", ""),
            "url": doc.get("url", ""),
            "duration": duration_text,
            "skill_tags": ", ".join(doc.get("tags_lower", []))
        })
    return result

def find_matching_jobs(pool: Set[str], limit: int = 20) -> List[Dict[str, str]]:
    db = get_db()
    overlaps = {}
    for doc in db["res_reskill_index"].find({"kind": "job", "skill": {"$in": list(pool)}}):
        for rid in doc.get("ids", []):
            overlaps[rid] = overlaps.get(rid, 0) + 1
            
    valid = [(rid, count) for rid, count in overlaps.items() if count > 0]
    valid.sort(key=lambda x: (-x[1], x[0]))
    top_rids = [x[0] for x in valid[:limit]]
    
    if not top_rids:
        return []
        
    job_docs = {d["row_id"]: d for d in db["res_reskill_jobs"].find({"row_id": {"$in": top_rids}})}
    
    result = []
    for rid in top_rids:
        doc = job_docs.get(rid)
        if not doc:
            continue
        result.append({
            "title": doc.get("title", ""),
            "company": doc.get("company", ""),
            "location": doc.get("city", ""),
            "skills": ", ".join(doc.get("skills_first10", []))
        })
    return result

def build_prompt(job_title: str, city: str, experience: float, skills: List[str], gemini_analysis: dict, rising: list, declining: list, courses: list, jobs: list) -> str:
    prompt_parts = [SYSTEM_PROMPT]
    
    safe_skills = [str(x) for x in skills if x is not None] if isinstance(skills, list) else []
    
    prompt_parts.append("--- Worker Profile ---")
    prompt_parts.append(f"Job Title: {job_title}")
    prompt_parts.append(f"City: {city}")
    prompt_parts.append(f"Years of Experience: {experience}")
    prompt_parts.append(f"Skills: {', '.join(safe_skills)}")
    
    if gemini_analysis:
        pivot = gemini_analysis.get('pivot_roles')
        new = gemini_analysis.get('new_skills')
        safe_pivot = [str(x) for x in pivot if x is not None] if isinstance(pivot, list) else []
        safe_new = [str(x) for x in new if x is not None] if isinstance(new, list) else []
        
        prompt_parts.append("--- AI Risk Assessment ---")
        prompt_parts.append(f"Risk Score: {gemini_analysis.get('risk_score', 'N/A')}/100")
        prompt_parts.append(f"Risk Level: {gemini_analysis.get('risk_level', 'unknown')}")
        prompt_parts.append(f"Pivot Roles: {', '.join(safe_pivot)}")
        prompt_parts.append(f"New Skills: {', '.join(safe_new)}")
        prompt_parts.append(f"Explanation: {gemini_analysis.get('explanation', '')}")
        
    prompt_parts.append("--- Market Hiring Trends ---")
    prompt_parts.append(json.dumps({"rising_skills": rising, "declining_skills": declining}, indent=2, ensure_ascii=False))
    
    prompt_parts.append("--- Available Training Courses (matched to target skills) ---")
    prompt_parts.append(json.dumps(courses[:20], indent=2, ensure_ascii=False))
    
    prompt_parts.append("--- Relevant Job Openings (matched to target skills) ---")
    prompt_parts.append(json.dumps(jobs[:15], indent=2, ensure_ascii=False))
    
    return "\n".join(prompt_parts)

def generate_reskilling_path(job_title: str, city: str, experience: float, skills: List[str], gemini_analysis: dict = None) -> dict:
    try:
        rising, declining = get_trends()
        rising_names = [r["name"] for r in rising]
        
        pool = build_pool(skills, gemini_analysis, rising_names)
        
        courses = find_matching_courses(pool, 30)
        jobs = find_matching_jobs(pool, 20)
        
        prompt = build_prompt(job_title, city, experience, skills, gemini_analysis, rising, declining, courses, jobs)
        
        try:
            raw_text = generate_text(prompt, "GEMINI_API_KEY_RESKILLING")
            
            match = re.search(r'\{[\s\S]*\}', raw_text)
            if match:
                try:
                    data = json.loads(match.group(0))
                    return {
                        "recommendation_type": data.get("recommendation_type", "reskilling"),
                        "summary": data.get("summary", ""),
                        "recommended_skills": data.get("recommended_skills", []),
                        "recommended_courses": data.get("recommended_courses", []),
                        "recommended_jobs": data.get("recommended_jobs", []),
                        "learning_path": data.get("learning_path", []),
                        "raw_response": raw_text,
                        "error": None
                    }
                except json.JSONDecodeError:
                    pass
            
            return error_response("Could not parse Gemini response.", raw_text)
            
        except GeminiNotConfigured:
            return error_response("Gemini reskilling is not configured. Set GEMINI_API_KEY_RESKILLING.")
        except Exception as exc:
            return error_response("Gemini request failed: " + mask_secrets(str(exc)))
            
    except Exception as exc:
        return error_response("Internal error: " + mask_secrets(str(exc)))
