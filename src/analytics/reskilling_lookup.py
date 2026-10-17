"""PySpark analytics job: precomputed lookup tables for reskilling engine.

Produces 3 Parquet result sets:
  - analytics/reskilling_jobs: all jobs with clean lookup fields
  - analytics/reskilling_courses: all courses with clean lookup fields
  - analytics/reskilling_skill_index: inverted index skill -> list of job row_ids
"""
from __future__ import annotations

from collections import defaultdict
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.spark_session import get_spark

log = get_logger(__name__)


def run(spark: SparkSession) -> None:
    jobs_path = get_path("processed_jobs")
    courses_path = get_path("processed_courses")
    analytics_base = get_path("analytics")

    jobs_df = spark.read.parquet(jobs_path)
    courses_df = spark.read.parquet(courses_path)

    # 1. reskilling_jobs
    w_j = Window.orderBy("row_id")
    reskill_jobs_df = (
        jobs_df
        .withColumn("seq", F.row_number().over(w_j))
        .select(
            F.col("seq"),
            F.col("row_id"),
            F.col("title"),
            F.col("company"),
            F.col("city").alias("location"),
            F.col("experience"),
            F.slice(F.col("skills"), 1, 10).alias("required_skills"),
        )
    )
    reskill_jobs_df.write.mode("overwrite").parquet(f"{analytics_base}/reskilling_jobs")

    # 2. reskilling_courses
    w_c = Window.orderBy("course_id")
    reskill_courses_df = (
        courses_df
        .withColumn("seq", F.row_number().over(w_c))
        .select(
            F.col("seq"),
            F.col("course_id"),
            F.col("name"),
            F.col("source"),
            F.col("url"),
            F.col("duration_weeks"),
            F.col("duration_int"),
            F.concat_ws(", ", F.col("skill_tags")).alias("skill_tags_lower_str"),
        )
    )
    reskill_courses_df.write.mode("overwrite").parquet(f"{analytics_base}/reskilling_courses")

    # 3. reskilling_skill_index: skill -> list[row_id]
    exploded = (
        jobs_df.select("row_id", F.explode("skills").alias("skill"))
        .filter(F.length(F.col("skill")) > 0)
        .withColumn("skill_lower", F.lower(F.col("skill")))
    )
    index_df = (
        exploded.groupBy("skill_lower")
        .agg(F.collect_list("row_id").alias("job_ids_list"))
        .orderBy("skill_lower")
    )
    w_i = Window.orderBy("skill_lower")
    skill_index_df = (
        index_df
        .withColumn("seq", F.row_number().over(w_i))
        .select(
            F.col("seq"),
            F.col("skill_lower").alias("skill"),
            F.col("job_ids_list"),
        )
    )
    skill_index_df.write.mode("overwrite").parquet(f"{analytics_base}/reskilling_skill_index")

    log.info("Finished reskilling_lookup successfully.")


if __name__ == "__main__":
    spark = get_spark("skills_mirage_reskilling_lookup")
    try:
        run(spark)
    finally:
        spark.stop()
