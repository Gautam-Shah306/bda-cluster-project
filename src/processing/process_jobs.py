"""PySpark job to normalise the raw Naukri jobs CSV.

Reads dataset/raw/jobs/naukri_jobs.csv (14 columns, ~22,979 rows) and
writes a Parquet dataset to dataset/processed/jobs/ with additional
derived columns:

  row_id       int   0-based CSV row position (used for skill-trend half-split)
  city         str   first comma-separated token of joblocation_address
  title        str   alias of jobtitle
  ai_mentions  array<str>  AI keywords found in lower-cased jobdescription
  skills       array<str>  parsed skills list

All original 14 columns are preserved as strings.
"""
from __future__ import annotations

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import ArrayType, StringType
from pyspark.sql.window import Window

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.spark_session import get_spark

log = get_logger(__name__)

_AI_KEYWORDS: list[str] = [
    "chatgpt", "openai", "generative ai", "machine learning",
    "automation", "llm", "gpt", "ai tools",
]


def _ai_mentions_expr(col_name: str) -> F.Column:
    """Return a Spark column expression that finds AI keywords in a string column."""
    lower_col = F.lower(F.col(col_name))
    keyword_arrays = [
        F.when(lower_col.contains(kw), F.lit(kw)).otherwise(F.lit(None))
        for kw in _AI_KEYWORDS
    ]
    return F.array_compact(F.array(*keyword_arrays)).cast(ArrayType(StringType()))


def _parse_skills_expr(col_name: str) -> F.Column:
    """Parse a skills string into an array of trimmed skill tokens."""
    raw = F.col(col_name)
    stripped = F.trim(F.regexp_replace(raw, r"^\[|\]$", ""))
    tokens = F.split(stripped, ",")
    trimmed = F.transform(tokens, lambda x: F.trim(x))
    return F.filter(trimmed, lambda x: F.length(x) > 0)


def run(spark: SparkSession) -> None:
    """Execute the jobs processing job."""
    raw_path = get_path("raw_jobs")
    out_path = get_path("processed_jobs")
    log.info("Reading raw jobs from: %s", raw_path)

    schema_cols = [
        "company", "education", "experience", "industry",
        "jobdescription", "jobid", "joblocation_address", "jobtitle",
        "numberofpositions", "payrate", "postdate", "site_name",
        "skills", "uniq_id",
    ]

    df = (
        spark.read
        .option("header", "true")
        .option("encoding", "UTF-8")
        .option("multiLine", "true")
        .option("escape", '"')
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
    df = df.withColumn("row_id", (F.row_number().over(w) - 1).cast("integer"))
    df = df.drop("_mid")

    df = df.withColumn("skills", _parse_skills_expr("skills"))
    df = df.withColumn(
        "city",
        F.trim(F.split(F.col("joblocation_address"), ",")[0]),
    )
    df = df.withColumn(
        "city",
        F.when(F.length(F.col("city")) == 0, F.lit("Unknown")).otherwise(F.col("city")),
    )
    df = df.withColumn("title", F.col("jobtitle"))
    df = df.withColumn("ai_mentions", _ai_mentions_expr("jobdescription"))

    count = df.count()
    log.info("Writing %d processed job rows to: %s", count, out_path)
    df.write.mode("overwrite").parquet(out_path)
    log.info("Successfully processed and wrote %d rows.", count)


if __name__ == "__main__":
    spark = get_spark("skills_mirage_process_jobs")
    try:
        run(spark)
    finally:
        spark.stop()
