"""Correct joint analysis: composite on a transparent canvas, keep alpha."""
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

CH = "@%#*+=-:. "

def ascii_region(a, cx, cy, w=60, h=30, step=2):
    H, W = a.shape[:2]
    print(f"    region x{cx-w//2}..{cx+w//2} y{cy-h//2}..{cy+h//2}  (canvas {W}x{H})")
    for y in range(cy - h // 2, cy + h // 2, step):
        line = ""
        for x in range(cx - w // 2, cx + w // 2, step):
            if not (0 <= y < H and 0 <= x < W) or a[y, x, 3] < 128:
                line += " "
            else:
                v = a[y, x, :3].mean()
                line += CH[min(len(CH) - 1, int(v / 256 * len(CH)))]
        print(f"  y{y:4d} |{line}|")

def analyse(dragon, leg):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    c, (x0, y0) = canvas_of(pieces, names)
    a = np.asarray(c)
    up, lo, paw = (pieces[n] for n in names)
    print(f"=== {dragon} {leg} canvas {c.width}x{c.height}")
    for label, j in (("knee", lo["joint"]), ("ankle", paw["joint"])):
        print(f"--- {label} layout joint {tuple(round(float(v),1) for v in j)}")
        ascii_region(a, int(j[0] - x0), int(j[1] - y0))

if __name__ == "__main__":
    analyse(sys.argv[1], sys.argv[2])
