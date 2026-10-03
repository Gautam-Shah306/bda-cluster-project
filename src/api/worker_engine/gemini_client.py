"""Gemini client for interacting with the Google GenAI SDK."""
import os
from pathlib import Path
from dotenv import load_dotenv

from google import genai

class GeminiNotConfigured(Exception):
    """Raised when no Gemini API key is configured."""
    pass

def get_model_name() -> str:
    """Get the configured Gemini model name."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    return os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")

def resolve_api_key(specific_var: str | None) -> str | None:
    """Resolve the API key based on priority."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    
    if specific_var:
        val = os.environ.get(specific_var)
        if val:
            return val
            
    val = os.environ.get("GEMINI_API_KEY")
    if val:
        return val
        
    val = os.environ.get("GOOGLE_API_KEY")
    if val:
        return val
        
    return None

def mask_secrets(text: str) -> str:
    """Mask configured API keys in text."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    
    masked_text = text
    for var in ["GEMINI_API_KEY_WORKERANALYSIS", "GEMINI_API_KEY_RESKILLING", "GEMINI_API_KEY", "GOOGLE_API_KEY"]:
        val = os.environ.get(var)
        if val:
            masked_text = masked_text.replace(val, "***")
            
    return masked_text

def get_timeout_ms() -> int:
    """Get the timeout in milliseconds. The SDK expects milliseconds."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    
    timeout_secs = float(os.environ.get("GEMINI_TIMEOUT_SECONDS", "60"))
    return int(timeout_secs * 1000)

def generate_text(prompt: str, specific_var: str | None) -> str:
    """Generate text using Gemini."""
    api_key = resolve_api_key(specific_var)
    if not api_key:
        raise GeminiNotConfigured("Gemini API key not configured")
        
    client = genai.Client(api_key=api_key, http_options={"timeout": get_timeout_ms()})
    model = get_model_name()
    
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    
    return response.text or ""
