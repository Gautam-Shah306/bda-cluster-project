"""Security module for the API."""
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.common.mongo_client import get_db

repo_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=repo_root / ".env", override=False)

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "")
if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32 or JWT_SECRET_KEY == "supersecretsaxkey":
    raise RuntimeError("JWT_SECRET_KEY is missing, empty, too short, or uses the default placeholder.")

JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.environ.get("ACCESS_TOKEN_EXPIRE_HOURS", "24"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: The plain text password.
        
    Returns:
        The hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash.
    
    Args:
        plain_password: The plain text password.
        hashed_password: The hashed password.
        
    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Create a JWT access token.
    
    Args:
        data: The payload data.
        
    Returns:
        The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT access token.
    
    Args:
        token: The encoded JWT token.
        
    Returns:
        The decoded payload, or None if invalid.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get the current authenticated user from the token.
    
    Args:
        token: The JWT access token.
        
    Returns:
        The user document from the database (without the password).
        
    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("email")
    if email is None:
        raise credentials_exception
        
    db = get_db()
    user = db["users"].find_one({"email": email}, {"password": 0})
    if user is None:
        raise credentials_exception
        
    return user
