"""Chatbot routes – serves a simplified stub since the chatbot module is not installed."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


class ChatbotQuery(BaseModel):
    worker_profile: dict = {}
    question: str


@router.post("/query")
def chatbot(query: ChatbotQuery):
    """
    Handle chatbot queries.
    Returns a placeholder response when the chatbot module is not available.
    """
    return {
        "response": (
            "The chatbot is not available in this deployment. "
            "Please check the backend configuration."
        )
    }
