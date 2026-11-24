"""Building art by level: assets/buildings/levels.png, 3 rows on magenta (gold tree stump, wise mushroom, stone
mine), each 5 growth stages left to right (levels 1, 4, 7, 10, 15) -> frontend/public/buildings/<type>_t<1..5>.png,
cut out at the sheet's size (the game draws them at BUILDING_SCALE).

Usage: .venv/bin/python tools/slice_buildings.py
"""
from PIL import Image

from lib.image import components, cut, key_magenta
from lib.paths import ASSETS, PUBLIC

ROWS = ["gold_mine", "training_ground", "stone_quarry"]

if __name__ == "__main__":
    img = key_magenta(Image.open(ASSETS / "buildings" / "levels.png"))
    parts = [c for c in components(img) if c[0][2] * c[0][3] > 4000]
    parts.sort(key=lambda c: c[0][1] + c[0][3])   # by bottom edge: the rows stand on three ground lines
    rows, cur = [], []
    for c in parts:
        if cur and (c[0][1] + c[0][3]) - (cur[-1][0][1] + cur[-1][0][3]) > 80:
            rows.append(cur); cur = []
        cur.append(c)
    rows.append(cur)
    assert [len(r) for r in rows] == [5, 5, 5], [len(r) for r in rows]
    for name, row in zip(ROWS, rows):
        for k, c in enumerate(sorted(row, key=lambda c: c[0][0]), 1):
            piece, _ = cut(img, *c)
            piece.save(PUBLIC / "buildings" / f"{name}_t{k}.png")
            print(f"{name}_t{k}", piece.size)
