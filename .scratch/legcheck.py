"""Scratch: compose each leg of a dragon (rest pose) and zoom the joints, plus measure leg stretch."""
import sys, json, math
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
from pathlib import Path
from PIL import Image
import numpy as np

import build_rig as B
from rig_configs import CONFIGS

OUTDIR = Path("/Users/mypc/games/dragon-island-tools/.scratch")

def compose_pieces(pieces, names, pad=30):
    """layout-space composite of the named pieces (they are already laid out)."""
    placed = []
    for n in names:
        p = pieces[n]
        w = round(p["img"].width * p["scale"]); h = round(p["img"].height * p["scale"])
        placed.append((p["img"].resize((w, h), Image.LANCZOS), p["at"][0], p["at"][1]))
    x0 = min(x for _, x, _ in placed) - pad
    y0 = min(y for _, _, y in placed) - pad
    x1 = max(x + i.width for i, x, _ in placed) + pad
    y1 = max(y + i.height for i, _, y in placed) + pad
    canvas = Image.new("RGBA", (int(x1 - x0) + 1, int(y1 - y0) + 1), (255, 255, 255, 255))
    for img, x, y in placed:
        canvas.alpha_composite(img, (round(x - x0), round(y - y0)))
    return canvas, (x0, y0)

def zoom(canvas, cx, cy, r=58, f=5):
    box = (int(cx - r), int(cy - r), int(cx + r), int(cy + r))
    box = (max(0, box[0]), max(0, box[1]), min(canvas.width, box[2]), min(canvas.height, box[3]))
    c = canvas.crop(box)
    return c.resize((c.width * f, c.height * f), Image.NEAREST)

def run(dragon, tag):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    report = {}
    for leg in cfg["legs"]:
        names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
        canvas, (x0, y0) = compose_pieces(pieces, names)
        canvas.save(OUTDIR / f"{tag}_{leg}.png")
        # joints
        up, lo, paw = (pieces[n] for n in names)
        kj = (lo["joint"][0] - x0, lo["joint"][1] - y0)
        aj = (paw["joint"][0] - x0, paw["joint"][1] - y0)
        zoom(canvas, *kj).save(OUTDIR / f"{tag}_{leg}_knee.png")
        zoom(canvas, *aj).save(OUTDIR / f"{tag}_{leg}_ankle.png")
        l1 = math.dist(up["joint"], lo["joint"])
        l2 = math.dist(lo["joint"], paw["joint"])
        l3 = math.dist(up["joint"], paw["joint"])
        report[leg] = dict(thigh=round(l1, 1), shin=round(l2, 1), hip_to_paw=round(l3, 1),
                           stretch=round(l3 / (l1 + l2) * 100, 1))
    print(dragon, json.dumps(report, indent=1))
    return report

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "before")
