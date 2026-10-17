"""Run the batch pipeline end to end: processing -> analytics -> serving.

Usage (repo root, venv active):
    python pipeline/run_pipeline.py                  # all steps, mode from config/pipeline.yaml
    python pipeline/run_pipeline.py --dry-run        # print the plan only
    python pipeline/run_pipeline.py --from trends_and_gap --to reskilling_lookup
    python pipeline/run_pipeline.py --only load_results_to_mongo
    PIPELINE_MODE=cluster python pipeline/run_pipeline.py

Every step is its own module (``python -m <module>``) and overwrites its output, so the
whole pipeline is safe to re-run. The run stops at the first failing step.
The Mongo loader needs the MongoDB container to be up.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.common.logging_setup import get_logger  # noqa: E402

logger = get_logger("run_pipeline")

# (name, module, what it produces)
STEPS: list[tuple[str, str, str]] = [
    ("process_jobs", "src.processing.process_jobs", "processed/jobs"),
    ("process_courses", "src.processing.process_courses", "processed/courses"),
    ("dashboard_stats", "src.analytics.dashboard_stats", "stats, top-N, city/role drill-downs"),
    ("trends_and_gap", "src.analytics.trends_and_gap", "hiring trends, skill trends, skill gap"),
    ("vulnerability_index", "src.analytics.vulnerability_index", "vulnerability role/region/table"),
    ("reskilling_lookup", "src.analytics.reskilling_lookup", "reskilling lookup tables"),
    ("serving_extras", "src.analytics.serving_extras", "latest_jobs, courses"),
    ("load_results_to_mongo", "src.analytics.load_results_to_mongo", "18 res_* Mongo collections"),
]
NAMES = [s[0] for s in STEPS]


def select_steps(first: str | None, last: str | None, only: str | None) -> list[tuple[str, str, str]]:
    """Return the steps to run for the given --from/--to/--only options (names validated)."""
    for n in (first, last, only):
        if n is not None and n not in NAMES:
            raise ValueError(f"Unknown step '{n}'. Choose from: {', '.join(NAMES)}")
    if only:
        return [s for s in STEPS if s[0] == only]
    lo = NAMES.index(first) if first else 0
    hi = NAMES.index(last) if last else len(STEPS) - 1
    if lo > hi:
        raise ValueError("--from comes after --to")
    return STEPS[lo : hi + 1]


def run_step(module: str) -> int:
    """Run one step as a subprocess from the repo root and return its exit code."""
    return subprocess.run([sys.executable, "-m", module], cwd=REPO_ROOT, env=os.environ.copy()).returncode


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the selected steps and return a process exit code."""
    ap = argparse.ArgumentParser(description="Run the Skills Mirage batch pipeline")
    ap.add_argument("--from", dest="first", choices=NAMES)
    ap.add_argument("--to", dest="last", choices=NAMES)
    ap.add_argument("--only", choices=NAMES)
    ap.add_argument("--dry-run", action="store_true", help="print the plan without running anything")
    args = ap.parse_args(argv)
    try:
        steps = select_steps(args.first, args.last, args.only)
    except ValueError as exc:
        logger.error("FAIL: %s", exc)
        return 2
    logger.info("Mode: %s | steps: %s", os.environ.get("PIPELINE_MODE", "(config/pipeline.yaml)"), ", ".join(s[0] for s in steps))
    if args.dry_run:
        for name, module, produces in steps:
            logger.info("[dry-run] %s -> python -m %s (%s)", name, module, produces)
        return 0
    started = time.time()
    for name, module, _ in steps:
        t0 = time.time()
        logger.info("=== %s ===", name)
        code = run_step(module)
        if code != 0:
            logger.error("FAIL: step %s exited with code %d; stopping", name, code)
            return code
        logger.info("%s finished in %.1f s", name, time.time() - t0)
    logger.info("Pipeline finished in %.1f s", time.time() - started)
    return 0


if __name__ == "__main__":
    sys.exit(main())
