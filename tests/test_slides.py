from sample_editor.core.slides import extract_he_id


def test_extract_he_id_uses_filename_stem() -> None:
    assert extract_he_id("HE123.svs") == "HE123"
