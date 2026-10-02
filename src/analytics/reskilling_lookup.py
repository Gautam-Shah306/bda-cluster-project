r"""Analytics: Reskilling lookup tables and skill index.

Rules implemented:
- reskilling_jobs: Excludes jobs with no valid skills. Contains row_id, title, company, city,
  skills_first10 (first 10 of original skills), and skills_lower_set (distinct lower-cased non-empty skills).
- reskilling_courses: Includes all courses. Contains course_id, name, source, url, tags_lower (as stored),
  and tags_lower_set (distinct non-empty items of skill_tags_lower).
- reskilling_skill_index: Maps (kind, skill) to ascending distinct array of ids (row_id for jobs, course_id for courses).

Matching tie rule (implemented by the API, using these tables): overlap count descending, 
tie-break by original source order (jobs by row_id ASC, courses by course_id ASC) which gives a stable sort.
"""
import sys
from pathlib import Path

# Add repo root to sys.path so it can be run from anywhere without PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from pyspark.sql import functions as F

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.spark_session import get_spark

logger = get_logger("reskilling_lookup")

def main() -> None:
    spark = None
    try:
        jobs_uri = get_path("processed/jobs")
        courses_uri = get_path("processed/courses")
        analytics_base = get_path("analytics").rstrip("/")
        
        spark = get_spark("reskilling_lookup")
        logger.info("Reading processed data from %s and %s", jobs_uri, courses_uri)
        
        try:
            jobs_df = spark.read.parquet(jobs_uri)
            courses_df = spark.read.parquet(courses_uri)
        except Exception as e:
            if "Path does not exist" in str(e):
                logger.error("FAIL: Input path does not exist: %s", e)
                sys.exit(1)
            raise

        # 1. reskilling_jobs
        skills_first10_expr = F.slice(F.coalesce(F.col("skills"), F.array()), 1, 10)
        skills_lower_expr = F.expr("transform(coalesce(skills, array()), x -> lower(trim(x)))")
        skills_valid_expr = F.expr("filter(skills_lower, x -> length(x) > 0)")
        skills_set_expr = F.array_distinct(skills_valid_expr)
        
        jobs_processed = jobs_df.withColumn("skills_lower", skills_lower_expr) \
                                .withColumn("skills_lower_set", skills_set_expr) \
                                .withColumn("skills_first10", skills_first10_expr)
                                
        reskilling_jobs = jobs_processed.filter(F.size(F.col("skills_lower_set")) > 0) \
            .select("row_id", "title", "company", "city", "skills_first10", "skills_lower_set")

        # 2. reskilling_courses
        tags_lower_expr = F.coalesce(F.col("skill_tags_lower"), F.array())
        tags_valid_expr = F.expr("filter(tags_lower, x -> length(trim(x)) > 0)")
        tags_set_expr = F.array_distinct(tags_valid_expr)
        
        reskilling_courses = courses_df.withColumn("tags_lower", tags_lower_expr) \
            .withColumn("tags_lower_set", tags_set_expr) \
            .select("course_id", "name", "source", "url", "tags_lower", "tags_lower_set")

        # 3. reskilling_skill_index
        jobs_exploded = reskilling_jobs.select(
            F.lit("job").alias("kind"),
            F.explode("skills_lower_set").alias("skill"),
            F.col("row_id").alias("id")
        )
        courses_exploded = reskilling_courses.select(
            F.lit("course").alias("kind"),
            F.explode("tags_lower_set").alias("skill"),
            F.col("course_id").alias("id")
        )
        
        union_index = jobs_exploded.unionByName(courses_exploded)
        
        reskilling_skill_index = union_index.groupBy("kind", "skill") \
            .agg(F.sort_array(F.collect_set("id")).alias("ids"))

        # Write outputs
        outputs = {
            "reskilling_jobs": reskilling_jobs,
            "reskilling_courses": reskilling_courses,
            "reskilling_skill_index": reskilling_skill_index
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
