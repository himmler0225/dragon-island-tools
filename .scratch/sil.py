"""Silhouette of each leg piece: width per row (source px)."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

for dragon in (sys.argv[1:] or ["ruby_dragon", "frost_dragon"]):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    leg = list(cfg["legs"])[0]
    for seg in ("upper", "lower", "paw"):
        p = pieces[f"{leg}_{seg}"]
        a = np.asarray(p["img"])[..., 3] > 128
        h = a.shape[0]
        print(f"--- {dragon} {leg} {seg}: img {p['img'].width}x{p['img'].height} scale {p['scale']:.3f}")
        for y in range(0, min(h, 90), 2):
            w = int(a[y].sum())
            if w:
                print(f"   row{y:4d} width {w:4d}")
