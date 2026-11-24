"""Composite the leg layers in layout space (legs_down order: paw, lower, upper) and report
which layer owns each pixel + darkness, around a joint."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

CH = "@%#*+=-:. "

def analyse(dragon, leg, w=70, h=40, step=2):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    x0 = min(pieces[n]["at"][0] for n in names) - 30
    y0 = min(pieces[n]["at"][1] for n in names) - 30
    W = int(max(pieces[n]["at"][0] + pieces[n]["img"].width * pieces[n]["scale"] for n in names) - x0) + 30
    H = int(max(pieces[n]["at"][1] + pieces[n]["img"].height * pieces[n]["scale"] for n in names) - y0) + 30
    acc_a = np.zeros((H, W)); acc_l = np.zeros((H, W)); who = np.full((H, W), -1)
    for j, n in reversed(list(enumerate(names))):   # draw paw, lower, upper
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
    lo, paw = pieces[names[1]], pieces[names[2]]
    for label, jt in (("knee", lo["joint"]), ("ankle", paw["joint"])):
        cx, cy = int(jt[0] - x0), int(jt[1] - y0)
        print(f"--- {dragon} {leg} {label} canvas({cx},{cy})")
        print("  darkness (# dark, + mid, - light, . bg)")
        for y in range(cy - h // 2, cy + h // 2, step):
            line = ""
            for x in range(cx - w // 2, cx + w // 2, step):
                if not (0 <= y < H and 0 <= x < W) or acc_a[y, x] < 0.35:
                    line += "."; continue
                v = acc_l[y, x]
                line += "#" if v < 70 else ("+" if v < 110 else ("-" if v < 165 else "o"))
            print(f"  y{y:4d} |{line}|")
        print("  owner (0=upper 1=lower 2=paw)")
        for y in range(cy - h // 2, cy + h // 2, step):
            line = "".join(str(who[y, x]) if (0 <= y < H and 0 <= x < W and who[y, x] >= 0) else "." for x in range(cx - w // 2, cx + w // 2, step))
            print(f"  y{y:4d} |{line}|")

if __name__ == "__main__":
    analyse(sys.argv[1], sys.argv[2])
