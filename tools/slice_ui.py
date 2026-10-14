"""Logo and loading screen -> frontend/public/ui/.

  assets/ui/logo.png                 logo on a plain (white) background
  assets/ui/loading/background.png   full-bleed loading painting
  assets/ui/loading/bar.png          on magenta: bar frame (top) and bar fill (bottom)

Writes frontend/public/ui/: logo.png (transparent), loading_bg.jpg, loading_frame.png,
loading_fill.png, and loading_bar.json (where the fill goes inside the frame, as shares of the frame).

Usage: .venv/bin/python tools/slice_ui.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path("/Users/mypc/cinemark-workspace/dragon-island")
sys.path.insert(0, str(ROOT))

from lib.image import key_magenta
from lib.paths import ASSETS, UI_OUT

UI = ASSETS / "ui"


def remove_plain_background(img, tol=18):
    """Flood-fill the near-uniform background from the borders and make it transparent."""
    rgb = np.asarray(img.convert("RGB")).astype(np.int16)
    h, w = rgb.shape[:2]
    bg = np.median(np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]), axis=0)
    near = (np.abs(rgb - bg).max(axis=2) <= tol).astype(np.uint8)
    mask = np.zeros((h + 2, w + 2), np.uint8)
    for x in range(0, w, 8):
        for y in (0, h - 1):
            if near[y, x] and not mask[y + 1, x + 1]:
                cv2.floodFill(near, mask, (x, y), 2, flags=4 | (1 << 8))
    for y in range(0, h, 8):
        for x in (0, w - 1):
            if near[y, x] and not mask[y + 1, x + 1]:
                cv2.floodFill(near, mask, (x, y), 2, flags=4 | (1 << 8))
    outside = mask[1:-1, 1:-1] > 0
    alpha = np.where(outside, 0, 255).astype(np.uint8)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.0)   # soften the cut edge
    out = Image.fromarray(np.dstack([rgb.astype(np.uint8), alpha]), "RGBA")
    return out.crop(out.getchannel("A").getbbox())


def main_part(img, min_share=0.02):
    """Drop specks: keep opaque regions with at least `min_share` of the biggest region's area."""
    arr = np.asarray(img).copy()
    solid = (arr[..., 3] > 40).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(cv2.dilate(solid, np.ones((9, 9), np.uint8)))
    if n <= 2:
        return img.crop(img.getchannel("A").getbbox())
    biggest = stats[1:, 4].max()
    keep = [i for i in range(1, n) if stats[i][4] >= min_share * biggest]
    arr[~np.isin(labels, keep)] = 0
    out = Image.fromarray(arr, "RGBA")
    return out.crop(out.getchannel("A").getbbox())


def main():
    UI_OUT.mkdir(parents=True, exist_ok=True)
    logo = remove_plain_background(Image.open(UI / "logo.png"))
    logo.thumbnail((640, 640), Image.LANCZOS)
    logo.save(UI_OUT / "logo.png", optimize=True)

    Image.open(UI / "loading" / "background.png").convert("RGB").save(UI_OUT / "loading_bg.jpg", quality=86, optimize=True)

    bar = key_magenta(Image.open(UI / "loading" / "bar.png"))
    rows = (np.asarray(bar)[..., 3] > 40).any(axis=1)
    gaps = [y for y in range(1, bar.height - 1) if not rows[y] and rows[y - 1]]
    split = gaps[0] + 1                      # first empty row after the frame
    frame = main_part(bar.crop((0, 0, bar.width, split)))
    fill = main_part(bar.crop((0, split, bar.width, bar.height)))
    # the frame's opening: the transparent hole in its middle row
    a = np.asarray(frame)[..., 3] > 40
    mid = a[a.shape[0] // 2]
    x0 = x1 = a.shape[1] // 2   # transparent run through the centre of the middle row
    while x0 > 0 and not mid[x0 - 1]:
        x0 -= 1
    while x1 < a.shape[1] - 1 and not mid[x1 + 1]:
        x1 += 1
    # vertical extent: the transparent run through the middle column
    col, ym = a[:, (x0 + x1) // 2], a.shape[0] // 2
    y0 = ym
    while y0 > 0 and not col[y0 - 1]:
        y0 -= 1
    y1 = ym
    while y1 < a.shape[0] - 1 and not col[y1 + 1]:
        y1 += 1
    frame.save(UI_OUT / "loading_frame.png", optimize=True)
    fill.save(UI_OUT / "loading_fill.png", optimize=True)
    spec = {"frame": list(frame.size), "fill": list(fill.size),
            "hole": [round(x0 / frame.width, 4), round(y0 / frame.height, 4),
                     round((x1 - x0) / frame.width, 4), round((y1 - y0) / frame.height, 4)]}
    (UI_OUT / "loading_bar.json").write_text(json.dumps(spec))
    print("logo", logo.size, "| frame", frame.size, "fill", fill.size, "hole", spec["hole"])


if __name__ == "__main__":
    main()
