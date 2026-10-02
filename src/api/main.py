"""Main FastAPI application."""
import os
from typing import Callable

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import auth_routes, dashboard_routes
from src.common.logging_setup import get_logger

logger = get_logger("api_main")

load_dotenv(override=False)

app = FastAPI(title="Skills Mirage API")

cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    """Log all API requests."""
    logger.info("API Request: %s %s", request.method, request.url.path)
    response = await call_next(request)
    return response

app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)

@app.get("/")
def read_root() -> dict:
    """Health check endpoint."""
    return {"message": "Skills Mirage Backend Running"}
