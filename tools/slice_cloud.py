"""Riding cloud for dragons that fly on a cloud instead of wings.

  assets/dragons/<id>/cloud.png   on magenta: one big cloud platform + a few small cloud puffs

Writes frontend/public/dragons/<id>/cloud_main.png and cloud_1..N.png (puffs, left to right).

Usage: .venv/bin/python tools/slice_cloud.py [dragon_id ...]   (default: every dragon with cloud.png)
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from build_rig import components, cut  # noqa: E402
from slice_sheet import key_magenta  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DRAGONS = ROOT / "assets" / "dragons"
OUT = ROOT / "frontend" / "public" / "dragons"


def main(ids):
    for dragon_id in ids:
        img = key_magenta(Image.open(DRAGONS / dragon_id / "cloud.png"))
        parts = sorted(components(img), key=lambda c: -c[0][2] * c[0][3])
        dst = OUT / dragon_id
        dst.mkdir(parents=True, exist_ok=True)
        main_cloud, _ = cut(img, *parts[0])
        main_cloud.save(dst / "cloud_main.png", optimize=True)
        puffs = sorted(parts[1:], key=lambda c: c[0][0])
        for k, (bbox, mask) in enumerate(puffs, 1):
            piece, _ = cut(img, bbox, mask)
            piece.thumbnail((320, 320), Image.LANCZOS)
            piece.save(dst / f"cloud_{k}.png", optimize=True)
        print(f"{dragon_id}: cloud_main {main_cloud.size} + {len(puffs)} puffs")


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(p.parent.name for p in DRAGONS.glob("*/cloud.png")))
