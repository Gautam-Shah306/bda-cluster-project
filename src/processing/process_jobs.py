"""Jobs processing module."""
import sys
from pathlib import Path

# Add repo root to sys.path so it can be run from anywhere without PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from pyspark.sql import functions as F

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.spark_session import get_spark

logger = get_logger("process_jobs")

def main() -> None:
    """Run the jobs processing logic."""
    spark = None
    try:
        input_uri = get_path("raw/jobs")
        output_uri = get_path("processed/jobs")
        
        spark = get_spark("process_jobs")
        logger.info("Reading input from: %s", input_uri)
        
        try:
            df = spark.read.csv(
                input_uri,
                header=True,
                inferSchema=False,
                multiLine=True,
                quote='"',
                escape='"'
            )
        except Exception as e:
            if "Path does not exist" in str(e):
                logger.error("FAIL: Input path does not exist: %s", input_uri)
                sys.exit(1)
            raise
            
        # 1. Replace nulls with ""
        df = df.fillna("")
        
        # 2. skills: array<string>. Strip leading "[" and trailing "]", split on commas, trim, drop empty
        skills_expr = F.expr(
            "filter(transform(split(regexp_replace(skills, '^\\\\[|\\\\]$', ''), ','), x -> trim(x)), x -> length(x) > 0)"
        )
        
        # 3. city: text before first comma of joblocation_address, trimmed; "Unknown" if empty
        city_expr = F.trim(F.substring_index(F.col("joblocation_address"), ",", 1))
        city_expr = F.when((city_expr == "") | city_expr.isNull(), "Unknown").otherwise(city_expr)
        
        # 4. title: copy of jobtitle
        title_expr = F.col("jobtitle")
        
        # 5. ai_mentions
        keywords = [
            "chatgpt", "openai", "generative ai", "machine learning",
            "automation", "llm", "gpt", "ai tools"
        ]
        kw_conditions = []
        for kw in keywords:
            kw_conditions.append(F.when(F.lower(F.col("jobdescription")).contains(kw), F.lit(kw)))
        ai_mentions_expr = F.array_compact(F.array(*kw_conditions))
        
        # Build final DataFrame
        processed_df = df.withColumn("skills", skills_expr) \
                         .withColumn("city", city_expr) \
                         .withColumn("title", title_expr) \
                         .withColumn("ai_mentions", ai_mentions_expr)
                         
        logger.info("Writing output to: %s", output_uri)
        processed_df.write.mode("overwrite").parquet(output_uri)
        
        # Log row count
        count = df.count()
        logger.info("Successfully processed and wrote %d rows.", count)
        
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
