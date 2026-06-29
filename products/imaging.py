from __future__ import annotations

import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image

# Tunable defaults.
WEBP_QUALITY = 80
MAX_SIZE = (1600, 1600)


def to_webp(
    image_file,
    *,
    quality: int = WEBP_QUALITY,
    max_size: tuple[int, int] = MAX_SIZE,
) -> tuple[str, ContentFile] | None:
    try:
        img = Image.open(image_file)
        img.load()
    except Exception:
        return None

    # Preserve transparency where present, otherwise flatten to RGB.
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")

    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=quality, method=6)
    buffer.seek(0)

    base = os.path.splitext(os.path.basename(image_file.name))[0]
    return f"{base}.webp", ContentFile(buffer.read())
