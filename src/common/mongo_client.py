"""MongoDB client factory for the Skills Mirage project.

Provides get_db() which loads credentials from .env and returns the
project database object. The connection URI is never printed in full;
it is masked in log output.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

from src.common.logging_setup import get_logger

log = get_logger(__name__)

_ENV_PATH = Path(__file__).parents[2] / ".env"


def _mask_uri(uri: str) -> str:
    """Mask credentials in a MongoDB URI for safe logging."""
    return re.sub(r"//([^:@/]+:[^@/]+)@", "//***@", uri)


def get_db() -> Database:
    """Load .env, connect to MongoDB, and return the project database.

    Returns:
        A pymongo Database object for the skills_mirage database.

    Raises:
        RuntimeError: if MONGO_URI or MONGO_DB is not set, or if the
            server cannot be reached within the timeout.
    """
    load_dotenv(_ENV_PATH)
    uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("MONGO_DB", "skills_mirage_db")
    if not uri:
        raise RuntimeError(
            "MONGO_URI is not set. Add it to your .env file."
        )
    log.info("Connecting to MongoDB at %s (db=%s)", _mask_uri(uri), db_name)
    client: MongoClient = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # Trigger a connection to verify reachability.
    client.admin.command("ping")
    log.info("MongoDB connection established.")
    return client[db_name]
