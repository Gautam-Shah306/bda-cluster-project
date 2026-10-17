"""Apply the small, behaviour-neutral code cleanups listed in the F3 audit.

Usage (from the repo root): python scripts/apply_cleanups.py
Each edit is an exact string replacement that is skipped when already applied and
aborts (without writing) when the expected text is not found.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.common.logging_setup import get_logger  # noqa: E402

logger = get_logger("apply_cleanups")

EDITS: list[tuple[str, str, str]] = [
    (
        "src/api/routes/courses_routes.py",
        "from typing import List, Optional\n\nfrom fastapi import APIRouter, HTTPException, Query",
        "from typing import Optional\n\nfrom fastapi import APIRouter, Query",
    ),
    (
        "src/api/routes/courses_routes.py",
        'router = APIRouter(prefix="", tags=["Courses"])  # prefix is handled, wait, endpoints are /courses, /courses/stats etc. So prefix="/courses"',
        'router = APIRouter(prefix="", tags=["Courses"])  # full paths are written in the decorators',
    ),
    (
        "src/analytics/trends_and_gap.py",
        '"""Analytics: Hiring trends, skill trends, and skill gap.',
        'r"""Analytics: Hiring trends, skill trends, and skill gap.',
    ),
]


def apply_edit(rel: str, old: str, new: str) -> str:
    """Apply one replacement; return 'applied', 'already' or raise."""
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if new in text:
        return "already"
    if text.count(old) != 1:
        raise ValueError(f"{rel}: expected text not found exactly once")
    path.write_text(text.replace(old, new), encoding="utf-8")
    return "applied"


def main() -> None:
    """Run all edits, stopping at the first failure."""
    for rel, old, new in EDITS:
        try:
            logger.info("%s: %s", rel, apply_edit(rel, old, new))
        except (OSError, ValueError) as exc:
            logger.error("FAIL: %s", exc)
            sys.exit(1)


if __name__ == "__main__":
    main()
