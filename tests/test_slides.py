from sample_editor.core.slides import (
    SUPPORTED_SLIDE_EXTENSIONS,
    describe_case_files,
    extract_he_id,
    list_case_slide_paths,
    list_slide_files,
)


def test_extract_he_id_uses_filename_stem() -> None:
    assert extract_he_id("HE123.svs") == "HE123"


def test_supported_slide_extensions_match_gui_targets() -> None:
    assert SUPPORTED_SLIDE_EXTENSIONS == (".isyntax", ".ndpi")


def test_list_slide_files_only_returns_supported_extensions(tmp_path) -> None:
    case_folder = tmp_path / "CaseA"
    case_folder.mkdir()
    (case_folder / "sample_a.isyntax").write_text("", encoding="utf-8")
    (tmp_path / "sample_b.ndpi").write_text("", encoding="utf-8")
    (tmp_path / "ignore_me.svs").write_text("", encoding="utf-8")

    assert list_slide_files(tmp_path) == ["CaseA/sample_a.isyntax", "sample_b.ndpi"]


def test_case_files_are_sorted_by_size_descending(tmp_path) -> None:
    large = tmp_path / "large.isyntax"
    small = tmp_path / "small.isyntax"
    large.write_bytes(b"a" * 20)
    small.write_bytes(b"a" * 5)

    assert list_case_slide_paths(large) == [large, small]


def test_describe_case_files_marks_largest_file(tmp_path) -> None:
    large = tmp_path / "large.isyntax"
    small = tmp_path / "small.isyntax"
    large.write_bytes(b"a" * 20)
    small.write_bytes(b"a" * 5)

    descriptions = describe_case_files(small)

    assert descriptions[0]["name"] == "large.isyntax"
    assert descriptions[0]["is_largest"] is True
    assert descriptions[1]["is_largest"] is False
