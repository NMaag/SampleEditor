"""Slide-processing helpers for SampleEditor."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import tifffile

from sample_editor.core.labels import generate_label_image


def extract_he_id(filename: str) -> str:
    """Return the filename stem used for HE-to-block mapping."""
    return Path(filename).stem


def list_slide_files(folder: Path) -> list[str]:
    """List slide files supported by the current tool."""
    if not folder.is_dir():
        return []
    return sorted(path.name for path in folder.iterdir() if path.suffix.lower() == ".svs")


def describe_slide(slide_path: Path) -> list[dict[str, Any]]:
    """Return page-level metadata for a slide."""
    pages: list[dict[str, Any]] = []
    with tifffile.TiffFile(slide_path) as tif:
        for index, page in enumerate(tif.pages, start=1):
            description_tag = page.tags.get("ImageDescription", None)
            pages.append(
                {
                    "page_number": index,
                    "shape": page.shape,
                    "description": description_tag.value if description_tag else None,
                }
            )
    return pages


def compare_slides(original_path: Path, new_path: Path) -> dict[str, list[dict[str, Any]]]:
    """Return comparable page metadata for two slides."""
    return {
        "original": describe_slide(original_path),
        "new": describe_slide(new_path),
    }


def replace_label_and_write(
    svs_path: Path,
    code: str,
    out_path: Path | None = None,
) -> Path:
    """Replace the label page in an SVS file and write a new output slide."""
    label_np = generate_label_image(code)
    if out_path is None:
        out_path = svs_path.with_name(f"{code}{svs_path.suffix}")

    with tifffile.TiffFile(svs_path) as tif:
        kept_pages: list[tuple[Any, dict[str, Any], str]] = []
        seen_shapes = set()

        try:
            series = tif.series[0]
            levels = getattr(series, "levels", None)
        except Exception:
            levels = None

        if levels:
            for level_index, level in enumerate(levels):
                try:
                    array = level.asarray()
                except Exception as exc:
                    print(f"Level {level_index}: read error: {exc}; skipping")
                    continue

                tags: dict[str, Any] = {}
                try:
                    page0 = level.pages[0]
                    tags = {tag.name: tag.value for tag in page0.tags.values()}
                    description = tags.get("ImageDescription", None)
                except Exception:
                    description = None

                shape = getattr(array, "shape", None)
                kept_pages.append((array, tags, f"level[{level_index}] desc={description}"))
                seen_shapes.add(shape)
        else:
            print("No series levels found, falling back to tif.pages for pyramid levels.")

        for page_index, page in enumerate(tif.pages):
            try:
                array = page.asarray()
            except Exception as exc:
                print(f"page {page_index + 1}: read error: {exc}; skipping")
                continue

            shape = getattr(array, "shape", None)
            if isinstance(shape, tuple) and len(shape) >= 2 and (shape[0] == 1 or shape[1] == 1):
                continue
            if shape in seen_shapes:
                continue

            tags = {tag.name: tag.value for tag in page.tags.values()}
            description = tags.get("ImageDescription", None)
            kept_pages.append((array, tags, f"page[{page_index}] desc={description}"))
            seen_shapes.add(shape)

    if not kept_pages:
        raise ValueError(f"No pages collected from {svs_path}")

    label_index = None
    for index, (_, tags, _) in enumerate(kept_pages):
        description = tags.get("ImageDescription", "")
        if description and "Label" in str(description):
            label_index = index
            break

    if label_index is None and len(kept_pages) >= 2:
        label_index = len(kept_pages) - 2

    if label_index is not None:
        _, old_tags, _ = kept_pages[label_index]
        new_tags = {**old_tags}
        new_tags["ImageDescription"] = "Anonymized Label"
        kept_pages[label_index] = (label_np, new_tags, f"replaced_label_at_{label_index}")
    else:
        print("Warning: Could not determine a label page to replace.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tifffile.TiffWriter(out_path, bigtiff=True) as tif_writer:
        for index, (array, tags, _) in enumerate(kept_pages, start=1):
            photometric = (
                "minisblack"
                if (array.ndim == 2 or (array.ndim == 3 and array.shape[2] == 1))
                else "rgb"
            )
            x_resolution = tags.get("XResolution", (1, 1))
            y_resolution = tags.get("YResolution", (1, 1))
            tif_writer.write(
                array,
                photometric=photometric,
                metadata=None,
                description=tags.get("ImageDescription", None),
                resolution=(x_resolution, y_resolution),
                resolutionunit=tags.get("ResolutionUnit", None),
                compression="jpeg",
                tile=(512, 512),
            )
            progress = int(40 * index / len(kept_pages))
            print(
                "\r[Writing] ["
                + "#" * progress
                + "-" * (40 - progress)
                + f"] {index}/{len(kept_pages)} pages",
                end="",
                flush=True,
            )

    print("\nDone.")
    print(f"Saved: {out_path}")
    return out_path
