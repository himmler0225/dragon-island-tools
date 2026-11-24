"""Stun (Choáng) art: assets/status/stun_sheet.png, 4 rows on black split by thin grey lines:
  1. a burst of stars (8 frames)   2. stars circling (8 frames, loops)   3. the icon (left), more circling, dizzy eyes
  4. a ring bursting on the ground with stones (8 frames)
-> frontend/public/status/: stun_1..8 (circling), stun_b1..b8 (burst), stun_g1..g8 (ground), stun_icon.
Every frame of a row is cut with the same box (the union of all of them), so it does not jump when played.

Usage: .venv/bin/python tools/slice_stun.py
"""
import numpy as np
from PIL import Image

from lib.paths import ASSETS, PUBLIC

SRC = ASSETS / "status" / "stun_sheet.png"
DST = PUBLIC / "status"


def rows(img):
    a = np.asarray(img.convert("RGB")).astype(int)
    lit = (a.max(axis=2) > 70) & (a.max(axis=2) - a.min(axis=2) < 40)
    lines = np.nonzero(lit.mean(axis=1) > 0.5)[0]
    cuts = [0]
    for r in lines:
        if r - cuts[-1] > 40:
            cuts.append(int(r))
    cuts.append(img.height)
    return list(zip(cuts[:-1], cuts[1:]))


def frames(strip, n, names, x0=0):
    w = (strip.width - x0) / n
    cells = [strip.crop((round(x0 + k * w), 0, round(x0 + (k + 1) * w), strip.height)) for k in range(n)]
    box = None
    for c in cells:
        ys, xs = np.nonzero(np.asarray(c.convert("L")) > 14)
        if len(xs):
            b = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    box = (max(0, box[0] - 6), max(0, box[1] - 6), box[2] + 6, box[3] + 6)
    for c, name in zip(cells, names):
        f = c.crop(box)
        s = min(1, 256 / max(f.size))
        f.resize((round(f.width * s), round(f.height * s)), Image.LANCZOS).save(DST / f"{name}.png")
    print(names[0], "..", names[-1], f.size)


if __name__ == "__main__":
    img = Image.open(SRC).convert("RGB")
    r = rows(img)
    assert len(r) == 4, r
    strip = lambda k: img.crop((0, r[k][0] + 3, img.width, r[k][1] - 3))
    frames(strip(0), 8, [f"stun_b{k}" for k in range(1, 9)])
    frames(strip(1), 8, [f"stun_{k}" for k in range(1, 9)])
    frames(strip(3), 8, [f"stun_g{k}" for k in range(1, 9)])
    row3 = strip(2)
    ic = row3.crop((0, 0, row3.width // 6, row3.height))
    ys, xs = np.nonzero(np.asarray(ic.convert("L")) > 30)
    ic = ic.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    ic.resize((128, round(ic.height * 128 / ic.width)), Image.LANCZOS).save(DST / "stun_icon.png")
    print("stun_icon", ic.size)
