"""Worker routes."""
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.api.security import get_current_user
from src.common.mongo_client import get_db
from src.api.worker_engine.worker_parser import parse_worker_profile
from src.api.worker_engine.worker_gemini import analyze_worker

router = APIRouter(prefix="/worker", tags=["Worker"])

class WorkerProfile(BaseModel):
    job_role: str
    city: str
    years_of_experience: float
    role_description: str
    skills: List[str]

@router.get("/profile")
def get_worker_profile(current_user: dict = Depends(get_current_user)) -> dict:
    """Get worker profile."""
    # current_user from get_current_user already strips password
    return {
        "job_role": current_user.get("job_role"),
        "city": current_user.get("city"),
        "years_of_experience": current_user.get("years_of_experience"),
        "role_description": current_user.get("role_description"),
        "skills": current_user.get("skills", []),
        "gemini_risk_score": current_user.get("gemini_risk_score"),
        "reasoning": current_user.get("reasoning"),
        "reskilling_path": current_user.get("reskilling_result"),
        "gemini_analysis": current_user.get("gemini_analysis")
    }

@router.post("/profile")
def update_worker_profile(profile: WorkerProfile, current_user: dict = Depends(get_current_user)) -> dict:
    """Update worker profile and run Gemini analysis."""
    legacy = {
        "job_title": profile.job_role,
        "city": profile.city,
        "experience_years": profile.years_of_experience,
        "writeup": profile.role_description,
        "skills": profile.skills
    }
    
    parsed = parse_worker_profile(legacy)
    
    # Merge skills
    submitted_skills = profile.skills
    final_skills = []
    
    if submitted_skills:
        # de-duplicate case-sensitively keeping first appearance order
        seen = set()
        for s in parsed["skills"] + submitted_skills:
            if s not in seen:
                final_skills.append(s)
                seen.add(s)
        parsed["skills"] = final_skills
        analysis_skills = submitted_skills
    else:
        analysis_skills = parsed["skills"]
        
    gemini_analysis = analyze_worker(
        job_title=profile.job_role,
        city=profile.city,
        experience=profile.years_of_experience,
        skills=analysis_skills
    )
    
    now_utc = datetime.now(timezone.utc)
    
    db = get_db()
    db["users"].update_one(
        {"email": current_user["email"]},
        {"$set": {
            "name": current_user.get("name"),
            "email": current_user["email"],
            "job_role": profile.job_role,
            "city": profile.city,
            "years_of_experience": float(profile.years_of_experience),
            "role_description": profile.role_description,
            "skills": submitted_skills,
            "gemini_risk_score": gemini_analysis.get("risk_score"),
            "gemini_analysis": gemini_analysis,
            "reasoning": gemini_analysis.get("explanation"),
            "updated_at": now_utc
        }},
        upsert=True
    )
    
    return {
        "parsed_profile": parsed,
        "gemini_analysis": gemini_analysis
    }

from src.api.worker_engine.reskilling_engine import generate_reskilling_path

@router.get("/reskilling")
def get_reskilling_path(current_user: dict = Depends(get_current_user)) -> dict:
    """Get stored reskilling path."""
    stored = current_user.get("reskilling_result")
    if stored:
        return stored
        
    return {
        "recommendation_type": None,
        "summary": "No reskilling analysis generated yet. Click 'Generate' to create one.",
        "recommended_skills": [],
        "recommended_courses": [],
        "recommended_jobs": [],
        "learning_path": [],
        "error": None
    }

@router.post("/reskilling")
def run_reskilling_path(current_user: dict = Depends(get_current_user)) -> dict:
    """Generate reskilling path based on the user's profile."""
    db = get_db()
    # Read fresh
    user = db["users"].find_one({"email": current_user["email"]}, {"password": 0})
    
    if user is None or not user.get("job_role"):
        return {
            "recommendation_type": None,
            "summary": "Please fill in your Worker Analysis profile first.",
            "recommended_skills": [],
            "recommended_courses": [],
            "recommended_jobs": [],
            "learning_path": [],
            "error": "No worker profile found. Submit your profile on the Worker Analysis page first."
        }
        
    result = generate_reskilling_path(
        job_title=user["job_role"],
        city=user.get("city") or "",
        experience=float(user.get("years_of_experience") or 0),
        skills=user.get("skills", []),
        gemini_analysis=user.get("gemini_analysis")
    )
    
    now_utc = datetime.now(timezone.utc)
    db["users"].update_one(
        {"email": current_user["email"]},
        {"$set": {
            "reskilling_result": result,
            "reskilling_updated_at": now_utc
        }}
    )
    return result
