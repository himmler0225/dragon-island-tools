"""Diagnostic: render each segment of a leg separately to see where the dark seam comes from."""
import sys
sys.path.insert(0, "/Users/mypc/games/dragon-island-tools/tools")
from pathlib import Path
import numpy as np
from PIL import Image
import build_rig as B
from rig_configs import CONFIGS

OUT = Path("/Users/mypc/games/dragon-island-tools/.scratch")

def zoom(canvas, cx, cy, r=58, f=5):
    box = (max(0, int(cx - r)), max(0, int(cy - r)), min(canvas.width, int(cx + r)), min(canvas.height, int(cy + r)))
    c = canvas.crop(box)
    return c.resize((c.width * f, c.height * f), Image.NEAREST)

def run(dragon, leg, tag):
    cfg = CONFIGS[dragon]
    pieces = B.build(cfg)
    names = [f"{leg}_{s}" for s in ("upper", "lower", "paw")]
    for n in names:
        p = pieces[n]
        w = round(p["img"].width * p["scale"]); h = round(p["img"].height * p["scale"])
        im = p["img"].resize((w, h), Image.LANCZOS)
        # put on white
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        bg.save(OUT / f"{tag}_solo_{n}.png")
    print("solo layers written for", dragon, leg)

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3])
