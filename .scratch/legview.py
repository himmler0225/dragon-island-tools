"""Full-leg ASCII render + seam detector (contiguous dark run across the limb)."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

def composite(pieces, names):
    x0 = min(pieces[n]["at"][0] for n in names) - 30
    y0 = min(pieces[n]["at"][1] for n in names) - 30
    W = int(max(pieces[n]["at"][0] + pieces[n]["img"].width * pieces[n]["scale"] for n in names) - x0) + 30
    H = int(max(pieces[n]["at"][1] + pieces[n]["img"].height * pieces[n]["scale"] for n in names) - y0) + 30
    acc_a = np.zeros((H, W)); acc_l = np.zeros((H, W)); who = np.full((H, W), -1)
    for j, n in reversed(list(enumerate(names))):
        p = pieces[n]
        s = p["scale"]
        im = p["img"].resize((round(p["img"].width * s), round(p["img"].height * s)), Image.LANCZOS)
        a = np.asarray(im).astype(float)
        al = a[..., 3] / 255.0
        lum = a[..., :3].mean(axis=2)
        ox = int(round(p["at"][0] - x0)); oy = int(round(p["at"][1] - y0))
        ih, wd = al.shape
        yy, xx = np.mgrid[0:H, 0:W]
        sy = np.clip(yy - oy, 0, ih - 1); sx = np.clip(xx - ox, 0, wd - 1)
        inside = (yy >= oy) & (yy < oy + ih) & (xx >= ox) & (xx < ox + wd)
        src_a = np.where(inside, al[sy, sx], 0.0)
        acc_a = acc_a * (1 - src_a) + src_a
        acc_l = np.where(src_a > 0.5, lum[sy, sx], acc_l)
        who = np.where(src_a > 0.5, j, who)
    return acc_a, acc_l, who, (x0, y0)

def seams(acc_a, acc_l, who):
    """Rows where a dark run spans >= 45% of the limb width."""
    out = []
    for y in range(acc_a.shape[0]):
        m = acc_a[y] > 0.5
        if m.sum() < 15:
            continue
        xs = np.nonzero(m)[0]
        vals = acc_l[y][m]
        body = np.median(vals)
        thr = 0.6 * body
        dark = vals < thr
        # longest contiguous run of dark inside the span
        idx = np.nonzero(dark)[0]
        if len(idx) == 0:
            continue
        best = run = 1
        for i in range(1, len(idx)):
            run = run + 1 if idx[i] == idx[i - 1] + 1 else 1
            best = max(best, run)
        span = len(xs)
        if best >= 0.45 * span and best >= 6:
            out.append((y, span, best, round(body, 1), round(float(vals[dark].mean()), 1)))
    return out

def show(acc_a, acc_l, who, step=3, x0=0, x1=None, y0=0, y1=None):
    H, W = acc_a.shape
    x1 = x1 or W; y1 = y1 or H
    for y in range(y0, y1, step):
        line = ""
        for x in range(x0, x1, step):
            if acc_a[y, x] < 0.35:
                line += "."
            else:
                v = acc_l[y, x]
                line += "#" if v < 70 else ("+" if v < 110 else ("-" if v < 165 else "o"))
        print(f"  y{y:4d} |{line}|")

if __name__ == "__main__":
    dragon, leg = sys.argv[1], sys.argv[2]
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    acc_a, acc_l, who, (ox, oy) = composite(pieces, names)
    print(f"=== {dragon} {leg} canvas {acc_a.shape}")
    show(acc_a, acc_l, who, step=3)
    print("--- seam rows (dark run >= 45% of width):")
    for s in seams(acc_a, acc_l, who):
        print("  ", s)
