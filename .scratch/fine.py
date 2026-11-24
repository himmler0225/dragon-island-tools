"""Fine dump around a joint: per-row owner runs + luminance, x resolution 1."""
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

def dump(dragon, leg, label, r=46):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    acc_a, acc_l, who, (ox, oy) = composite(pieces, names)
    lo, paw = pieces[names[1]], pieces[names[2]]
    jt = lo["joint"] if label == "knee" else paw["joint"]
    cx, cy = int(jt[0] - ox), int(jt[1] - oy)
    print(f"=== {dragon} {leg} {label} canvas({cx},{cy})")
    for y in range(cy - r, cy + r):
        if not (0 <= y < acc_a.shape[0]):
            continue
        m = acc_a[y] > 0.4
        if m.sum() < 4:
            continue
        xs = np.nonzero(m)[0]
        seg = []
        prev = -9; run = None
        for x in xs:
            w = int(who[y, x])
            if w != prev:
                if run: seg.append(run)
                run = [w, x, x, who[y, x]]
                prev = w
            else:
                run[2] = x
        if run: seg.append(run)
        runs = " ".join(f"{'ULP'[s[0]]}{s[1]}-{s[2]}" for s in seg)
        # darkest pixel in the row + its x
        vals = acc_l[y][m]
        di = int(np.argmin(vals))
        print(f" y{y:4d} lum min {vals.min():5.1f} @{int(xs[di]):4d} med {np.median(vals):5.1f} | {runs}")

if __name__ == "__main__":
    dump(sys.argv[1], sys.argv[2], sys.argv[3])
