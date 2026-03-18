from sample_editor.core.slides import (
    SUPPORTED_SLIDE_EXTENSIONS,
    extract_he_id,
    list_slide_files,
)


def test_extract_he_id_uses_filename_stem() -> None:
    assert extract_he_id("HE123.svs") == "HE123"


def test_supported_slide_extensions_match_gui_targets() -> None:
    assert SUPPORTED_SLIDE_EXTENSIONS == (".isyntax", ".ndpi")


def test_list_slide_files_only_returns_supported_extensions(tmp_path) -> None:
    (tmp_path / "sample_a.isyntax").write_text("", encoding="utf-8")
    (tmp_path / "sample_b.ndpi").write_text("", encoding="utf-8")
    (tmp_path / "ignore_me.svs").write_text("", encoding="utf-8")

    assert list_slide_files(tmp_path) == ["sample_a.isyntax", "sample_b.ndpi"]
