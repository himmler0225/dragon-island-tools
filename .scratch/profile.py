"""Numeric dump of the joint region: alpha coverage of each segment + luminance profile across the seam."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
from pathlib import Path
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

def analyse(dragon, leg, tag):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    up, lo, paw = (pieces[n] for n in names)
    print(f"=== {dragon} {leg}")
    for label, p in (("upper", up), ("lower", lo), ("paw", paw)):
        a = np.asarray(p["img"])
        al = a[..., 3]
        rows = np.nonzero(al.any(axis=1))[0]
        print(f" {label}: img {p['img'].width}x{p['img'].height} at {tuple(round(v,1) for v in p['at'])} scale {p['scale']:.3f} "
              f"alpha rows {rows[0]}..{rows[-1]} joint {tuple(round(v,1) for v in p['joint'])}")
    # joint of lower in layout; where is it relative to each piece?
    for label, p in (("upper", up), ("lower", lo), ("paw", paw)):
        print(f"   {label}: bbox {p['bbox']}")
    return pieces

def profile(dragon, leg):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    # compose in layout space
    placed = []
    for n in names:
        p = pieces[n]
        w = round(p["img"].width * p["scale"]); h = round(p["img"].height * p["scale"])
        placed.append((p["img"].resize((w, h), Image.LANCZOS), p["at"][0], p["at"][1], n))
    x0 = min(x for _, x, _, _ in placed) - 30
    y0 = min(y for _, _, y, _ in placed) - 30
    canvas = Image.new("RGBA", (int(max(x + i.width for i, x, _, _ in placed) - x0) + 1,
                               int(max(y + i.height for i, _, y, _ in placed) - y0) + 1), (255, 255, 255, 255))
    for img, x, y, n in reversed(placed):   # legs_down: thigh over shin over paw
        canvas.alpha_composite(img, (round(x - x0), round(y - y0)))
    a = np.asarray(canvas).astype(float)
    lum = a[..., :3].mean(axis=2)
    lo, paw = pieces[names[1]], pieces[names[2]]
    for label, j in (("knee", lo["joint"]), ("ankle", paw["joint"])):
        cx, cy = int(j[0] - x0), int(j[1] - y0)
        print(f"-- {label} at ({cx},{cy})")
        for dy in range(-8, 9, 2):
            row = lum[cy + dy, max(0, cx - 22): cx + 23]
            bar = "".join("#" if v < 110 else ("+" if v < 150 else ".") for v in row)
            print(f"  y{cy+dy:+3d} {bar}")

if __name__ == "__main__":
    analyse(sys.argv[1], sys.argv[2], "x")
    profile(sys.argv[1], sys.argv[2])
