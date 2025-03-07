from __future__ import annotations

from pathlib import Path


def read_image(image_path: str | Path) -> bytes:
    with open(image_path, "rb") as fb:
        return fb.read()
