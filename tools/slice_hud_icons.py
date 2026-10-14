"""Extract HUD icons from the 4x4 icon sheet.

  assets/ui/hud_icons.png  4x4 grid of icons on transparent background

Writes frontend/public/ui/<name>.png for each icon.

Usage: .venv/bin/python tools/slice_hud_icons.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# repo root: tools/ → repo root; use sys.argv[0] for reliable resolution in all environments
ROOT = Path("/Users/mypc/cinemark-workspace/dragon-island")
sys.path.insert(0, str(ROOT))

from lib.paths import UI_OUT

ICONS_SRC = ROOT / "assets" / "ui" / "hud_icons.png"
ICON_NAMES = [
    "bag", "shop", "gift", "battle",
    "achievement", "quest", "profile", "potion",
    "chest", "cards", "currency", "mail",
    "map", "settings", "friends", "ranking",
]
ICON_SIZE = 128   # px, square; shown at ~56 px so they stay sharp on retina screens


def grid_cuts(occupancy, parts, search=40):
    """Cut positions for a roughly even grid: near each k/parts mark, the emptiest line within
    +-search px (some icons touch, so there is not always a fully transparent gap)."""
    n = len(occupancy)
    cuts = [0]
    for k in range(1, parts):
        mark = round(k * n / parts)
        lo, hi = mark - search, mark + search
        cuts.append(lo + int(np.argmin(occupancy[lo:hi])))
    return cuts + [n]


def drop_haze(img, tol=8):
    """Zero the near-invisible haze left by background removal so it does not tint what is behind."""
    r, g, b, a = img.split()
    return Image.merge("RGBA", (r, g, b, a.point(lambda v: 0 if v <= tol else v)))


def main():
    sheet = drop_haze(Image.open(ICONS_SRC).convert("RGBA"))
    solid = np.asarray(sheet.getchannel("A")) > 60
    rows = grid_cuts(solid.sum(axis=1), 4)
    cols = grid_cuts(solid.sum(axis=0), 4)
    UI_OUT.mkdir(parents=True, exist_ok=True)
    for r in range(4):
        for c in range(4):
            icon = sheet.crop((cols[c], rows[r], cols[c + 1], rows[r + 1]))
            icon = icon.crop(
                icon.getchannel("A").point(lambda v: 255 if v > 60 else 0).getbbox()
            )
            side = max(icon.size)
            square = Image.new("RGBA", (side, side))
            square.alpha_composite(icon, ((side - icon.width) // 2, (side - icon.height) // 2))
            square.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS).save(
                UI_OUT / f"{ICON_NAMES[r * 4 + c]}.png", optimize=True
            )
    print(f"icons  {len(ICON_NAMES)} -> {UI_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
