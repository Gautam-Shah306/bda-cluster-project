"""Analytics: Load Parquet results to MongoDB."""
import sys
from pathlib import Path

# Add repo root to sys.path so it can be run from anywhere without PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from pymongo import ASCENDING, DESCENDING, IndexModel
from pyspark.sql import functions as F

from src.common.config import get_path
from src.common.logging_setup import get_logger
from src.common.mongo_client import get_db
from src.common.spark_session import get_spark

logger = get_logger("load_results_to_mongo")

def sort_spec_to_spark(df, sort_keys):
    """Convert a sort_keys list to Spark order expressions."""
    if not sort_keys:
        return df
    
    order_exprs = []
    for key in sort_keys:
        col_name, direction = key.split()
        if direction.lower() == "desc":
            order_exprs.append(F.desc(col_name))
        else:
            order_exprs.append(F.asc(col_name))
    return df.orderBy(*order_exprs)

def build_mongo_index(index_spec, unique=False):
    """Convert a tuple of fields to a pymongo IndexModel."""
    if not index_spec:
        return None
    keys = [(field, ASCENDING) for field in index_spec]
    return IndexModel(keys, unique=unique)

def main() -> None:
    spark = None
    try:
        analytics_base = get_path("analytics").rstrip("/")
        db = get_db()
        
        spark = get_spark("load_results_to_mongo")
        
        mappings = [
            ("stats", "res_stats", [], None, False),
            ("top_cities", "res_top_cities", ["demand desc", "name asc"], None, False),
            ("top_roles", "res_top_roles", ["count desc", "role asc"], None, False),
            ("industry_distribution", "res_industry", ["value desc", "name asc"], None, False),
            ("city_roles", "res_city_roles", ["city_key asc", "rank asc"], ("city_key", "rank"), False),
            ("role_cities", "res_role_cities", ["role_key asc", "rank asc"], ("role_key", "rank"), False),
            ("hiring_trends", "res_hiring_trends", ["month asc"], None, False),
            ("skill_trend_years", "res_skill_years", ["year desc"], None, False),
            ("skill_trends", "res_skill_trends", ["year_key asc", "kind asc", "rank asc"], ("year_key", "kind", "rank"), False),
            ("skill_gap", "res_skill_gap", ["rank asc"], None, False),
            ("vulnerability_role_risks", "res_vuln_roles", ["role_key asc"], ("role_key",), True),
            ("vulnerability_region_risks", "res_vuln_regions", ["risk desc", "city asc"], None, False),
            ("vulnerability_table", "res_vuln_table", ["rank asc"], None, False),
            ("reskilling_jobs", "res_reskill_jobs", ["row_id asc"], ("row_id",), True),
            ("reskilling_courses", "res_reskill_courses", ["course_id asc"], ("course_id",), True),
            ("reskilling_skill_index", "res_reskill_index", ["kind asc", "skill asc"], ("kind", "skill"), True),
            ("latest_jobs", "res_latest_jobs", ["postdate desc", "row_id asc"], ("row_id",), True),
            ("courses", "res_courses", ["course_id asc"], ("course_id",), True)
        ]
        
        failures = []
        
        for parquet_folder, coll_name, sort_keys, index_spec, unique in mappings:
            input_uri = f"{analytics_base}/{parquet_folder}"
            
            # Guardrail: never touch non-res_ collections
            if not coll_name.startswith("res_"):
                logger.error("Refusing to touch collection not starting with res_: %s", coll_name)
                continue
                
            try:
                df = spark.read.parquet(input_uri)
            except Exception as e:
                if "Path does not exist" in str(e):
                    logger.error("FAIL: Input path does not exist: %s", input_uri)
                    sys.exit(1)
                raise
                
            parquet_count = df.count()
            logger.info("Loading %s (Parquet rows: %d) into MongoDB %s...", parquet_folder, parquet_count, coll_name)
            
            # Sort
            df_sorted = sort_spec_to_spark(df, sort_keys)
            
            # Drop old collection
            db.drop_collection(coll_name)
            collection = db[coll_name]
            
            # Stream rows to driver and insert
            batch = []
            seq = 0
            for row in df_sorted.toLocalIterator():
                doc = row.asDict(recursive=True)
                doc["seq"] = seq
                batch.append(doc)
                seq += 1
                
                if len(batch) >= 1000:
                    collection.insert_many(batch)
                    batch = []
                    
            if batch:
                collection.insert_many(batch)
                
            # Create indexes
            idx_model = build_mongo_index(index_spec, unique)
            if idx_model:
                collection.create_indexes([idx_model])
                
            # Verify counts
            mongo_count = collection.count_documents({})
            logger.info("Collection %s: Parquet rows = %d, Mongo docs = %d", coll_name, parquet_count, mongo_count)
            
            if parquet_count != mongo_count:
                failures.append((coll_name, parquet_count, mongo_count))
                
        if failures:
            logger.error("FAIL: Count mismatches detected:")
            for f in failures:
                logger.error("  %s: Parquet=%d vs Mongo=%d", f[0], f[1], f[2])
            sys.exit(1)
            
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
