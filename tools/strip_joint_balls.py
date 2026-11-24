"""Take the round joint balls off a legs sheet drawn with them (the birds: a ball under each thigh, on both ends of
each shin and on top of each foot), so the rig joins the pieces by overlapping them, like the dragons' legs.

The balls are cut off by sheet rows, read off each sheet by eye (CUTS: per piece of a column, top to bottom, the rows
kept: (from, to), None = that end as drawn). A cut end is flat, and hidden: the rig draws thigh over shin over foot.

Writes parts/legs_noballs.png next to parts/legs.png (the original is kept).

Usage: .venv/bin/python tools/strip_joint_balls.py <dragon_id> ...
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

from lib.image import components, key_magenta
from lib.paths import DRAGONS

# rows kept of (thigh, shin, foot), sheet px
PHOENIX = [(None, 398), (506, 694), (808, None)]
CUTS = {
    "fire_phoenix": PHOENIX,
    "ice_phoenix": PHOENIX,
}

if __name__ == "__main__":
    for did in sys.argv[1:]:
        P = DRAGONS / did / "parts"
        img = key_magenta(Image.open(P / "legs.png"))
        # the sheet itself is kept as drawn (keying is only used to find the pieces: it can eat purple feathers);
        # only the cut rows of each piece are painted over with the background
        raw = np.asarray(Image.open(P / "legs.png").convert("RGB")).copy()
        parts = [c for c in components(img) if c[0][2] * c[0][3] > 1500]
        # columns: pieces whose x ranges overlap belong to one leg
        cols = []
        for c in sorted(parts, key=lambda c: c[0][0] + c[0][2] / 2):
            mid = c[0][0] + c[0][2] / 2
            if cols and abs(mid - cols[-1]["mid"]) < 140:
                cols[-1]["pieces"].append(c)
            else:
                cols.append({"mid": mid, "pieces": [c]})
        for col in cols:
            pieces = sorted(col["pieces"], key=lambda c: c[0][1])
            assert len(pieces) == 3, (did, [c[0] for c in pieces])
            for ((x, y, w, h), m), (top, bottom) in zip(pieces, CUTS[did]):
                piece = np.asarray(Image.fromarray(((m > 0) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 0
                if top is not None:
                    raw[:top][piece[:top]] = (255, 0, 255)
                if bottom is not None:
                    raw[bottom:][piece[bottom:]] = (255, 0, 255)
        # (a few px wider than the keyed piece: its soft edge goes too)
        Image.fromarray(raw).save(P / "legs_noballs.png")
        print(did, len(cols), "legs ->", P / "legs_noballs.png")
