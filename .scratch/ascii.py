"""ASCII render of a joint region so the seam can be read numerically."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

CH = " .:-=+*#%@"

def canvas_of(pieces, names):
    placed = []
    for n in names:
        p = pieces[n]
        w = round(p["img"].width * p["scale"]); h = round(p["img"].height * p["scale"])
        placed.append((p["img"].resize((w, h), Image.LANCZOS), p["at"][0], p["at"][1]))
    x0 = min(x for _, x, _ in placed) - 30
    y0 = min(y for _, _, y in placed) - 30
    c = Image.new("RGBA", (int(max(x + i.width for i, x, _ in placed) - x0) + 1,
                           int(max(y + i.height for i, _, y in placed) - y0) + 1), (255, 255, 255, 255))
    for img, x, y in reversed(placed):
        c.alpha_composite(img, (round(x - x0), round(y - y0)))
    return c, (x0, y0)

def ascii_region(canvas, cx, cy, w=48, h=26, step=2):
    a = np.asarray(canvas).astype(float)
    lum = a[..., :3].mean(axis=2)
    al = a[..., 3]
    print(f"    (canvas {canvas.width}x{canvas.height}) region x{cx-w//2}..{cx+w//2} y{cy-h//2}..{cy+h//2}")
    for y in range(cy - h // 2, cy + h // 2, step):
        line = ""
        for x in range(cx - w // 2, cx + w // 2, step):
            if not (0 <= y < canvas.height and 0 <= x < canvas.width):
                line += " "; continue
            if al[y, x] < 128:
                line += " "
            else:
                v = lum[y, x]
                line += CH[min(len(CH) - 1, int(v / 256 * len(CH)))]
        print(f"  y{y:4d} |{line}|")

if __name__ == "__main__":
    dragon, leg = sys.argv[1], sys.argv[2]
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    c, (x0, y0) = canvas_of(pieces, names)
    lo, paw = pieces[names[1]], pieces[names[2]]
    for label, j in (("knee", lo["joint"]), ("ankle", paw["joint"])):
        print(f"--- {dragon} {leg} {label}")
        ascii_region(c, int(j[0] - x0), int(j[1] - y0))
