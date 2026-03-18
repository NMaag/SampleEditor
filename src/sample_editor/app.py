"""Command-line entry point for the revamp project."""

from __future__ import annotations

import logging
from pathlib import Path

from sample_editor.core.config import get_default_config_path, load_config, save_config
from sample_editor.core.mapping import load_mapping_safe
from sample_editor.core.slides import (
    compare_slides,
    extract_he_id,
    list_slide_files,
    replace_label_and_write,
)


HELP_TEXT = """
SampleEditor Revamp

Menu options:
- (v) View a file
- (c) Convert a single file
- (b) Batch convert new files
- (m) Compare two files
- (f) Change infeed, outfeed, or CSV mapping path
- (h) Help
- (q) Quit
"""


def ask_input(prompt: str, allow_quit: bool = True) -> str | None:
    """Prompt for input and treat q/exit as cancel."""
    try:
        response = input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return None

    if allow_quit and response.lower() in {"q", "exit"}:
        return None
    return response


def get_app_dirs(base_dir: Path) -> dict[str, Path]:
    """Build default app paths."""
    return {
        "input_folder": base_dir / "infeed",
        "output_folder": base_dir / "outfeed",
        "csv_mapping_path": base_dir / "block_he_mapping.csv",
        "config_path": get_default_config_path(base_dir),
    }


def load_runtime_paths(base_dir: Path) -> dict[str, Path]:
    """Load configured app paths on top of defaults."""
    defaults = get_app_dirs(base_dir)
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


def select_slide_file(folder: Path) -> str | None:
    """Select a slide filename from a folder."""
    slide_files = list_slide_files(folder)
    if not folder.is_dir():
        print(f"Folder not found: {folder}")
        return None
    if not slide_files:
        print("No SVS files found in the folder.")
        return None

    print("\nAvailable slide files:")
    for index, filename in enumerate(slide_files, start=1):
        print(f"{index}: {filename}")

    while True:
        choice_raw = ask_input("\nSelect file number (or 'q' to return): ")
        if choice_raw is None:
            return None
        try:
            choice = int(choice_raw)
        except ValueError:
            print("Invalid input. Please enter a valid number or 'q' to return.")
            continue

        if 1 <= choice <= len(slide_files):
            return slide_files[choice - 1]

        print(f"Please enter a number between 1 and {len(slide_files)}.")


def print_slide_details(slide_path: Path) -> None:
    """Print slide page details."""
    pages = compare_slides(slide_path, slide_path)["original"]
    print(f"\nViewing file: {slide_path}")
    print(f"{len(pages)} pages found in {slide_path}:")
    for page in pages:
        print(
            f"Page {page['page_number']}: "
            f"shape={page['shape']}, description={page['description']}"
        )


def convert_single_slide(
    input_folder: Path,
    output_folder: Path,
    mapping: dict[str, str],
) -> tuple[Path, Path] | tuple[None, None]:
    """Convert a single slide chosen interactively."""
    slide_filename = select_slide_file(input_folder)
    if not slide_filename:
        return None, None

    slide_path = input_folder / slide_filename
    he_id = extract_he_id(slide_filename)
    code = mapping.get(he_id) if mapping else None
    if code:
        print(f"Auto-mapped Block ID '{code}' from mapping key '{he_id}'.")
    else:
        code = ask_input(
            f"Enter Block ID for '{slide_filename}' or type 'q' to return to menu: "
        )
        if code is None:
            print("Conversion cancelled.")
            return None, None

    out_path = output_folder / f"{code}{slide_path.suffix}"
    replace_label_and_write(slide_path, code, out_path)
    return slide_path, out_path


def batch_convert_new_files(
    input_folder: Path,
    output_folder: Path,
    mapping: dict[str, str],
) -> None:
    """Convert new input slides that are not already present in output."""
    infeed_files = list_slide_files(input_folder)
    outfeed_files = list_slide_files(output_folder)
    outfeed_block_ids = {Path(filename).stem for filename in outfeed_files}

    files_to_convert: list[tuple[str, str, str]] = []
    for filename in infeed_files:
        he_id = extract_he_id(filename)
        code = mapping.get(he_id)
        if not code:
            print(
                f"Warning: Could not auto-map Block ID for {filename} "
                f"(mapping key: '{he_id}')."
            )
            code = ask_input(
                f"Enter Block ID for '{filename}' or type 'q' to return to menu: "
            )
            if code is None:
                print("Batch conversion cancelled.")
                return

        if code not in outfeed_block_ids:
            files_to_convert.append((filename, code, he_id))

    if not files_to_convert:
        print("All infeed files have already been converted.")
        return

    print(f"\n{len(files_to_convert)} infeed files have not been converted yet:")
    for index, (filename, code, he_id) in enumerate(files_to_convert, start=1):
        print(f"  {index}: {filename} (mapping key: {he_id}) -> Block ID: {code}")

    proceed = input(f"\nConvert these {len(files_to_convert)} files? (y/n): ").strip().lower()
    if proceed != "y":
        print("Batch conversion cancelled.")
        return

    for index, (filename, code, he_id) in enumerate(files_to_convert, start=1):
        print(
            f"\n[{index}/{len(files_to_convert)}] Converting {filename} "
            f"with Block ID '{code}' (mapping key: {he_id})..."
        )
        slide_path = input_folder / filename
        out_path = output_folder / f"{code}{slide_path.suffix}"
        try:
            replace_label_and_write(slide_path, code, out_path)
        except Exception as exc:
            print(f"  Error processing {filename}: {exc}")


