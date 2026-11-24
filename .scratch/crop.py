"""Tight crop of a joint region, upscaled, saved for visual inspection."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

OUT = "/Users/mypc/games/dragon-island-tools/.scratch/"

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

def save(dragon, leg, tag):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    c, (x0, y0) = canvas_of(pieces, names)
    lo, paw = pieces[names[1]], pieces[names[2]]
    for label, j, r in (("knee", lo["joint"], 46), ("ankle", paw["joint"], 46)):
        cx, cy = int(j[0] - x0), int(j[1] - y0)
        box = (max(0, cx - r), max(0, cy - r), min(c.width, cx + r), min(c.height, cy + r))
        crop = c.crop(box).resize(((box[2]-box[0])*6, (box[3]-box[1])*6), Image.LANCZOS)
        crop.save(f"{OUT}{tag}_{leg}_{label}.png")
    print("saved", tag, leg)

if __name__ == "__main__":
    save(sys.argv[1], sys.argv[2], sys.argv[3])
