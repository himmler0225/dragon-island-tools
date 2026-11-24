"""Star (sao) art: assets/ui/stars.png, a design sheet on black. Cut:
  the single stars (row 1: 9 of them; 1-9★ gold -> red, 10-30★ violet -> blue -> cyan -> rainbow) -> ui/star_1..9.png
  the milestone badges (row 3: 1, 3, 5, 9, 10, 15, 20, 30★) -> ui/star_badge_<n>.png
into frontend/public/ui/ (black made see-through by brightness: they glow on black).

Usage: .venv/bin/python tools/slice_stars.py
"""
import cv2
import numpy as np
from PIL import Image

from lib.paths import ASSETS, PUBLIC

BADGES = [1, 3, 5, 9, 10, 15, 20, 30]


def blobs(img, y0, y1, x0, count, size):
    band = np.asarray(img.crop((x0, y0, img.width, y1)).convert("L"))
    lit = cv2.morphologyEx((band > 60).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(lit)
    found = sorted([s for s in st[1:] if s[4] > 600 and s[2] < 320 and s[3] > 30], key=lambda s: -s[4])[:count]   # (not the thin rules)
    found = sorted(found, key=lambda s: s[0])
    assert len(found) == count, (y0, len(found))
    out = []
    for x, y, w, h, _ in found:
        # just the blob's box (a square crop would take in the labels under it), centred on a square canvas
        crop = img.crop((x0 + x - 8, y0 + y - 8, x0 + x + w + 8, y0 + y + h + 8)).convert("RGB")
        a = np.asarray(crop).astype(np.float32)
        alpha = np.clip((a.max(axis=2) - 10) / 50, 0, 1)   # glow on black: dark goes see-through
        piece = Image.fromarray(np.dstack([a, alpha * 255]).astype(np.uint8), "RGBA")
        side = max(piece.size)
        sq = Image.new("RGBA", (side, side))
        sq.alpha_composite(piece, ((side - piece.width) // 2, (side - piece.height) // 2))
        out.append(sq.resize((size, size), Image.LANCZOS))
    return out


if __name__ == "__main__":
    img = Image.open(ASSETS / "ui" / "stars.png").convert("RGB")
    dst = PUBLIC / "ui"
    for k, s in enumerate(blobs(img, 20, 135, 300, 9, 64), 1):
        s.save(dst / f"star_{k}.png")
    for n, b in zip(BADGES, blobs(img, 265, 385, 270, 8, 128)):
        b.save(dst / f"star_badge_{n}.png")
    print("ok")
