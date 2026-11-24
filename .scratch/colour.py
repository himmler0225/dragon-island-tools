"""Colour probe: thigh's lower body vs shin's body (what the joint should melt into)."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

def med_rgb(a, rows):
    m = a[rows][a[rows][..., 3] > 200]
    if not len(m):
        return None
    return [round(float(np.median(m[:, i])), 1) for i in range(3)]

for dragon in (sys.argv[1:] or ["ruby_dragon", "frost_dragon"]):
    cfg = {**CONFIGS[dragon]}
    cfg.pop("crouch", None)
    pieces = B.build(cfg)
    print(f"===== {dragon}")
    for leg in cfg["legs"]:
        up = pieces[f"{leg}_upper"]; lo = pieces[f"{leg}_lower"]; paw = pieces[f"{leg}_paw"]
        ua = np.asarray(up["img"]).astype(float); la = np.asarray(lo["img"]).astype(float); pa = np.asarray(paw["img"]).astype(float)
        uh = ua.shape[0]; lh = la.shape[0]; ph = pa.shape[0]
        print(f"-- {leg}")
        print(f"   thigh bottom band (rows {uh-40}..{uh-20}) rgb {med_rgb(ua, slice(uh-40, uh-20))}")
        print(f"   thigh cap band    (rows {uh-16}..{uh})    rgb {med_rgb(ua, slice(uh-16, uh))}")
        print(f"   shin body         (rows 20..50)            rgb {med_rgb(la, slice(20, 50))}")
        print(f"   shin cap band     (rows 0..14)             rgb {med_rgb(la, slice(0, 14))}")
        print(f"   shin lower body   (rows {lh-40}..{lh-20})  rgb {med_rgb(la, slice(lh-40, lh-20))}")
        print(f"   paw cap band      (rows 0..14)             rgb {med_rgb(pa, slice(0, 14))}")
        print(f"   paw body          (rows 20..50)            rgb {med_rgb(pa, slice(20, 50))}")
