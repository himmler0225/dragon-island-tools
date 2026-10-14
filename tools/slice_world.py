"""Islands, buildings and resource icons -> frontend/public/.

  assets/island/<id>.png            one floating island (magenta or transparent background)
  assets/buildings/<type>.png       3 upgrade levels side by side on magenta
  assets/ui/resources.png           gold, exp, evolution stone side by side on magenta

Writes:
  frontend/public/islands/<id>.png              background removed, cropped to the island
  frontend/public/buildings/<type>_<1..3>.png   one file per level, cropped
  frontend/public/ui/res_<gold|exp|stone>.png

Usage: .venv/bin/python tools/slice_world.py
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path("/Users/mypc/cinemark-workspace/dragon-island")
sys.path.insert(0, str(ROOT))

from lib.image import key_magenta
from lib.paths import ASSETS, PUBLIC

RESOURCES = ["gold", "exp", "stone"]


def keyed(path):
    img = Image.open(path).convert("RGBA")
    # images that already have transparency are used as they are
    return img if img.getchannel("A").getextrema()[0] < 250 else key_magenta(img)


def main_part(img, min_share=0.02):
    """Drop specks: keep opaque regions with at least `min_share` of the biggest region's area."""
    arr = np.asarray(img).copy()
    solid = (arr[..., 3] > 40).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(cv2.dilate(solid, np.ones((9, 9), np.uint8)))
    if n <= 2:
        return img.crop(img.getchannel("A").getbbox())
    biggest = stats[1:, 4].max()
    keep = [i for i in range(1, n) if stats[i][4] >= min_share * biggest]
    arr[~np.isin(labels, keep)] = 0
    out = Image.fromarray(arr, "RGBA")
    return out.crop(out.getchannel("A").getbbox())


def cells(img, count):
    """Split a row of `count` items at the widest empty column gaps (items differ in width, so an
    even grid would cut slivers off the neighbours)."""
    filled = (np.asarray(img)[..., 3] > 40).sum(axis=0) > 2
    runs, start = [], None   # empty column runs between items
    for x, f in enumerate(list(filled) + [True]):
        if not f and start is None:
            start = x
        elif f and start is not None:
            if 0 < start and x < img.width:
                runs.append((x - start, start, x))
            start = None
    cuts = sorted((a + b) // 2 for _, a, b in sorted(runs, reverse=True)[:count - 1])
    edges = [0, *cuts, img.width]
    return [img.crop((edges[k], 0, edges[k + 1], img.height)) for k in range(count)]


def main():
    (PUBLIC / "islands").mkdir(parents=True, exist_ok=True)
    (PUBLIC / "buildings").mkdir(parents=True, exist_ok=True)
    for path in sorted((ASSETS / "island").glob("*.png")):
        out = main_part(keyed(path))
        out.save(PUBLIC / "islands" / path.name, optimize=True)
        print(f"island {path.stem:16s} {out.size}")
    for path in sorted((ASSETS / "buildings").glob("*.png")):
        for lvl, cell in enumerate(cells(keyed(path), 3), 1):
            out = main_part(cell, min_share=0.004)   # keep small floating crystals
            out.save(PUBLIC / "buildings" / f"{path.stem}_{lvl}.png", optimize=True)
        print(f"building {path.stem:16s} 3 levels")
    for name, cell in zip(RESOURCES, cells(keyed(ASSETS / "ui" / "resources.png"), 3)):
        out = main_part(cell)
        out.thumbnail((160, 160), Image.LANCZOS)
        out.save(PUBLIC / "ui" / f"res_{name}.png", optimize=True)
    print("resources", RESOURCES)


if __name__ == "__main__":
    main()
