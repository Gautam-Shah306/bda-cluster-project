"""Analytics: Hiring trends, skill trends, and skill gap.

Rules implemented:
- hiring_trends: month key = first 7 characters of postdate if they match ^\d{4}-\d{2}$, else "Recent". Sorted by key ASC.
- skill_trend_years: unique years = first 4 characters of postdate when all four are digits (as int). Sorted DESC.
- skill_trends(year): keeps jobs whose year equals the given year (or all jobs for "all"). Kept jobs split by row_id order into previous (first mid jobs) and recent (rest, mid = max(1, n // 2)). Skills are case-sensitive. change = recent_count - previous_count. Rising = top 10 with change > 0. Declining = last 10 with change < 0 (kept in sorted order). 
- skill_gap: demand = count of lower-cased job skill over ALL jobs. supply = count of tag in courses skill_tags_lower. gap = demand - supply. Top 10 by gap DESC.

Known differences from reference:
Spark has no inherent row order, so tie-breaking (which reference Counter does by first-seen) is done deterministically: count/gap/change DESC, then skill name ASC.
"""
import sys
from pathlib import Path
from collections import defaultdict

# Add repo root to sys.path so it can be run from anywhere without PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from pyspark.sql import functions as F, Window

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.spark_session import get_spark

logger = get_logger("trends_and_gap")

def main() -> None:
    spark = None
    try:
        jobs_uri = get_path("processed/jobs")
        courses_uri = get_path("processed/courses")
        analytics_base = get_path("analytics").rstrip("/")
        
        spark = get_spark("trends_and_gap")
        logger.info("Reading processed data from %s and %s", jobs_uri, courses_uri)
        
        try:
            jobs_df = spark.read.parquet(jobs_uri)
            courses_df = spark.read.parquet(courses_uri)
        except Exception as e:
            if "Path does not exist" in str(e):
                logger.error("FAIL: Input path does not exist: %s", e)
                sys.exit(1)
            raise

        # 1. hiring_trends
        first_7 = F.substring(F.col("postdate"), 1, 7)
        month_expr = F.when(first_7.rlike(r"^\d{4}-\d{2}$"), first_7).otherwise("Recent")
        hiring_trends_df = jobs_df.withColumn("month", month_expr) \
            .groupBy("month").agg(F.count("*").alias("job_count")) \
            .orderBy(F.asc("month"))

        # 2. skill_trend_years
        first_4 = F.substring(F.col("postdate"), 1, 4)
        year_expr = F.when(first_4.rlike(r"^\d{4}$"), first_4.cast("int")).otherwise(None)
        jobs_year_df = jobs_df.withColumn("year", year_expr)
        
        skill_trend_years_df = jobs_year_df.filter(F.col("year").isNotNull()) \
            .select("year").distinct().orderBy(F.desc("year"))

        # 3. skill_trends
        yk_expr = F.when(F.col("year").isNotNull(), F.array(F.lit("all"), F.col("year").cast("string"))) \
                   .otherwise(F.array(F.lit("all")))
        st_base = jobs_year_df.withColumn("year_key", F.explode(yk_expr))
        
        window_yk = Window.partitionBy("year_key").orderBy("row_id")
        st_ranked = st_base.withColumn("rn", F.row_number().over(window_yk)) \
                           .withColumn("n", F.count("*").over(Window.partitionBy("year_key")))
        
        st_grouped = st_ranked.withColumn("mid", F.greatest(F.lit(1), F.floor(F.col("n") / 2))) \
                              .withColumn("group", F.when(F.col("rn") <= F.col("mid"), "previous").otherwise("recent"))

        st_skills = st_grouped.select("year_key", "group", F.explode("skills").alias("skill"))
        st_counts = st_skills.groupBy("year_key", "skill").agg(
            F.sum(F.when(F.col("group") == "recent", 1).otherwise(0)).alias("recent_count"),
            F.sum(F.when(F.col("group") == "previous", 1).otherwise(0)).alias("previous_count")
        ).withColumn("change", F.col("recent_count") - F.col("previous_count"))

        window_rising = Window.partitionBy("year_key").orderBy(F.desc("change"), F.asc("skill"))
        rising_df = st_counts.filter(F.col("change") > 0) \
            .withColumn("rank", F.row_number().over(window_rising)) \
            .filter(F.col("rank") <= 10) \
            .withColumn("kind", F.lit("rising")) \
            .select("year_key", "kind", "rank", F.col("skill").alias("name"), "change")

        window_bottom = Window.partitionBy("year_key").orderBy(F.asc("change"), F.desc("skill"))
        declining_filtered = st_counts.filter(F.col("change") < 0) \
            .withColumn("bottom_rank", F.row_number().over(window_bottom)) \
            .filter(F.col("bottom_rank") <= 10)

        declining_df = declining_filtered.withColumn("rank", F.row_number().over(window_rising)) \
            .withColumn("kind", F.lit("declining")) \
            .select("year_key", "kind", "rank", F.col("skill").alias("name"), "change")

        skill_trends_df = rising_df.unionByName(declining_df)

        bottom_whole = st_counts.withColumn("bottom_rank", F.row_number().over(window_bottom)) \
            .filter(F.col("bottom_rank") <= 10) \
            .filter(F.col("change") < 0)

        dec_1 = declining_filtered.select("year_key", "skill").collect()
        dec_2 = bottom_whole.select("year_key", "skill").collect()
        d1_map = defaultdict(set)
        d2_map = defaultdict(set)
        for row in dec_1: d1_map[row["year_key"]].add(row["skill"])
        for row in dec_2: d2_map[row["year_key"]].add(row["skill"])

        for yk in set(d1_map.keys()).union(set(d2_map.keys())):
            if d1_map[yk] != d2_map[yk]:
                logger.info("Ambiguity difference for year_key %s: filtered_first=%s, whole_first=%s", yk, d1_map[yk], d2_map[yk])
            else:
                logger.info("Ambiguity check for year_key %s: both readings yield identical declining sets.", yk)

        # 4. skill_gap
        demand_df = jobs_df.select(F.explode("skills").alias("raw_skill")) \
            .withColumn("skill", F.lower(F.col("raw_skill"))) \
            .groupBy("skill").agg(F.count("*").alias("market_demand"))

        supply_df = courses_df.select(F.explode("skill_tags_lower").alias("skill")) \
            .groupBy("skill").agg(F.count("*").alias("training_supply"))

        gap_base = demand_df.join(supply_df, "skill", "left").fillna({"training_supply": 0})
        gap_base = gap_base.withColumn("gap", F.col("market_demand") - F.col("training_supply"))

        window_gap = Window.orderBy(F.desc("gap"), F.asc("skill"))
        skill_gap_df = gap_base.withColumn("rank", F.row_number().over(window_gap)) \
            .filter(F.col("rank") <= 10) \
            .select("rank", "skill", "market_demand", "training_supply", "gap")

        # Write outputs
        outputs = {
            "hiring_trends": hiring_trends_df,
            "skill_trend_years": skill_trend_years_df,
            "skill_trends": skill_trends_df,
            "skill_gap": skill_gap_df
        }
        
        for name, out_df in outputs.items():
            out_path = f"{analytics_base}/{name}"
            out_df.write.mode("overwrite").parquet(out_path)
            
            written_df = spark.read.parquet(out_path)
            logger.info("Successfully wrote %d rows to %s", written_df.count(), out_path)
            
    except SystemExit:
        raise
    except Exception as e:
        logger.error("FAIL: Job failed with exception: %s", e)
        sys.exit(1)
    finally:
        if spark is not None:
            spark.stop()

if __name__ == "__main__":
    main()
