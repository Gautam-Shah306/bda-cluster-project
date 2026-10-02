"""Courses processing module."""
import sys
from pathlib import Path

# Add repo root to sys.path so it can be run from anywhere without PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.spark_session import get_spark

logger = get_logger("process_courses")

def main() -> None:
    """Run the courses processing logic."""
    spark = None
    try:
        input_uri = get_path("raw/courses")
        output_uri = get_path("processed/courses")
        
        spark = get_spark("process_courses")
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
            
        # 1. Fill nulls with ""
        df = df.fillna("")
        
        # 2. skill_tags: array<string>, split on commas, trim, drop empty, keep original case
        skills_expr = F.expr(
            "filter(transform(split(skill_tags, ','), x -> trim(x)), x -> length(x) > 0)"
        )
        
        # 4. duration_weeks: cast to float then to int. Empty/invalid becomes null
        duration_expr = F.col("duration_weeks").cast("float").cast("int")
        
        # 5. syllabus_weeks: parse JSON array, fallback to empty array
        schema = ArrayType(StringType())
        syllabus_expr = F.coalesce(F.from_json(F.col("syllabus_weeks"), schema), F.array())
        
        # Build final DataFrame
        processed_df = df.withColumn("skill_tags", skills_expr) \
                         .withColumn("skill_tags_lower", F.expr("transform(skill_tags, x -> lower(x))")) \
                         .withColumn("duration_weeks", duration_expr) \
                         .withColumn("syllabus_weeks", syllabus_expr)
                         
        logger.info("Writing output to: %s", output_uri)
        processed_df.write.mode("overwrite").parquet(output_uri)
        
        # Log row count from written output
        written_df = spark.read.parquet(output_uri)
        count = written_df.count()
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
