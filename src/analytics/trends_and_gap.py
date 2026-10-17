"""PySpark analytics job: trends and skill gap.

Produces 4 Parquet result sets:
  - analytics/hiring_trends: monthly posting counts
  - analytics/skill_trend_years: available years for filtering
  - analytics/skill_trends: rising and declining skills (half-split)
  - analytics/skill_gap: top 10 market demand vs course supply
"""
from __future__ import annotations

from collections import Counter
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

    # 1. hiring_trends: month = first 7 chars of postdate
    month_col = F.when(
        F.col("postdate").rlike(r"^\d{4}-\d{2}"),
        F.substring(F.col("postdate"), 1, 7)
    ).otherwise(F.lit("Recent"))

    hiring_counts = (
        jobs_df.withColumn("month", month_col)
        .groupBy("month").count()
        .orderBy("month")
    )
    w_m = Window.orderBy("month")
    hiring_df = (
        hiring_counts
        .withColumn("seq", F.row_number().over(w_m))
        .select(
            F.col("seq"),
            F.col("month"),
            F.col("count").alias("job_count"),
        )
    )
    hiring_df.write.mode("overwrite").parquet(f"{analytics_base}/hiring_trends")

    # 2. skill_trend_years
    year_col = F.when(
        F.col("postdate").rlike(r"^\d{4}"),
        F.substring(F.col("postdate"), 1, 4).cast("integer")
    ).otherwise(F.lit(None))

    years_df = (
        jobs_df.withColumn("year", year_col)
        .filter(F.col("year").isNotNull())
        .select("year")
        .distinct()
        .orderBy(F.desc("year"))
    )
    w_y = Window.orderBy(F.desc("year"))
    skill_years_df = years_df.withColumn("seq", F.row_number().over(w_y))
    skill_years_df.write.mode("overwrite").parquet(f"{analytics_base}/skill_trend_years")

    # 3. skill_trends (rising & declining skills)
    rows = (
        jobs_df.withColumn("year", year_col)
        .select("row_id", "year", "skills")
        .collect()
    )

    available_years = sorted({r["year"] for r in rows if r["year"] is not None}, reverse=True)
    all_filters = ["all"] + [str(y) for y in available_years]

    trend_docs = []
    seq_counter = 1

    for yf in all_filters:
        if yf == "all":
            subset = sorted(rows, key=lambda x: x["row_id"])
        else:
            y_int = int(yf)
            subset = sorted([r for r in rows if r["year"] == y_int], key=lambda x: x["row_id"])

        n = len(subset)
        if n < 2:
            continue
        mid = max(1, n // 2)
        prev_rows = subset[:mid]
        recent_rows = subset[mid:]

        prev_counts = Counter()
        for r in prev_rows:
            for s in r["skills"]:
                if s:
                    prev_counts[s] += 1

        recent_counts = Counter()
        for r in recent_rows:
            for s in r["skills"]:
                if s:
                    recent_counts[s] += 1

        all_skills = set(prev_counts.keys()) | set(recent_counts.keys())
        diffs = []
        for s in all_skills:
            diff = recent_counts[s] - prev_counts[s]
            diffs.append((s, diff, recent_counts[s] + prev_counts[s]))

        rising = sorted([d for d in diffs if d[1] > 0], key=lambda x: (-x[1], x[0]))[:10]
        declining = sorted([d for d in diffs if d[1] < 0], key=lambda x: (x[1], x[0]))[:10]

        for s, diff, _ in rising:
            trend_docs.append({
                "seq": seq_counter,
                "year_filter": yf,
                "type": "rising",
                "name": s,
                "growth": f"+{diff}",
                "decline": None,
                "color": "from-blue-500 to-cyan-400",
            })
            seq_counter += 1

        for s, diff, _ in declining:
            trend_docs.append({
                "seq": seq_counter,
                "year_filter": yf,
                "type": "declining",
                "name": s,
                "growth": None,
                "decline": str(diff),
                "color": "from-amber-500 to-rose-400",
            })
            seq_counter += 1

    if trend_docs:
        trends_df = spark.createDataFrame(trend_docs)
        trends_df.write.mode("overwrite").parquet(f"{analytics_base}/skill_trends")

    # 4. skill_gap: market demand vs course supply (lower-cased)
    job_skills_exploded = (
        jobs_df.select(F.explode("skills").alias("skill"))
        .filter(F.length(F.col("skill")) > 0)
        .withColumn("skill_lower", F.lower(F.col("skill")))
    )
    demand_df = (
        job_skills_exploded.groupBy("skill_lower")
        .agg(F.count("*").alias("market_demand"))
    )

    course_tags_exploded = (
        courses_df.select(F.explode("skill_tags").alias("tag"))
        .filter(F.length(F.col("tag")) > 0)
        .withColumn("tag_lower", F.lower(F.col("tag")))
    )
    supply_df = (
        course_tags_exploded.groupBy("tag_lower")
        .agg(F.count("*").alias("training_supply"))
    )

    gap_joined = (
        demand_df.join(supply_df, demand_df["skill_lower"] == supply_df["tag_lower"], how="left")
        .fillna({"training_supply": 0})
        .withColumn("gap", F.col("market_demand") - F.col("training_supply"))
        .orderBy(F.desc("gap"), F.asc("skill_lower"))
        .limit(10)
    )

    w_gap = Window.orderBy(F.desc("gap"), F.asc("skill_lower"))
    gap_df = (
        gap_joined.withColumn("seq", F.row_number().over(w_gap))
        .select(
            F.col("seq"),
            F.col("skill_lower").alias("skill"),
            F.col("market_demand"),
            F.col("training_supply"),
            F.col("gap"),
        )
    )
    gap_df.write.mode("overwrite").parquet(f"{analytics_base}/skill_gap")
    log.info("Finished trends_and_gap successfully.")


if __name__ == "__main__":
    spark = get_spark("skills_mirage_trends_and_gap")
    try:
        run(spark)
    finally:
        spark.stop()
