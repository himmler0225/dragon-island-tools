"""Geometry of the joint overlap: where the lower piece's dome sits vs the upper piece's silhouette."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

def widths(img, rows):
    a = np.asarray(img)[..., 3] > 128
    out = {}
    for r in rows:
        if r < 0 or r >= a.shape[0]:
            continue
        xs = np.nonzero(a[r])[0]
        out[r] = (int(xs[0]), int(xs[-1]), len(xs)) if len(xs) else None
    return out

for dragon in (sys.argv[1:] or ["ruby_dragon", "frost_dragon"]):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    print(f"===== {dragon}  leg_pull={cfg['leg_pull']} leg_scale={cfg['leg_scale']}")
    for leg in cfg["legs"]:
        up, lo, paw = (pieces[f"{leg}_{s}"] for s in ("upper", "lower", "paw"))
        ua = np.asarray(up["img"])[..., 3] > 128
        la = np.asarray(lo["img"])[..., 3] > 128
        pa = np.asarray(paw["img"])[..., 3] > 128
        # layout rows
        uy = up["at"][1]; ly = lo["at"][1]; py = paw["at"][1]
        # dome: top rows of the lower piece
        dome_rows = [r for r in range(0, 24) if la[r].any()]
        dome_top = dome_rows[0]
        dome_w = int(la[dome_top + 2].sum()) if dome_top + 2 < la.shape[0] else 0
        # where is the dome in layout?
        dome_y_layout = ly + dome_top * up["scale"]
        # thigh silhouette widths near its bottom (layout rows)
        u_h = up["img"].height
        rows = {}
        for r in range(u_h - 1, max(-1, u_h - 60), -4):
            xs = np.nonzero(ua[r])[0]
            if len(xs):
                rows[r] = (int(xs[0]), int(xs[-1]), len(xs))
        # thigh layout row for a given image row
        print(f"-- {leg}: upper img {up['img'].size} at y{uy:.0f}, lower at y{ly:.0f}, paw at y{py:.0f}")
        print(f"   lower dome top image row {dome_top}, width@dome+2 {dome_w}, layout y {dome_y_layout:.1f}")
        # thigh bottom rows (image row -> width)
        print("   thigh bottom rows:", {r: v[2] for r, v in sorted(rows.items())[:12]})
        # which thigh image row is at the dome's layout y?
        u_scale = up["scale"]
        thigh_row_at_dome = (dome_y_layout - uy) / u_scale
        print(f"   thigh image row at dome y = {thigh_row_at_dome:.0f}")
