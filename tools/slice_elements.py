"""Element (hệ) icons: assets/ui/elements.png, 9 round badges on black (4 on top, 5 below) ->
frontend/public/ui/element_<slug>.png (128 px, black outside the badge made transparent).

Order on the sheet: fire, earth, ice, water / leaf, moon, light, thunder, wing.
The game's elements map onto them in the frontend (config/elements.ts).

Usage: .venv/bin/python tools/slice_elements.py
"""
import numpy as np
import cv2
from PIL import Image

from lib.paths import ASSETS, PUBLIC

NAMES = ["fire", "earth", "ice", "water", "leaf", "moon", "light", "thunder", "wing"]


if __name__ == "__main__":
    img = Image.open(ASSETS / "ui" / "elements.png").convert("RGB")
    a = np.asarray(img)
    lit = (a.max(axis=2) > 28).astype(np.uint8)
    # the glows run together: each row is one blob, cut evenly into its badges (4 on top, 5 below)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.morphologyEx(lit, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8)))
    rows = sorted([tuple(s) for s in st[1:] if s[4] > 50000], key=lambda s: s[1])
    assert len(rows) == 2, rows
    blobs = []
    for (x, y, w, h, _), count in zip(rows, (4, 5)):
        cw = w / count
        for k in range(count):
            cx, cy, side = x + cw * (k + 0.5), y + h / 2, min(cw, h)
            blobs.append((round(cx - side / 2), round(cy - side / 2), round(side), round(side), 0))
    out = PUBLIC / "ui"
    for name, (x, y, w, h, _) in zip(NAMES, blobs):
        icon = img.crop((x, y, x + w, y + h)).convert("RGBA")
        px = np.asarray(icon).copy()
        # round badge: everything outside the circle that fits the box goes see-through, softly
        yy, xx = np.mgrid[0:h, 0:w]
        r = min(w, h) / 2
        d = np.hypot(xx - w / 2, yy - h / 2)
        px[..., 3] = (np.clip((r - d) / 3, 0, 1) * 255).astype(np.uint8)
        Image.fromarray(px).resize((128, 128), Image.LANCZOS).save(out / f"element_{name}.png")
        print(name, (x, y, w, h))
