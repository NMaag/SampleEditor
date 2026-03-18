from pathlib import Path

from sample_editor.core.config import (
    DEFAULT_CONFIG_NAME,
    get_default_config_path,
    load_config,
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
