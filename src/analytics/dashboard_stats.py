"""PySpark analytics job: dashboard statistics and distributions.

Produces 6 Parquet result sets:
  - analytics/stats: overall counts and top items (1 doc)
  - analytics/top_cities: top 10 hiring cities
  - analytics/top_roles: top 10 job roles
  - analytics/industry_distribution: top 5 companies as industry proxy
  - analytics/city_roles: role counts per city (top 10 per city)
  - analytics/role_cities: city counts per role (top 10 per role)
"""
from __future__ import annotations

import json
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.spark_session import get_spark

log = get_logger(__name__)


def run(spark: SparkSession) -> None:
    jobs_path = get_path("processed_jobs")
    analytics_base = get_path("analytics")
    log.info("Reading processed jobs from: %s", jobs_path)

    df = spark.read.parquet(jobs_path)
    total_jobs = df.count()

    # top city
    city_counts = df.filter(F.length(F.col("city")) > 0).groupBy("city").count().orderBy(F.desc("count"), F.asc("city"))
    top_city_row = city_counts.first()
    top_city = top_city_row["city"] if top_city_row else "N/A"

    # top role
    role_counts = df.filter(F.length(F.col("title")) > 0).groupBy("title").count().orderBy(F.desc("count"), F.asc("title"))
    top_role_row = role_counts.first()
    most_common_role = top_role_row["title"] if top_role_row else "N/A"

    # most in demand skill
    skills_df = df.select(F.explode("skills").alias("skill")).filter(F.length(F.col("skill")) > 0)
    skill_counts = skills_df.groupBy("skill").count().orderBy(F.desc("count"), F.asc("skill"))
    top_skill_row = skill_counts.first()
    most_in_demand_skill = top_skill_row["skill"] if top_skill_row else "N/A"

    # 1. stats
    stats_data = [{
        "seq": 1,
        "total_jobs": total_jobs,
        "top_city": top_city,
        "most_in_demand_skill": most_in_demand_skill,
        "most_common_role": most_common_role,
    }]
    stats_df = spark.createDataFrame(stats_data)
    stats_df.write.mode("overwrite").parquet(f"{analytics_base}/stats")

    # 2. top_cities (top 10)
    w = Window.orderBy(F.desc("count"), F.asc("city"))
    top_cities_df = (
        city_counts
        .filter(F.col("city") != "Unknown")
        .limit(10)
        .withColumn("seq", F.row_number().over(w))
        .select(
            F.col("seq"),
            F.col("city").alias("name"),
            F.col("count").alias("demand"),
        )
    )
    top_cities_df.write.mode("overwrite").parquet(f"{analytics_base}/top_cities")

    # 3. top_roles (top 10)
    w_role = Window.orderBy(F.desc("count"), F.asc("title"))
    top_roles_df = (
        role_counts
        .limit(10)
        .withColumn("seq", F.row_number().over(w_role))
        .select(
            F.col("seq"),
            F.col("title").alias("role"),
            F.col("count"),
        )
    )
    top_roles_df.write.mode("overwrite").parquet(f"{analytics_base}/top_roles")

    # 4. industry_distribution (top 5 companies as proxy)
    company_counts = (
        df.filter(F.length(F.col("company")) > 0)
        .groupBy("company").count()
        .orderBy(F.desc("count"), F.asc("company"))
        .limit(5)
    )
    w_comp = Window.orderBy(F.desc("count"), F.asc("company"))
    industry_df = (
        company_counts
        .withColumn("seq", F.row_number().over(w_comp))
        .select(
            F.col("seq"),
            F.col("company").alias("name"),
            F.col("count").alias("value"),
        )
    )
    industry_df.write.mode("overwrite").parquet(f"{analytics_base}/industry_distribution")

    # 5. city_roles: breakdown of roles per city
    city_role_counts = (
        df.filter((F.length(F.col("city")) > 0) & (F.length(F.col("title")) > 0))
        .groupBy("city", "title")
        .count()
    )
    w_cr = Window.partitionBy("city").orderBy(F.desc("count"), F.asc("title"))
    w_cr_seq = Window.orderBy("city", F.desc("count"))
    city_roles_df = (
        city_role_counts
        .withColumn("rank", F.row_number().over(w_cr))
        .filter(F.col("rank") <= 10)
        .withColumn("seq", F.row_number().over(w_cr_seq))
        .select(
            F.col("seq"),
            F.col("city"),
            F.lower(F.col("city")).alias("city_lower"),
            F.col("title").alias("role"),
            F.col("count"),
        )
    )
    city_roles_df.write.mode("overwrite").parquet(f"{analytics_base}/city_roles")

    # 6. role_cities: breakdown of cities per role
    role_city_counts = (
        df.filter((F.length(F.col("title")) > 0) & (F.length(F.col("city")) > 0))
        .groupBy("title", "city")
        .count()
    )
    w_rc = Window.partitionBy("title").orderBy(F.desc("count"), F.asc("city"))
    w_rc_seq = Window.orderBy("title", F.desc("count"))
    role_cities_df = (
        role_city_counts
        .withColumn("rank", F.row_number().over(w_rc))
        .filter(F.col("rank") <= 10)
        .withColumn("seq", F.row_number().over(w_rc_seq))
        .select(
            F.col("seq"),
            F.col("title").alias("role"),
            F.lower(F.col("title")).alias("role_lower"),
            F.col("city"),
            F.col("count"),
        )
    )
    role_cities_df.write.mode("overwrite").parquet(f"{analytics_base}/role_cities")
    log.info("Finished dashboard_stats successfully.")


if __name__ == "__main__":
    spark = get_spark("skills_mirage_dashboard_stats")
    try:
        run(spark)
    finally:
        spark.stop()
