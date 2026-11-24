"""Objective detector: find dark horizontal seam lines in the composed leg image."""
import sys, json, math
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
from pathlib import Path
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

OUTDIR = Path("/Users/mypc/games/dragon-island-tools/.scratch")

def compose_pieces(pieces, names, pad=30):
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

def seam_score(a, cx, cy, halfw=18, rows=9):
    """Mean darkness of a horizontal band of width 2*halfw centred at (cx,cy)."""
    band = a[max(0, cy - rows): cy + rows + 1, max(0, cx - halfw): cx + halfw + 1]
    if band.size == 0:
        return None
    lum = band[..., :3].mean(axis=2)
    alpha = band[..., 3] / 255.0
    # darkness relative to the local limb brightness: use the pixels fully inside
    m = alpha > 0.9
    if m.sum() < 20:
        return None
    return float(lum[m].mean()), int(m.sum())

def run(dragon, tag):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    rows = []
    for leg in cfg["legs"]:
        names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
        canvas, (x0, y0) = compose_pieces(pieces, names)
        a = np.asarray(canvas).astype(float)
        up, lo, paw = (pieces[n] for n in names)
        for label, j in (("knee", lo["joint"]), ("ankle", paw["joint"])):
            cx, cy = int(j[0] - x0), int(j[1] - y0)
            s = seam_score(a, cx, cy)
            # also a reference: the solid limb brightness at mid-thigh
            mid = up["joint"]
            ref = seam_score(a, int(mid[0] - x0), int(mid[1] - y0) + 40, rows=6)
            rows.append((leg, label, round(cx), round(cy), s[0] if s else None, s[1] if s else 0,
                         round(ref[0], 1) if ref else None))
    print(f"--- {dragon} [{tag}]")
    print(f"{'leg':11s} {'joint':6s} {'x':>5s} {'y':>5s} {'lum':>7s} {'npx':>5s} {'ref_lum':>8s}")
    for r in rows:
        print(f"{r[0]:11s} {r[1]:6s} {r[2]:5d} {r[3]:5d} {str(r[4]):>7s} {r[5]:5d} {str(r[6]):>8s}")
    return rows

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "before")
