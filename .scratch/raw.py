"""Dump the top rows of the lower piece and the bottom rows of the upper piece (raw pixels)."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

CH = "@%#*+=-:. "

def dump(a, y0, y1, x0=0, x1=None, step=1):
    H, W = a.shape[:2]
    x1 = x1 or W
    print(f"   x{x0}..{x1}")
    for y in range(y0, y1):
        line = ""
        for x in range(x0, x1, step):
            if not (0 <= y < H and 0 <= x < W):
                line += " "; continue
            if a[y, x, 3] < 128:
                line += " "
            else:
                v = a[y, x, :3].mean()
                line += CH[min(len(CH) - 1, int(v / 256 * len(CH)))]
        print(f"  y{y:4d} |{line}|")

def analyse(dragon, leg):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    print(f"=== {dragon} {leg}")
    for label in ("upper", "lower", "paw"):
        p = pieces[f"{leg}_{label}"]
        a = np.asarray(p["img"]).astype(float)
        rows = np.nonzero(a[..., 3].any(axis=1))[0]
        cols = np.nonzero(a[..., 3].any(axis=0))[0]
        print(f"-- {label}: img {p['img'].width}x{p['img'].height} rows {rows[0]}..{rows[-1]} cols {cols[0]}..{cols[-1]} bbox {p['bbox']}")
        if label == "upper":
            dump(a, max(0, rows[-1] - 26), rows[-1] + 1)
        else:
            dump(a, rows[0], min(a.shape[0], rows[0] + 26))

if __name__ == "__main__":
    analyse(sys.argv[1], sys.argv[2])
