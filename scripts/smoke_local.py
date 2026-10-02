"""Smoke test script to verify local Spark configuration."""
import os
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# Add repo root to sys.path so it can be run from anywhere without PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.common.config import get_path, get_config, get_mode
from src.common.logging_setup import get_logger
from src.common.spark_session import get_spark

logger = get_logger("smoke_local")

def main() -> None:
    """Run the smoke test."""
    if get_mode() != "local":
        logger.error("FAIL: This smoke test can only be run in local mode.")
        sys.exit(1)
        
    spark = None
    try:
        config = get_config()
        logger.info("Loaded config.")
        
        # Print resolved paths
        for path_name in config.get("paths", {}):
            logger.info("Resolved path '%s': %s", path_name, get_path(path_name))
            
        spark = get_spark("smoke_test")
        
        # Build 3-row in-memory DF
        data = [("A", 1), ("B", 2), ("C", 3)]
        columns = ["letter", "number"]
        df = spark.createDataFrame(data, columns)
        
        smoke_path = get_path("smoke_test")
        logger.info("Writing smoke test data to: %s", smoke_path)
        
        df.write.mode("overwrite").parquet(smoke_path)
        
        read_df = spark.read.parquet(smoke_path)
        count = read_df.count()
        
        if count == 3:
            logger.info("PASS: Read back 3 rows.")
        else:
            logger.error("FAIL: Expected 3 rows, got %d", count)
            sys.exit(1)
            
    except Exception as e:
        logger.error("FAIL: Exception occurred: %s", e)
        sys.exit(1)
    finally:
        if spark is not None:
            spark.stop()
        
        # Clean up smoke_test directory
        try:
            smoke_uri = get_path("smoke_test")
            parsed = urllib.parse.urlparse(smoke_uri)
            smoke_test_dir = Path(urllib.request.url2pathname(parsed.path))
            
            if smoke_test_dir.exists():
                shutil.rmtree(smoke_test_dir)
                logger.info("Cleaned up smoke_test directory.")
        except Exception as e:
            logger.warning("Failed to clean up smoke_test: %s", e)

if __name__ == "__main__":
    main()
