from sample_editor.core.labels import generate_label_image


def test_generate_label_image_returns_expected_shape() -> None:
    image = generate_label_image("BLOCK001")

    assert image.shape == (300, 400, 3)
