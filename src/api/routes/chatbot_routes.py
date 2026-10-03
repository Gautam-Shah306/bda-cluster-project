"""Chatbot routes."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.api.security import get_current_user
from src.common.mongo_client import get_db
from src.api.chatbot.query_router import handle_query
from src.api.worker_engine.gemini_client import mask_secrets

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatbotQuery(BaseModel):
    worker_profile: dict = {}
    question: str = Field(min_length=1, max_length=1000)
    
    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("question must not be blank")
        return v

@router.post("/query")
def query_chatbot(query: ChatbotQuery, current_user: dict = Depends(get_current_user)) -> dict:
    """Ask the chatbot a question."""
    db = get_db()
    # Read fresh user document without password
    user_data = db["users"].find_one({"email": current_user["email"]}, {"password": 0})
    
    try:
        response_text = handle_query(query.model_dump(), user_data=user_data)
        return {"response": response_text}
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Chatbot failed: " + mask_secrets(str(exc))
        )
