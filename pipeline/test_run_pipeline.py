"""Tests for the pipeline step selection (run: pytest pipeline)."""
import pytest

from pipeline import run_pipeline as rp


def test_all_steps_by_default():
    assert [s[0] for s in rp.select_steps(None, None, None)] == rp.NAMES


def test_range_and_only():
    assert [s[0] for s in rp.select_steps("trends_and_gap", "reskilling_lookup", None)] == [
        "trends_and_gap", "vulnerability_index", "reskilling_lookup"]
    assert [s[0] for s in rp.select_steps(None, None, "serving_extras")] == ["serving_extras"]


def test_bad_order_and_name():
    with pytest.raises(ValueError):
        rp.select_steps("serving_extras", "process_jobs", None)
    with pytest.raises(ValueError):
        rp.select_steps("nope", None, None)


def test_dry_run_exit_code_and_failure_stops(monkeypatch):
    assert rp.main(["--dry-run"]) == 0
    calls = []
    monkeypatch.setattr(rp, "run_step", lambda m: (calls.append(m), 1 if m.endswith("process_courses") else 0)[1])
    assert rp.main([]) == 1
    assert len(calls) == 2  # stopped right after the failing second step
