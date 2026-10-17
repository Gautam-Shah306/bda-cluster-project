"""PySpark analytics job: latest jobs and full course table.

Produces 2 Parquet result sets:
  - analytics/latest_jobs: newest 50 jobs with raw skills string
  - analytics/courses: all 398 courses with clean fields
"""
from __future__ import annotations

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.spark_session import get_spark

log = get_logger(__name__)


def run(spark: SparkSession) -> None:
    raw_jobs_path = get_path("raw_jobs")
    courses_path = get_path("processed_courses")
    analytics_base = get_path("analytics")

    # 1. latest_jobs from raw CSV
    raw_df = (
        spark.read
        .option("header", "true")
        .option("encoding", "UTF-8")
        .option("multiLine", "true")
        .option("escape", '"')
        .csv(raw_jobs_path)
        .fillna("")
    )

    location_col = F.trim(F.split(F.col("joblocation_address"), ",")[0])

    latest_50 = (
        raw_df.filter(F.length(F.col("jobtitle")) > 0)
        .orderBy(F.desc("postdate"))
        .limit(50)
    )

    w = Window.orderBy(F.desc("postdate"))
    latest_df = (
        latest_50
        .withColumn("seq", F.row_number().over(w))
        .select(
            F.col("seq"),
            F.col("jobtitle"),
            F.col("company"),
            location_col.alias("location"),
            F.col("skills"),
            F.col("experience"),
            F.col("postdate"),
        )
    )
    latest_df.write.mode("overwrite").parquet(f"{analytics_base}/latest_jobs")

    # 2. courses from processed/courses Parquet
    processed_courses_df = spark.read.parquet(courses_path)
    w_c = Window.orderBy("course_id")
    courses_out = (
        processed_courses_df
        .withColumn("seq", F.row_number().over(w_c))
        .select(
            F.col("seq"),
            F.col("course_id"),
            F.col("name"),
            F.col("source"),
            F.col("domain"),
            F.col("url"),
            F.col("institution"),
            F.col("duration_weeks"),
            F.col("difficulty"),
            F.concat_ws(", ", F.col("skill_tags_orig")).alias("skill_tags_orig_str"),
            F.col("syllabus_weeks"),
        )
    )
    courses_out.write.mode("overwrite").parquet(f"{analytics_base}/courses")

    log.info("Finished serving_extras successfully.")


if __name__ == "__main__":
    spark = get_spark("skills_mirage_serving_extras")
    try:
        run(spark)
    finally:
        spark.stop()
