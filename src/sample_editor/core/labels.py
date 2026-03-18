"""Label image generation for SampleEditor."""

from __future__ import annotations

import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont


def generate_label_image(code: str) -> np.ndarray:
    """Generate a simple QR label image for a block ID."""
    qr = qrcode.make(code).resize((200, 200))
    label = Image.new("RGB", (400, 300), "white")
    draw = ImageDraw.Draw(label)
    font = ImageFont.load_default()
    draw.text((220, 120), code, fill="black", font=font)
    label.paste(qr, (10, 50))
    return np.array(label)
