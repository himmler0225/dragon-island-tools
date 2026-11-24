"""Row-luminance profile of a composed leg, to locate dark seam rows objectively."""
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
                           int(max(y + i.height for i, _, y in placed) - y0) + 1), (255, 255, 255, 255))
    for img, x, y in reversed(placed):
        c.alpha_composite(img, (round(x - x0), round(y - y0)))
    return c, (x0, y0)

def profile(dragon, leg, center=0.5, halfw=None):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    c, (x0, y0) = canvas_of(pieces, names)
    a = np.asarray(c).astype(float)
    lum = a[..., :3].mean(axis=2); al = a[..., 3]
    # horizontal centre of the limb at each row (mean of opaque xs)
    print(f"=== {dragon} {leg}  canvas {c.width}x{c.height}")
    for y in range(c.height):
        m = al[y] > 200
        if m.sum() < 8:
            continue
        xs = np.nonzero(m)[0]
        cx = int(xs.mean())
        w = halfw or max(6, len(xs) // 6)
        x0r, x1r = max(0, cx - w), min(c.width, cx + w + 1)
        vals = lum[y, x0r:x1r][al[y, x0r:x1r] > 200]
        if len(vals) < 5:
            continue
        print(f" y{y:4d} cx{cx:4d} w{len(xs):4d} mean {vals.mean():6.1f} min {vals.min():6.1f} p10 {np.percentile(vals,10):6.1f}")

if __name__ == "__main__":
    profile(sys.argv[1], sys.argv[2])
