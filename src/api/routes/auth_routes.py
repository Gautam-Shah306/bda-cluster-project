"""Authentication routes."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from src.api.security import create_access_token, get_current_user, hash_password, verify_password
from src.common.mongo_client import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

class SignupRequest(BaseModel):
    """Request schema for signup."""
    email: EmailStr
    name: str
    password: str

class LoginRequest(BaseModel):
    """Request schema for login."""
    email: EmailStr
    password: str

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest) -> dict:
    """Register a new user."""
    email = request.email.lower().strip()
    db = get_db()
    
    if db["users"].find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user_doc = {
        "email": email,
        "name": request.name,
        "password": hash_password(request.password),
        "job_role": None,
        "city": None,
        "years_of_experience": None,
        "role_description": None,
        "skills": [],
        "risk_score": None,
        "created_at": datetime.now(timezone.utc)
    }
    
    db["users"].insert_one(user_doc)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(request: LoginRequest) -> dict:
    """Authenticate user and return JWT."""
    email = request.email.lower().strip()
    db = get_db()
    
    user = db["users"].find_one({"email": email})
    if not user or not verify_password(request.password, user.get("password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
        
    access_token = create_access_token(
        data={"user_id": str(user["_id"]), "email": email}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current user details."""
    return {
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "job_role": current_user.get("job_role"),
        "city": current_user.get("city"),
        "years_of_experience": current_user.get("years_of_experience"),
        "role_description": current_user.get("role_description"),
        "risk_score": current_user.get("gemini_risk_score")
    }
