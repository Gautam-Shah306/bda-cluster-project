"""Analytics: Dashboard statistics.

Known differences from reference: Python's collections.Counter breaks ties
by first appearance. Since Spark has no inherent row order, we break ties
deterministically by sorting by count DESC, then by value ASC.
"""
import sys
from pathlib import Path

# Add repo root to sys.path so it can be run from anywhere without PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from pyspark.sql import functions as F, Window

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.spark_session import get_spark

logger = get_logger("dashboard_stats")

def main() -> None:
    spark = None
    try:
        input_uri = get_path("processed/jobs")
        analytics_base = get_path("analytics").rstrip("/")
        
        spark = get_spark("dashboard_stats")
        logger.info("Reading processed jobs from: %s", input_uri)
        
        try:
            df = spark.read.parquet(input_uri)
        except Exception as e:
            if "Path does not exist" in str(e):
                logger.error("FAIL: Input path does not exist: %s", input_uri)
                sys.exit(1)
            raise

        # 1. stats
        total_jobs = df.count()
        
        top_city_rows = df.groupBy("city").count().orderBy(F.desc("count"), F.asc("city")).limit(1).collect()
        top_city_val = top_city_rows[0]["city"] if top_city_rows else "N/A"
        
        skills_rows = df.select(F.explode("skills").alias("skill")).groupBy("skill").count().orderBy(F.desc("count"), F.asc("skill")).limit(1).collect()
        top_skill_val = skills_rows[0]["skill"] if skills_rows else "N/A"
        
        role_rows = df.groupBy("title").count().orderBy(F.desc("count"), F.asc("title")).limit(1).collect()
        top_role_val = role_rows[0]["title"] if role_rows else "N/A"
        
        stats_df = spark.createDataFrame([{
            "total_jobs": total_jobs,
            "top_city": top_city_val,
            "most_in_demand_skill": top_skill_val,
            "most_common_role": top_role_val
        }])
        
        # 2. top_cities
        top_cities_df = df.filter(F.col("city") != "") \
            .groupBy(F.col("city").alias("name")) \
            .agg(F.count("*").alias("demand")) \
            .orderBy(F.desc("demand"), F.asc("name")) \
            .limit(10)
            
        # 3. top_roles
        top_roles_df = df.withColumn("trimmed_title", F.trim(F.col("title"))) \
            .filter(F.col("trimmed_title") != "") \
            .groupBy(F.col("trimmed_title").alias("role")) \
            .agg(F.count("*").alias("count")) \
            .orderBy(F.desc("count"), F.asc("role")) \
            .limit(10)
            
        # 4. industry_distribution
        company_col = F.when((F.col("company").isNull()) | (F.col("company") == ""), "Unknown").otherwise(F.col("company"))
        industry_df = df.withColumn("company_trimmed", F.trim(company_col)) \
            .filter(F.col("company_trimmed") != "") \
            .groupBy(F.col("company_trimmed").alias("name")) \
            .agg(F.count("*").alias("value")) \
            .orderBy(F.desc("value"), F.asc("name")) \
            .limit(5)
            
        # 5. city_roles
        cr_base = df.withColumn("city_key", F.lower(F.trim(F.col("city")))) \
            .withColumn("name", F.trim(F.col("title"))) \
            .filter(F.col("name") != "")
            
        cr_counts = cr_base.groupBy("city_key", "name").agg(F.count("*").alias("value"))
        cr_window = Window.partitionBy("city_key").orderBy(F.desc("value"), F.asc("name"))
        city_roles_df = cr_counts.withColumn("rank", F.row_number().over(cr_window)) \
            .filter(F.col("rank") <= 10)
            
        # 6. role_cities
        rc_base = df.withColumn("role_key", F.lower(F.trim(F.col("title")))) \
            .filter(F.col("role_key") != "") \
            .withColumn("name", F.col("city")) \
            .filter(F.col("name") != "")
            
        rc_counts = rc_base.groupBy("role_key", "name").agg(F.count("*").alias("value"))
        rc_window = Window.partitionBy("role_key").orderBy(F.desc("value"), F.asc("name"))
        role_cities_df = rc_counts.withColumn("rank", F.row_number().over(rc_window)) \
            .filter(F.col("rank") <= 10)
            
        # Write outputs
        outputs = {
            "stats": stats_df,
            "top_cities": top_cities_df,
            "top_roles": top_roles_df,
            "industry_distribution": industry_df,
            "city_roles": city_roles_df,
            "role_cities": role_cities_df
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
