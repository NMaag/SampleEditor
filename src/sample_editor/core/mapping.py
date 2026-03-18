"""CSV mapping helpers for SampleEditor."""

from __future__ import annotations

import csv
import logging
from pathlib import Path


REQUIRED_HEADERS = ("Block ID", "HE Image ID")


def load_he_to_blockid_map(csv_path: Path) -> dict[str, str]:
    """Load HE image IDs to block IDs from a CSV file."""
    mapping: dict[str, str] = {}

    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        headers = reader.fieldnames or []
        missing = [header for header in REQUIRED_HEADERS if header not in headers]
        if missing:
            raise ValueError(
                f"CSV mapping file missing required headers: {missing}"
            )

        for row_number, row in enumerate(reader, start=1):
            block_id = str(row.get("Block ID", "")).strip()
            he_id = str(row.get("HE Image ID", "")).strip()

            if not he_id or not block_id:
                logging.warning(
                    "Skipping incomplete row %s in mapping CSV: HE='%s' Block='%s'",
                    row_number,
                    he_id,
                    block_id,
                )
                continue

            if he_id in mapping:
                logging.warning(
                    "Duplicate HE Image ID '%s' in CSV at row %s; keeping first "
                    "value '%s'",
                    he_id,
                    row_number,
                    mapping[he_id],
                )
                continue

            mapping[he_id] = block_id

    return mapping


def load_mapping_safe(csv_path: Path) -> dict[str, str]:
    """Load mapping from disk, returning an empty dict on failure."""
    if csv_path.is_file():
        try:
            mapping = load_he_to_blockid_map(csv_path)
            logging.info(
                "Loaded mapping from %s (%s entries)",
                csv_path,
                len(mapping),
            )
            return mapping
        except Exception as exc:
            logging.error("Error loading mapping file '%s': %s", csv_path, exc)
            return {}

    logging.info("Mapping file not found: %s", csv_path)
    return {}
