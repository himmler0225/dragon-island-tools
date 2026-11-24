"""Island HUD icons from one sheet of separate frameless icons on magenta (assets/ui/menu_icons.png): the frames are
drawn by the HUD's CSS. Writes frontend/public/ui/<name>.png over the older icons of tools/slice_hud_icons.py and the
resources of tools/slice_world.py, so run this one after them.

Usage: .venv/bin/python tools/slice_menu_icons.py
"""
import numpy as np
from PIL import Image

from lib.image import key_distance
from lib.paths import ASSETS, UI_OUT

ICON_SIZE = 192   # px, square: the crest and the gift are shown large
# name: box on the sheet. Not used: the crowned book (ranking is the trophy), the pickaxe (no such menu yet)
ICONS = {
    "profile": (105, 5, 545, 395), "ranking": (600, 75, 895, 355), "res_gold": (950, 105, 1240, 318), "res_stone": (1300, 125, 1575, 335),
    "gift": (38, 422, 248, 642), "battle": (275, 435, 495, 628), "friends": (750, 432, 966, 633), "quest": (995, 410, 1186, 658),
    "cards": (1236, 426, 1412, 642), "achievement": (1465, 422, 1616, 640),
    "team": (60, 686, 304, 888), "breed": (342, 675, 576, 888), "mail": (632, 682, 847, 868), "settings": (885, 698, 1074, 886),
    "shop": (1368, 676, 1609, 888),
}

src = key_distance(Image.open(ASSETS / "ui" / "menu_icons.png"), 30, 70)   # tight: pink feathers and the crest's pink glow stay
for name, box in ICONS.items():
    cell = src.crop(box)
    cell = cell.crop(cell.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox())
    side = max(cell.size)
    square = Image.new("RGBA", (side, side))
    square.alpha_composite(cell, ((side - cell.width) // 2, (side - cell.height) // 2))
    square.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS).save(UI_OUT / f"{name}.png", optimize=True)
    print(name, cell.size)
