from pathlib import Path

from sample_editor.core.config import (
    DEFAULT_CONFIG_NAME,
    get_default_config_path,
    get_default_paths,
    load_config,
    load_runtime_paths,
    persist_runtime_paths,
    save_config,
)


def test_get_default_config_path_uses_expected_filename() -> None:
    base_dir = Path("C:/temp/sample-editor")

    assert get_default_config_path(base_dir) == base_dir / DEFAULT_CONFIG_NAME


def test_save_and_load_config_round_trip(tmp_path: Path) -> None:
    config_path = tmp_path / DEFAULT_CONFIG_NAME
    config = {
        "input_folder": "C:/input",
        "output_folder": "C:/output",
        "csv_mapping_path": "C:/mapping.csv",
    }

    save_config(config_path, config)

    assert load_config(config_path) == config


def test_load_config_returns_empty_dict_when_missing(tmp_path: Path) -> None:
    missing_path = tmp_path / DEFAULT_CONFIG_NAME

    assert load_config(missing_path) == {}


def test_get_default_paths_returns_expected_structure(tmp_path: Path) -> None:
    paths = get_default_paths(tmp_path)

    assert paths["input_folder"] == tmp_path / "infeed"
    assert paths["output_folder"] == tmp_path / "outfeed"
    assert paths["csv_mapping_path"] == tmp_path / "block_he_mapping.csv"
    assert paths["config_path"] == tmp_path / DEFAULT_CONFIG_NAME


def test_load_and_persist_runtime_paths_round_trip(tmp_path: Path) -> None:
    paths = {
        "input_folder": tmp_path / "custom-in",
        "output_folder": tmp_path / "custom-out",
        "csv_mapping_path": tmp_path / "custom.csv",
        "config_path": tmp_path / DEFAULT_CONFIG_NAME,
    }

    persist_runtime_paths(paths)
    loaded = load_runtime_paths(tmp_path)

    assert loaded["input_folder"] == paths["input_folder"]
    assert loaded["output_folder"] == paths["output_folder"]
    assert loaded["csv_mapping_path"] == paths["csv_mapping_path"]
