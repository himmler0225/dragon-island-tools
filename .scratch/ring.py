"""Measure the dome (dark outline ring) thickness of the lower leg pieces, pre-crouch."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

for dragon in (sys.argv[1:] or ["ruby_dragon", "frost_dragon"]):
    cfg = {**CONFIGS[dragon]}
    cfg.pop("crouch", None)
    pieces = B.build(cfg)
    print(f"===== {dragon}")
    for leg in cfg["legs"]:
        for seg in ("lower", "paw"):
            p = pieces[f"{leg}_{seg}"]
            a = np.asarray(p["img"]).astype(float)
            al = a[..., 3]
            lum = a[..., :3].mean(axis=2)
            rows = np.nonzero((al > 128).any(axis=1))[0]
            if not len(rows):
                continue
            top = rows[0]
            # depth at which the row stops being "outline" (dark) everywhere
            depth = 0
            for r in range(top, min(top + 60, a.shape[0])):
                m = al[r] > 128
                if not m.any():
                    break
                v = lum[r][m]
                if v.mean() > 0.62 * np.median(lum[int(top + 30):int(top + 60)][al[int(top + 30):int(top + 60)] > 128]) if (al[int(top + 30):int(top + 60)] > 128).any() else True:
                    depth = r - top
                    break
            print(f"  {leg}_{seg}: img {p['img'].width}x{p['img'].height} bbox {p['bbox']} "
                  f"dome_top_row {top} ring_depth {depth}")
            # width of the dome at a few depths
            for d in (0, 2, 4, 6, 8, 12, 16, 20, 26):
                r = top + d
                if r < a.shape[0]:
                    xs = np.nonzero(al[r] > 128)[0]
                    print(f"      depth {d:3d} row {r:4d} width {len(xs):4d} lummean "
                          f"{(lum[r][al[r] > 128].mean() if (al[r] > 128).any() else -1):6.1f}")
