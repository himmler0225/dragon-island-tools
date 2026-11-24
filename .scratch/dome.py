"""Where exactly does the lower piece's dome poke out of the upper piece's silhouette?"""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

def comp(pieces, names):
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

def analyse(dragon, leg):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    acc_a, acc_l, who, (ox, oy) = comp(pieces, names)
    print(f"=== {dragon} {leg}")
    # per-layer canvas origin
    for j, n in enumerate(names):
        p = pieces[n]
        print(f"   {n}: at=({p['at'][0]:.1f},{p['at'][1]:.1f}) scale {p['scale']:.3f} canvas origin "
              f"({int(round(p['at'][0]-ox))},{int(round(p['at'][1]-oy))}) img {p['img'].size}")
    # the lower piece's dome: topmost opaque row of its own image
    la = np.asarray(pieces[names[1]]["img"])[..., 3] > 128
    rows = np.nonzero(la.any(axis=1))[0]
    print(f"   lower dome top image row {rows[0]}")
    lo = pieces[names[1]]
    s = lo["scale"]
    lx = int(round(lo["at"][0] - ox)); ly = int(round(lo["at"][1] - oy))
    dome_canvas_y = ly + int(rows[0] * s)
    print(f"   dome canvas y ~{dome_canvas_y}")
    for dy in range(-6, 30, 3):
        y = dome_canvas_y + dy
        if not (0 <= y < acc_a.shape[0]):
            continue
        # span of each layer at this canvas row
        out = []
        for j, n in enumerate(names):
            p = pieces[n]
            sc = p["scale"]
            im = np.asarray(p["img"].resize((round(p["img"].width*sc), round(p["img"].height*sc)), Image.LANCZOS))[..., 3] > 128
            px = int(round(p["at"][0] - ox)); py = int(round(p["at"][1] - oy))
            r = y - py
            if 0 <= r < im.shape[0]:
                xs = np.nonzero(im[r])[0]
                if len(xs):
                    out.append(f"{'ULP'[j]}:{xs[0]+px}-{xs[-1]+px}")
        m = acc_a[y] > 0.4
        dark = np.nonzero(m & (acc_l[y] < 0.62 * np.median(acc_l[y][m])))[0] if m.sum() > 6 else []
        dk = ("".join(f"{d}," for d in dark)) if len(dark) else "-"
        print(f"   y{y:4d} layers {' '.join(out):45s} dark xs {dk}")

for dragon in (sys.argv[1:] or ["ruby_dragon"]):
    cfg = CONFIGS[dragon]
    for leg in cfg["legs"]:
        analyse(dragon, leg)