def configure_paths(paths: dict[str, Path]) -> dict[str, Path]:
    """Interactively update app paths."""
    print("\nChange paths or mapping:")
    print(f"Current infeed folder: {paths['input_folder']}")
    print(f"Current outfeed folder: {paths['output_folder']}")
    print(f"Current CSV mapping path: {paths['csv_mapping_path']}")

    folder_type = ask_input(
        "Change (i)nfeed, (o)utfeed, or (m)apping path? (i/o/m or 'q' to return): "
    )
    if folder_type is None:
        return paths

    folder_type = folder_type.lower()
    if folder_type == "i":
        new_in = ask_input("Paste new infeed folder path: ")
        if new_in and Path(new_in).is_dir():
            paths["input_folder"] = Path(new_in)
            persist_runtime_paths(paths)
            print(f"Infeed folder updated to: {paths['input_folder']}")
        elif new_in is not None:
            print("Invalid folder path. No changes made.")
    elif folder_type == "o":
        new_out = ask_input("Paste new outfeed folder path: ")
        if new_out and Path(new_out).is_dir():
            paths["output_folder"] = Path(new_out)
            persist_runtime_paths(paths)
            print(f"Outfeed folder updated to: {paths['output_folder']}")
        elif new_out is not None:
            print("Invalid folder path. No changes made.")
    elif folder_type == "m":
        new_map = ask_input("Paste new CSV mapping file path (or a path to create): ")
        if new_map is not None:
            paths["csv_mapping_path"] = Path(new_map)
            persist_runtime_paths(paths)
            print(f"CSV mapping path updated to: {paths['csv_mapping_path']}")
    else:
        print("Invalid choice. No changes made.")

    return paths


def main() -> None:
    """Run the command-line application."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    base_dir = Path(__file__).resolve().parents[2]
    paths = load_runtime_paths(base_dir)
    paths["output_folder"].mkdir(parents=True, exist_ok=True)

    while True:
        mapping = load_mapping_safe(paths["csv_mapping_path"])
        print(f"\nCurrent infeed folder: {paths['input_folder']}")
        print(f"Current outfeed folder: {paths['output_folder']}")
        print(f"Current CSV mapping path: {paths['csv_mapping_path']}")
        print("Would you like to:")
        print("  (v) View a file")
        print("  (c) Convert a single file")
        print("  (b) Batch convert new files")
        print("  (m) Compare two files")
        print("  (f) Change infeed, outfeed, or CSV mapping path")
        print("  (h) Read Help / Info")
        print("  (q) Quit")
        action = input("Enter your choice (v/c/b/m/f/h/q): ").strip().lower()

        if action == "v":
            folder_choice = input("View from (i)nfeed or (o)utfeed folder? (i/o): ").strip().lower()
            folder = paths["input_folder"] if folder_choice == "i" else paths["output_folder"] if folder_choice == "o" else None
            if folder is None:
                print("Invalid folder choice.")
                continue
            slide_filename = select_slide_file(folder)
            if slide_filename:
                print_slide_details(folder / slide_filename)
        elif action == "c":
            convert_single_slide(paths["input_folder"], paths["output_folder"], mapping)
        elif action == "b":
            batch_convert_new_files(paths["input_folder"], paths["output_folder"], mapping)
        elif action == "m":
            print("\nSelect original (infeed) file to compare:")
            original_filename = select_slide_file(paths["input_folder"])
            if not original_filename:
                continue
            print("\nSelect new (outfeed) file to compare:")
            new_filename = select_slide_file(paths["output_folder"])
            if not new_filename:
                continue
            comparison = compare_slides(
                paths["input_folder"] / original_filename,
                paths["output_folder"] / new_filename,
            )
            print(f"\nOriginal file: {len(comparison['original'])} pages")
            for page in comparison["original"]:
                print(
                    f"  Page {page['page_number']}: "
                    f"shape={page['shape']}, description={page['description']}"
                )
            print(f"\nNew file: {len(comparison['new'])} pages")
            for page in comparison["new"]:
                print(
                    f"  Page {page['page_number']}: "
                    f"shape={page['shape']}, description={page['description']}"
                )
        elif action == "f":
            paths = configure_paths(paths)
        elif action == "h":
            print(HELP_TEXT)
        elif action == "q":
            print("Exiting.")
            break
        else:
            print("Invalid option. Please enter 'v', 'c', 'b', 'm', 'f', 'h', or 'q'.")


if __name__ == "__main__":
    main()
