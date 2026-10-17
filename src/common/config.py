"""Project configuration loader.

Reads config/pipeline.yaml and exposes helpers for resolving data paths in
both local and cluster (HDFS) modes.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from src.common.logging_setup import get_logger

log = get_logger(__name__)

_CONFIG_PATH = Path(__file__).parents[2] / "config" / "pipeline.yaml"
_config: dict[str, Any] | None = None


def get_repo_root() -> Path:
    """Return the absolute path to the repository root."""
    return Path(__file__).parents[2]


def get_config() -> dict[str, Any]:
    """Load and cache config/pipeline.yaml.

    Returns:
        Parsed YAML as a Python dict.

    Raises:
        FileNotFoundError: if pipeline.yaml does not exist.
    """
    global _config
    if _config is None:
        if not _CONFIG_PATH.exists():
            raise FileNotFoundError(f"Config file not found: {_CONFIG_PATH}")
        with _CONFIG_PATH.open(encoding="utf-8") as fh:
            _config = yaml.safe_load(fh)
        log.info("Loaded config from %s", _CONFIG_PATH)
    return _config


def get_mode() -> str:
    """Return the pipeline mode ('local' or 'cluster').

    The PIPELINE_MODE environment variable overrides the config file.

    Raises:
        ValueError: if the mode is not 'local' or 'cluster'.
    """
    mode = os.environ.get("PIPELINE_MODE") or get_config().get("mode", "local")
    if mode not in ("local", "cluster"):
        raise ValueError(f"PIPELINE_MODE must be 'local' or 'cluster', got: {mode!r}")
    return mode


def get_path(name: str) -> str:
    """Resolve a named path from the config to a URI string.

    In local mode returns a 'file:///' URI. In cluster mode returns an
    'hdfs://' URI. The caller can pass the URI directly to PySpark.

    Args:
        name: key under config.paths (e.g. 'processed_jobs', 'analytics').

    Returns:
        A URI string suitable for use with PySpark.

    Raises:
        KeyError: if the named path is not defined in config.paths.
    """
    cfg = get_config()
    mode = get_mode()
    paths = cfg.get("paths", {})
    if name not in paths:
        raise KeyError(f"Path '{name}' not defined in config.paths")
    relative = paths[name]
    if mode == "local":
        root = get_repo_root() / cfg["local"]["root"]
        absolute = (root / relative).resolve()
        return absolute.as_uri()  # file:///...
    else:
        root = cfg["cluster"]["root"].rstrip("/")
        return f"{root}/{relative}"
