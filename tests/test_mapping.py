from pathlib import Path

import pytest

from sample_editor.core.mapping import load_he_to_blockid_map, load_mapping_safe


def test_load_he_to_blockid_map_reads_expected_values(tmp_path: Path) -> None:
    csv_path = tmp_path / "mapping.csv"
    csv_path.write_text(
        "Block ID,HE Image ID\n"
        "BLOCK001,HE001\n"
        "BLOCK002,HE002\n",
        encoding="utf-8",
    )

    assert load_he_to_blockid_map(csv_path) == {
        "HE001": "BLOCK001",
        "HE002": "BLOCK002",
    }


def test_load_he_to_blockid_map_rejects_missing_headers(tmp_path: Path) -> None:
    csv_path = tmp_path / "mapping.csv"
    csv_path.write_text(
        "Wrong,Headers\n"
        "BLOCK001,HE001\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required headers"):
        load_he_to_blockid_map(csv_path)


def test_load_mapping_safe_returns_empty_dict_when_missing(tmp_path: Path) -> None:
    csv_path = tmp_path / "missing.csv"

    assert load_mapping_safe(csv_path) == {}
