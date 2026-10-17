"""Writers for scraped data: one dated folder per run, with cross-run de-duplication.

Scrapers run on a laptop, so they write to the LOCAL data root from
config/pipeline.yaml (``local.root``); scripts/load_to_hdfs.sh copies the result
to HDFS for cluster runs. Layout: ``<root>/raw/scraped_jobs/dt=YYYY-MM-DD/jobs.jsonl``.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

from src.common.config import get_config, get_repo_root
from src.common.logging_setup import get_logger

logger = get_logger("ingestion_storage")


def local_folder(path_name: str) -> Path:
    """Return the local folder for a named path in config/pipeline.yaml."""
    config = get_config()
    sub = config["paths"][path_name]
    return get_repo_root() / config["local"]["root"] / sub


def run_folder(path_name: str, day: str | None = None) -> Path:
    """Return (and create) today's ``dt=YYYY-MM-DD`` folder under a scraped path."""
    day = day or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    folder = local_folder(path_name) / f"dt={day}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def read_jsonl(path: Path) -> list[dict]:
    """Read a JSON-lines file; bad lines are logged and skipped."""
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                logger.warning("%s line %d is not valid JSON; skipped", path.name, n)
    return rows


def existing_keys(path_name: str, file_name: str, key_fn: Callable[[dict], tuple]) -> set[tuple]:
    """Collect de-duplication keys from every earlier run of a scraped path."""
    keys: set[tuple] = set()
    base = local_folder(path_name)
    if not base.exists():
        return keys
    for f in sorted(base.glob(f"dt=*/{file_name}")):
        keys.update(key_fn(r) for r in read_jsonl(f))
    return keys


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    """Write rows as JSON lines (UTF-8); return how many were written."""
    count = 0
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def job_key(row: dict) -> tuple:
    """De-duplication key for a scraped job (W12): title + company + location, lower-cased."""
    return tuple(str(row.get(k, "")).strip().lower() for k in ("jobtitle", "company", "joblocation_address"))


def course_key(row: dict) -> tuple:
    """De-duplication key for a scraped course: name + source (same as the reference)."""
    return tuple(str(row.get(k, "")).strip().lower() for k in ("name", "source"))
