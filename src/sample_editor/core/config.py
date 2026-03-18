"""Configuration helpers for SampleEditor."""

from __future__ import annotations

import json
import logging
from pathlib import Path


DEFAULT_CONFIG_NAME = "sampleeditor_config.json"


def get_default_config_path(base_dir: Path) -> Path:
    """Return the default config location for an app directory."""
    return base_dir / DEFAULT_CONFIG_NAME


def load_config(config_path: Path) -> dict:
    """Load configuration from disk, returning an empty dict on failure."""
    if config_path.is_file():
        try:
            with config_path.open("r", encoding="utf-8") as config_file:
                data = json.load(config_file)
            logging.info("Loaded config from %s", config_path)
            return data
        except Exception as exc:
            logging.error("Failed to read config %s: %s", config_path, exc)
    return {}


def save_config(config_path: Path, config: dict) -> None:
    """Persist configuration to disk."""
    try:
        with config_path.open("w", encoding="utf-8") as config_file:
            json.dump(config, config_file, indent=2)
        logging.info("Saved config to %s", config_path)
    except Exception as exc:
        logging.error("Failed to save config %s: %s", config_path, exc)

