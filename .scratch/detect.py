"""Objective seam detector on the composed (crouched) leg: count dark-outline pixels per row."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

def canvas_of(pieces, names):
    placed = []
    for n in names:
        p = pieces[n]
        w = round(p["img"].width * p["scale"]); h = round(p["img"].height * p["scale"])
        placed.append((p["img"].resize((w, h), Image.LANCZOS), p["at"][0], p["at"][1]))
    x0 = min(x for _, x, _ in placed) - 30
    y0 = min(y for _, _, y in placed) - 30
    c = Image.new("RGBA", (int(max(x + i.width for i, x, _ in placed) - x0) + 1,
                           int(max(y + i.height for i, _, y in placed) - y0) + 1), (0, 0, 0, 0))
    for img, x, y in reversed(placed):
        c.alpha_composite(img, (round(x - x0), round(y - y0)))
    return c, (x0, y0)

def report(dragon, leg, tag="", quiet=False):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    c, (x0, y0) = canvas_of(pieces, names)
    a = np.asarray(c).astype(float)
    lum = a[..., :3].mean(axis=2); al = a[..., 3]
    out = []
    for y in range(c.height):
        m = al[y] > 200
        if m.sum() < 12:
            continue
        xs = np.nonzero(m)[0]
        vals = lum[y][m]
        med = np.median(vals)
        dark = int((vals < 0.62 * med).sum())
        width = len(xs)
        frac = dark / width
        out.append((y, width, med, dark, frac))
    if not quiet:
        print(f"=== {dragon} {leg} {tag}  canvas {c.width}x{c.height}")
        for y, width, med, dark, frac in out:
            flag = "  <<<" if frac > 0.16 else ""
            print(f"  y{y:4d} w{width:4d} med{med:6.1f} dark{dark:4d} frac{frac:5.2f}{flag}")
    return out

if __name__ == "__main__":
    report(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
