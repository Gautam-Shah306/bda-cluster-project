"""Worker analysis and reskilling routes.

All routes use get_current_user which returns a static demo user for public access.
The POST /worker/profile endpoint calls the Gemini worker analysis engine if available.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from src.common.mongo_client import get_db
from src.api.jwt_handler import get_current_user
import logging
from datetime import datetime

# Worker engine imports — wrapped in try/except so the API starts even if
# the optional engine packages are not installed.
try:
    from src.api.worker_engine.worker_parser import parse_worker_profile
except ImportError:
    def parse_worker_profile(profile: dict) -> dict:  # type: ignore
        return {
            "role": profile.get("job_title", ""),
            "city": profile.get("city", ""),
            "skills": profile.get("skills", []),
        }

try:
    from src.api.worker_engine.worker_gemini import analyze_worker as gemini_analyze_worker
except ImportError:
    def gemini_analyze_worker(**kwargs) -> Optional[dict]:  # type: ignore
        return None

try:
    from src.api.worker_engine.reskilling_engine import generate_reskilling_path
except ImportError:
    def generate_reskilling_path(**kwargs) -> dict:  # type: ignore
        return {
            "recommendation_type": None,
            "summary": "Reskilling engine not available.",
            "recommended_skills": [],
            "recommended_courses": [],
            "recommended_jobs": [],
            "learning_path": [],
            "error": "Engine not installed.",
        }

router = APIRouter(prefix="/worker", tags=["Worker"])

logger = logging.getLogger(__name__)


class WorkerProfile(BaseModel):
    job_role: str
    city: str
    years_of_experience: float
    role_description: str
    skills: List[str]


@router.get("/profile")
def get_worker_profile(current_user: dict = Depends(get_current_user)):
    """Return the current user's worker profile."""
    return {
        "job_role": current_user.get("job_role"),
        "city": current_user.get("city"),
        "years_of_experience": current_user.get("years_of_experience"),
        "role_description": current_user.get("role_description"),
        "skills": current_user.get("skills", []),
        "gemini_risk_score": current_user.get("gemini_risk_score"),
        "reasoning": current_user.get("reasoning"),
        "reskilling_path": current_user.get("reskilling_path"),
        "gemini_analysis": current_user.get("gemini_analysis"),
    }


@router.post("/profile")
def update_worker_profile(profile: WorkerProfile, current_user: dict = Depends(get_current_user)):
    """Analyse the worker profile with Gemini and save the result."""
    legacy_profile = {
        "job_title": profile.job_role,
        "city": profile.city,
        "experience_years": profile.years_of_experience,
        "writeup": profile.role_description,
        "skills": profile.skills,
    }

    parsed = parse_worker_profile(legacy_profile)

    # Allow frontend skills override
    if profile.skills:
        parsed["skills"] = list(set(parsed.get("skills", []) + profile.skills))

    # Call Gemini for AI-powered worker analysis
    gemini_analysis = gemini_analyze_worker(
        job_title=profile.job_role,
        city=profile.city,
        experience=profile.years_of_experience,
        skills=profile.skills if profile.skills else parsed.get("skills", []),
    )

    logger.info("Worker profile update called for role: %s", profile.job_role)

    gemini_score = gemini_analysis.get("risk_score") if gemini_analysis else None

    # Save to MongoDB (best-effort)
    try:
        db = get_db()
        db["users"].update_one(
            {"email": current_user["email"]},
            {"$set": {
                "name": current_user.get("name"),
                "email": current_user["email"],
                "job_role": profile.job_role,
                "city": profile.city,
                "years_experience": profile.years_of_experience,
                "role_description": profile.role_description,
                "skills": profile.skills if profile.skills else parsed.get("skills", []),
                "gemini_risk_score": gemini_score,
                "gemini_analysis": gemini_analysis,
                "reasoning": gemini_analysis.get("explanation") if gemini_analysis else None,
                "updated_at": datetime.utcnow(),
            }},
            upsert=True,
        )
    except Exception as exc:
        logger.error("Mongo profile update failed: %s", exc)

    return {
        "parsed_profile": parsed,
        "gemini_analysis": gemini_analysis,
    }


# ── Reskilling endpoints ──────────────────────────────────────────────────────

@router.get("/reskilling")
def get_reskilling(current_user: dict = Depends(get_current_user)):
    """Return the cached reskilling result from MongoDB (if any)."""
    # Try to load from MongoDB
    try:
        db = get_db()
        record = db["users"].find_one({"email": current_user["email"]}, {"_id": 0})
        if record:
            cached = record.get("reskilling_result")
            if cached:
                return cached
    except Exception as exc:
        logger.error("Error reading reskilling from Mongo: %s", exc)

    return {
        "recommendation_type": None,
        "summary": "No reskilling analysis generated yet. Click 'Generate' to create one.",
        "recommended_skills": [],
        "recommended_courses": [],
        "recommended_jobs": [],
        "learning_path": [],
        "error": None,
    }


@router.post("/reskilling")
def create_reskilling(current_user: dict = Depends(get_current_user)):
    """Generate a new Gemini-powered reskilling path for the current user."""
    # Pull freshest profile from Mongo
    user_data = dict(current_user)
    try:
        db = get_db()
        record = db["users"].find_one({"email": current_user["email"]}, {"_id": 0})
        if record:
            user_data = record
    except Exception as exc:
        logger.error("Error reading user from Mongo: %s", exc)

    job_role = user_data.get("job_role")
    if not job_role:
        return {
            "recommendation_type": None,
            "summary": "Please fill in your Worker Analysis profile first.",
            "recommended_skills": [],
            "recommended_courses": [],
            "recommended_jobs": [],
            "learning_path": [],
            "error": "No worker profile found. Submit your profile on the Worker Analysis page first.",
        }

    result = generate_reskilling_path(
        job_title=job_role,
        city=user_data.get("city", ""),
        experience=float(user_data.get("years_experience", 0) or 0),
        skills=user_data.get("skills", []),
        gemini_analysis=user_data.get("gemini_analysis"),
    )

    logger.info("Reskilling path generated for user %s", current_user.get("email"))

    # Persist to MongoDB
    try:
        db = get_db()
        db["users"].update_one(
            {"email": current_user["email"]},
            {"$set": {
                "reskilling_result": result,
                "reskilling_updated_at": datetime.utcnow(),
            }},
        )
    except Exception as exc:
        logger.error("Error saving reskilling to Mongo: %s", exc)

    return result
