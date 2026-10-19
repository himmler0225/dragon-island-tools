"""Battle screen art -> frontend/public/battle/.

  assets/battle/background.png   wide battlefield painting (kept as JPEG)
  assets/battle/tower_ally.png   crystal dragon statue (left base), on magenta
  assets/battle/tower_enemy.png  stone dragon statue with the red gem (right base), on magenta
  assets/battle/ui.png           UI parts on magenta, picked by their bounding box (PARTS)

Usage: .venv/bin/python tools/slice_battle.py
"""
import numpy as np
from PIL import Image

from lib.image import components, cut, key_magenta
from lib.paths import ASSETS, PUBLIC

SRC, OUT = ASSETS / "battle", PUBLIC / "battle"

# name -> top-left of the part's bounding box on ui.png (picks the island)
PARTS = {
    "card": (37, 25), "card_on": (381, 20), "card_dead": (763, 25), "star": (1253, 85),
    "hp_frame": (31, 346), "hp_fill": (953, 375),
    "mana_frame": (40, 465), "mana_fill": (993, 507),
    "skill_btn": (42, 603), "skill_btn_on": (316, 603),
    "wave_tag": (588, 622), "timer": (1179, 623),
    "track": (42, 848), "track_fill": (178, 934),
}


def trimmed(img):
    ys, xs = np.nonzero(np.asarray(img)[..., 3] > 12)
    return img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bg = Image.open(SRC / "background.png").convert("RGB")
    bg.thumbnail((2400, 1400))
    bg.save(OUT / "background.jpg", quality=86)
    for name in ("tower_ally", "tower_enemy"):
        img = trimmed(key_magenta(Image.open(SRC / f"{name}.png")))
        img.thumbnail((640, 640), Image.LANCZOS)
        img.save(OUT / f"{name}.png", optimize=True)
    ui = key_magenta(Image.open(SRC / "ui.png"))
    parts = components(ui, min_area=800)
    for name, xy in PARTS.items():
        bbox, mask = min(parts, key=lambda c: (c[0][0] - xy[0]) ** 2 + (c[0][1] - xy[1]) ** 2)
        img, _ = cut(ui, bbox, mask, pad=0)
        trimmed(img).save(OUT / f"{name}.png", optimize=True)
    print(f"wrote background, 2 towers, {len(PARTS)} UI parts to {OUT}")


if __name__ == "__main__":
    main()
