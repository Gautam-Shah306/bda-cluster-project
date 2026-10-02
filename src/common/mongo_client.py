"""MongoDB client module."""
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

from src.common.logging_setup import get_logger

logger = get_logger("mongo_client")

# Load .env file from the repo root
repo_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=repo_root / ".env", override=False)

# Keep a global client to reuse connections
_client: MongoClient | None = None

def get_db() -> Database:
    """Initialize and return a MongoDB Database instance.
    
    Loads configuration from environment variables MONGO_URI and MONGO_DB,
    falling back to values in .env. Fails with a clear error if they are missing.
    Pings the database to ensure connectivity.
    
    Returns:
        pymongo.database.Database: The database instance.
        
    Raises:
        ValueError: If MONGO_URI or MONGO_DB are not set.
        Exception: If the connection ping fails.
    """
    global _client
    
    mongo_uri = os.environ.get("MONGO_URI")
    mongo_db_name = os.environ.get("MONGO_DB")
    
    if not mongo_uri or not mongo_db_name:
        raise ValueError("MONGO_URI and MONGO_DB environment variables must be set.")
        
    if _client is None:
        try:
            _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Ping the server
            _client.admin.command('ping')
            
            # Mask the URI for logging
            masked_uri = mongo_uri
            if "@" in mongo_uri:
                protocol_part = mongo_uri.split("://", 1)[0]
                host_part = mongo_uri.rsplit("@", 1)[1]
                masked_uri = f"{protocol_part}://***@{host_part}"
                
            logger.info("Successfully connected to MongoDB at %s, database: %s", masked_uri, mongo_db_name)
        except Exception as e:
            logger.error("FAIL: Failed to connect to MongoDB: %s", e)
            _client = None
            raise
            
    return _client[mongo_db_name]
