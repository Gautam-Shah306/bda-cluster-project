"""PySpark job to normalise the raw courses CSV.

Reads dataset/raw/courses/courses.csv (9 columns, 398 rows) and writes
a Parquet dataset to dataset/processed/courses/ with additional columns:

  course_id       int   0-based row position
  skill_tags      array<str>  lower-cased, trimmed tags from skill_tags string
  skill_tags_orig array<str>  original-case tags
  duration_int    int   integer weeks (None if unparseable)
  syllabus_list   array<str>  parsed syllabus_weeks JSON list

Original 9 columns are preserved.
"""
from __future__ import annotations

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import ArrayType, IntegerType, StringType
from pyspark.sql.window import Window

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.spark_session import get_spark

log = get_logger(__name__)


def run(spark: SparkSession) -> None:
    """Execute the courses processing job."""
    raw_path = get_path("raw_courses")
    out_path = get_path("processed_courses")
    log.info("Reading raw courses from: %s", raw_path)

    schema_cols = [
        "name", "source", "domain", "url", "institution",
        "duration_weeks", "difficulty", "skill_tags", "syllabus_weeks",
    ]

    df = (
        spark.read
        .option("header", "true")
        .option("encoding", "UTF-8")
        .csv(raw_path)
        .fillna("")
    )

    existing = set(df.columns)
    for col in schema_cols:
        if col not in existing:
            df = df.withColumn(col, F.lit(""))
    df = df.select(*schema_cols)

    df = df.withColumn("_mid", F.monotonically_increasing_id())
    w = Window.orderBy("_mid")
    df = df.withColumn("course_id", (F.row_number().over(w) - 1).cast("integer"))
    df = df.drop("_mid")

    tags_raw = F.split(F.col("skill_tags"), ",")
    df = df.withColumn("skill_tags_orig", F.filter(F.transform(tags_raw, F.trim), lambda x: F.length(x) > 0))
    df = df.withColumn("skill_tags", F.transform(F.col("skill_tags_orig"), F.lower))

    df = df.withColumn(
        "duration_int",
        F.regexp_extract(F.col("duration_weeks"), r"(\d+)", 1).cast(IntegerType()),
    )

    df = df.withColumn(
        "syllabus_list",
        F.when(
            F.col("syllabus_weeks").startswith("["),
            F.from_json(F.col("syllabus_weeks"), ArrayType(StringType())),
        ).otherwise(
            F.filter(
                F.transform(F.split(F.col("syllabus_weeks"), ","), F.trim),
                lambda x: F.length(x) > 0,
            )
        ),
    )

    count = df.count()
    log.info("Writing %d processed course rows to: %s", count, out_path)
    df.write.mode("overwrite").parquet(out_path)
    log.info("Successfully processed and wrote %d rows.", count)


if __name__ == "__main__":
    spark = get_spark("skills_mirage_process_courses")
    try:
        run(spark)
    finally:
        spark.stop()
