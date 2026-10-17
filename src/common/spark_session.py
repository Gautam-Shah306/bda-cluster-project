"""PySpark session factory for the Skills Mirage pipeline.

Provides a single get_spark() function that returns a SparkSession configured
for either local or cluster (YARN) mode, driven by the pipeline config.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from pyspark.sql import SparkSession

from src.common.config import get_config, get_mode
from src.common.logging_setup import get_logger

log = get_logger(__name__)


def get_spark(app_name: str) -> SparkSession:
    """Create or retrieve a SparkSession for the given application name.

    In local mode, runs as local[*] with no Hive support.
    In cluster mode, connects to YARN and enables Hive support.

    Args:
        app_name: A short human-readable name for the Spark application.

    Returns:
        A configured SparkSession.
    """
    mode = get_mode()
    cfg = get_config()
    spark_cfg = cfg.get("spark", {})

    python_exec = sys.executable
    os.environ.setdefault("PYSPARK_PYTHON", python_exec)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", python_exec)

    builder = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.driver.memory", spark_cfg.get("driver_memory", "2g"))
        .config("spark.executor.memory", spark_cfg.get("executor_memory", "2g"))
        .config("spark.sql.shuffle.partitions", str(spark_cfg.get("sql_shuffle_partitions", 8)))
    )

    if mode == "local":
        builder = builder.master("local[*]")
        log.info("Starting Spark in local mode for app: %s", app_name)
    else:
        master = cfg["cluster"].get("spark_master", "yarn")
        builder = (
            builder
            .master(master)
            .enableHiveSupport()
        )
        log.info("Starting Spark on %s for app: %s", master, app_name)

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    log.info("SparkSession ready: %s", spark.version)
    return spark
