"""Spark session setup module."""
import os
import sys
from pyspark.sql import SparkSession
from src.common.config import get_config
from src.common.logging_setup import get_logger

logger = get_logger(__name__)

def get_spark(app_name: str | None = None) -> SparkSession:
    """Returns a configured SparkSession based on the active mode."""
    # Ensure PySpark uses the current Python executable
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    
    config = get_config()
    mode = os.environ.get("PIPELINE_MODE", config.get("mode", "local"))
    
    name = app_name or config.get("spark", {}).get("app_name", "SkillsMirage")
    
    builder = SparkSession.builder.appName(name)
    
    if mode == "local":
        master = config.get("spark", {}).get("local_master", "local[*]")
        shuffle_parts = str(config.get("spark", {}).get("shuffle_partitions", 2))
        builder = builder.master(master).config("spark.sql.shuffle.partitions", shuffle_parts)
    else:
        master = config.get("cluster", {}).get("spark_master", "yarn")
        builder = builder.master(master).enableHiveSupport()
        
    logger.info("Starting SparkSession with mode=%s, master=%s", mode, master)
    
    return builder.getOrCreate()
