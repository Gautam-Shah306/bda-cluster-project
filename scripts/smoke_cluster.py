"""Cluster smoke test: write and read a tiny Parquet dataset on HDFS through Spark on YARN.

Run inside the master container (scripts/cluster_smoke.sh does this):
    PIPELINE_MODE=cluster python scripts/smoke_cluster.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.common.config import get_mode, get_path  # noqa: E402
from src.common.logging_setup import get_logger  # noqa: E402
from src.common.spark_session import get_spark  # noqa: E402

logger = get_logger("smoke_cluster")


def main() -> None:
    """Run the smoke test; exit non-zero on failure."""
    if get_mode() != "cluster":
        logger.error("FAIL: this smoke test needs PIPELINE_MODE=cluster")
        sys.exit(1)
    spark = None
    try:
        spark = get_spark("smoke_cluster")
        target = get_path("smoke_test")
        logger.info("Writing to %s", target)
        spark.createDataFrame([("A", 1), ("B", 2), ("C", 3)], ["letter", "number"]).write.mode("overwrite").parquet(target)
        df = spark.read.parquet(target)
        count = df.count()
        total = df.groupBy().sum("number").collect()[0][0]
        logger.info("Read back %d rows, sum=%s, partitions=%d, master=%s", count, total, df.rdd.getNumPartitions(), spark.sparkContext.master)
        if count != 3 or total != 6:
            logger.error("FAIL: unexpected content")
            sys.exit(1)
        logger.info("PASS: Spark on YARN wrote and read Parquet on HDFS")
    except Exception as exc:
        logger.error("FAIL: %s", exc)
        sys.exit(1)
    finally:
        if spark is not None:
            spark.stop()


if __name__ == "__main__":
    main()
