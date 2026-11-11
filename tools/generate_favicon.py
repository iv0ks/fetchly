#!/usr/bin/env python3
"""Generate the Fetchly favicon.

A small document mark (a sheet with a folded corner and a couple of text lines)
in the app's indigo/purple palette, rendered with Pillow so it stays
reproducible and matches the brand. It is a *static asset* served by Flask from
``app/static/`` — never through the vulnerable ``/docs`` endpoint.

Run from the repo root:

    python tools/generate_favicon.py

Writes ``app/static/favicon.png`` (base 512 px, also downscaled to 32 px).
"""

from __future__ import annotations

import os

from PIL import Image, ImageDraw

INDIGO = (58, 12, 163, 255)  # --accent
INDIGO_LIGHT = (124, 92, 240, 255)
PAPER = (255, 255, 255, 255)
LINE = (181, 167, 247, 255)

SIZE = 512
STATIC_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "app", "static")


def _render() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded indigo background tile.
    draw.rounded_rectangle([0, 0, SIZE, SIZE], radius=int(SIZE * 0.22), fill=INDIGO)

    # Document sheet with a folded top-right corner.
    left, top, right, bottom = 150, 120, 362, 392
    fold = 70
    sheet = [
        (left, top),
        (right - fold, top),
        (right, top + fold),
        (right, bottom),
        (left, bottom),
    ]
    draw.polygon(sheet, fill=PAPER)
    # The folded corner triangle, in a lighter indigo.
    draw.polygon(
        [(right - fold, top), (right - fold, top + fold), (right, top + fold)],
        fill=INDIGO_LIGHT,
    )

    # Text lines on the sheet.
    for i in range(4):
        y = top + 70 + i * 48
        x_end = right - 40 if i < 3 else left + 90
        draw.rounded_rectangle([left + 36, y, x_end, y + 18], radius=9, fill=LINE)

    return img


def main() -> None:
    out = os.path.abspath(STATIC_DIR)
    os.makedirs(out, exist_ok=True)
    base = _render()

    big = os.path.join(out, "favicon.png")
    base.save(big, "PNG")
    print(f"wrote {big}")

    small_path = os.path.join(out, "favicon-32.png")
    base.resize((32, 32), Image.LANCZOS).save(small_path, "PNG")
    print(f"wrote {small_path}")


if __name__ == "__main__":
    main()
