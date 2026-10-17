import os
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.common.mongo_client import get_db
users_collection = get_db()["users"]
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT Config ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretsaxkey")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload if payload else None
    except JWTError:
        return None


# --- Public access: no token required ---
def get_current_user():
    """Dummy implementation for public access.
    Returns a static demo user dict — no authentication required.
    """
    return {
        "email": "demo@example.com",
        "name": "Demo User",
        "job_role": "Software Engineer",
        "city": "Bangalore",
        "years_of_experience": 2,
        "role_description": "Demo role description",
        "skills": [],
        "gemini_risk_score": None,
        "gemini_analysis": None,
        "reasoning": None,
    }
