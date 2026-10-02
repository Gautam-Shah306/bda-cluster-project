"""Configuration module."""
import os
import yaml
from pathlib import Path

def get_repo_root() -> Path:
    """Returns the absolute path to the repository root."""
    return Path(__file__).resolve().parent.parent.parent

def get_config() -> dict:
    """Loads and returns the pipeline.yaml configuration."""
    config_path = get_repo_root() / "config" / "pipeline.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_path(name: str) -> str:
    """Returns the full URI/path for a named data location in the active mode."""
    config = get_config()
    mode = os.environ.get("PIPELINE_MODE", config.get("mode", "local"))
    
    if mode not in ("local", "cluster"):
        raise ValueError(f"Invalid mode: {mode}")
        
    paths = config.get("paths", {})
    if name not in paths and name != "smoke_test":
        raise KeyError(f"Unknown path name: {name}")
        
    sub_path = paths.get(name, name)
    
    if mode == "local":
        root = (get_repo_root() / config["local"]["root"]).resolve()
        return (root / sub_path).as_uri()
    else:
        root = config["cluster"]["root"]
        return f"{root.rstrip('/')}/{sub_path}"
