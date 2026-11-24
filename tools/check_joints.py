"""Measure how well each leg joint holds together when it bends (a walk bends knees and ankles by up to ~40°).

For every knee and ankle of every built rig (frontend/public/dragons/<id>/rig.json): the child piece is turned about
its joint from -40° to +40°, and the overlap between it and its parent (plus the joint's cap, if the rig has one) is
counted. A joint whose overlap falls to (almost) nothing opens a gap when the dragon walks.

Prints, per joint: the overlap at rest and the smallest while bent, in rig px², and `width`: the child's width at the
joint. A joint is flagged when the smallest overlap is under 15% of width² (a thin sliver or nothing).

Usage: .venv/bin/python tools/check_joints.py [dragon_id ...] [--all]   (default: only flagged joints are listed)
"""
import json
import sys

import numpy as np
from PIL import Image

from lib.paths import OUT

ANGLES = range(-40, 41, 10)
LEGS = ("fore_near", "hind_near", "fore_far", "hind_far")


def placed(d, bone, canvas, off, deg=0.0):
    """The bone's solid mask on a canvas (rig px, top-left `off`), turned `deg` about its joint."""
    img = Image.open(d / f"{bone['name']}.png").convert("RGBA").getchannel("A")
    jx, jy = bone["joint"]
    px, py = bone["origin"][0] * img.width, bone["origin"][1] * img.height
    big = Image.new("L", canvas)
    big.paste(img, (round(jx - px - off[0]), round(jy - py - off[1])))
    if deg:
        big = big.rotate(-deg, center=(jx - off[0], jy - off[1]), resample=Image.BILINEAR)
    return np.asarray(big) > 128


def check(did):
    d = OUT / did
    rig = json.load(open(d / "rig.json"))
    B = {b["name"]: b for b in rig["bones"]}
    rows = []
    for leg in LEGS:
        for top, low in (("upper", "lower"), ("lower", "paw")):
            p, c = B.get(f"{leg}_{top}"), B.get(f"{leg}_{low}")
            if not p or not c:
                continue
            jx, jy = c["joint"]
            off, canvas = (jx - 200, jy - 200), (400, 400)
            parent = placed(d, p, canvas, off)
            cap = B.get(f"cap_{leg}_{low}")
            child0 = placed(d, c, canvas, off)
            row = child0[200 - 2:200 + 3].any(axis=0)
            xs = np.nonzero(row)[0]
            width = float(xs.max() - xs.min() + 1) if len(xs) else 1.0
            if width < 6 or child0.sum() < 40:   # a rigid leg's stub bones: nothing bends there
                continue
            overlaps = []
            for a in ANGLES:
                held = parent | placed(d, cap, canvas, off, a / 2) if cap else parent   # (the cap turns halfway)
                overlaps.append(int((held & placed(d, c, canvas, off, a)).sum()))
            rows.append((f"{leg}_{low}", overlaps[len(overlaps) // 2], min(overlaps), width, bool(cap)))
    return rows


if __name__ == "__main__":
    show_all = "--all" in sys.argv
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(p.name for p in OUT.iterdir() if (p / "rig.json").exists())
    bad = 0
    for did in ids:
        for name, rest, low, width, cap in check(did):
            flagged = low < 0.15 * width * width
            bad += flagged
            if flagged or show_all:
                print(f"{'GAP ' if flagged else 'ok  '}{did:20s} {name:16s} rest {rest:6d}  min {low:6d}  width {width:5.0f}  ratio {low / (width * width):.2f}  {'cap' if cap else 'no cap'}")
    print(f"{bad} joint(s) flagged")
