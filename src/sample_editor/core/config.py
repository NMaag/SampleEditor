"""Configuration helpers for SampleEditor."""

from __future__ import annotations

import json
import logging
from pathlib import Path


DEFAULT_CONFIG_NAME = "sampleeditor_config.json"


def get_default_config_path(base_dir: Path) -> Path:
    """Return the default config location for an app directory."""
    return base_dir / DEFAULT_CONFIG_NAME


def get_default_paths(base_dir: Path) -> dict[str, Path]:
    """Return default input, output, mapping, and config paths."""
    return {
        "input_folder": base_dir / "infeed",
        "output_folder": base_dir / "outfeed",
        "csv_mapping_path": base_dir / "block_he_mapping.csv",
        "config_path": get_default_config_path(base_dir),
    }


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


def load_runtime_paths(base_dir: Path) -> dict[str, Path]:
    """Load configured app paths on top of defaults."""
    defaults = get_default_paths(base_dir)
    config = load_config(defaults["config_path"])

    return {
        "input_folder": Path(config.get("input_folder", defaults["input_folder"])),
        "output_folder": Path(config.get("output_folder", defaults["output_folder"])),
        "csv_mapping_path": Path(
            config.get("csv_mapping_path", defaults["csv_mapping_path"])
        ),
        "config_path": defaults["config_path"],
    }


def persist_runtime_paths(paths: dict[str, Path]) -> None:
    """Save user-editable paths to config."""
    save_config(
        paths["config_path"],
        {
            "input_folder": str(paths["input_folder"]),
            "output_folder": str(paths["output_folder"]),
            "csv_mapping_path": str(paths["csv_mapping_path"]),
        },
    )
