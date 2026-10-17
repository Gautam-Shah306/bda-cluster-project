"""Loads all 18 Parquet analytics result sets into MongoDB res_* collections.

Idempotent: drops and reloads each res_* collection in batches of 1000.
Safety: never touches 'users' or collections without 'res_' prefix.
"""
from __future__ import annotations

from pyspark.sql import SparkSession

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.mongo_client import get_db
from src.common.spark_session import get_spark

log = get_logger(__name__)

COLLECTION_MAP = {
    "stats": "res_stats",
    "top_cities": "res_top_cities",
    "top_roles": "res_top_roles",
    "industry_distribution": "res_industry",
    "city_roles": "res_city_roles",
    "role_cities": "res_role_cities",
    "hiring_trends": "res_hiring_trends",
    "skill_trend_years": "res_skill_years",
    "skill_trends": "res_skill_trends",
    "skill_gap": "res_skill_gap",
    "vulnerability_role_risks": "res_vuln_roles",
    "vulnerability_region_risks": "res_vuln_regions",
    "vulnerability_table": "res_vuln_table",
    "reskilling_jobs": "res_reskill_jobs",
    "reskilling_courses": "res_reskill_courses",
    "reskilling_skill_index": "res_reskill_index",
    "latest_jobs": "res_latest_jobs",
    "courses": "res_courses",
}


def load_one(spark: SparkSession, db, parquet_dir: str, collection_name: str) -> int:
    if not collection_name.startswith("res_"):
        raise ValueError(f"Safety abort: Refusing to load into non-res collection '{collection_name}'")

    path = f"{get_path('analytics')}/{parquet_dir}"
    log.info("Loading %s -> %s", path, collection_name)

    df = spark.read.parquet(path)
    coll = db[collection_name]
    coll.drop()

    batch: list[dict] = []
    total = 0

    for row in df.toLocalIterator():
        doc = row.asDict(recursive=True)
        batch.append(doc)
        if len(batch) >= 1000:
            coll.insert_many(batch)
            total += len(batch)
            batch = []

    if batch:
        coll.insert_many(batch)
        total += len(batch)

    coll.create_index("seq")
    log.info("Loaded %d documents into %s", total, collection_name)
    return total


def run(spark: SparkSession) -> None:
    db = get_db()
    total_loaded = 0
    for pdir, cname in COLLECTION_MAP.items():
        total_loaded += load_one(spark, db, pdir, cname)
    log.info("Finished loading %d collections into MongoDB.", len(COLLECTION_MAP))


if __name__ == "__main__":
    spark = get_spark("skills_mirage_load_mongo")
    try:
        run(spark)
    finally:
        spark.stop()
