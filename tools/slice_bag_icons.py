"""Dragon bag icons -> frontend/public/ui/bag/.

  assets/ui/bag_icons.png   3x3 grid of round badges on magenta, in this order:
                            info, gem, store / wipe, tab_all, tab_rare / tab_epic, tab_event, tab_legend

Each badge is trimmed and saved at most 160 px (BagPanel.tsx shows them, an emoji stands in when missing).
Usage: .venv/bin/python tools/slice_bag_icons.py
"""
from PIL import Image

from lib.image import components, cut, key_distance
from lib.paths import ASSETS, UI_OUT

NAMES = ["info", "gem", "store", "wipe", "tab_all", "tab_rare", "tab_epic", "tab_event", "tab_legend"]


def main():
    # distance keying: the purple orb (tab_epic) is close enough to magenta for key_magenta to eat it
    img = key_distance(Image.open(ASSETS / "ui" / "bag_icons.png"))
    parts = components(img)
    assert len(parts) == len(NAMES), f"expected {len(NAMES)} badges, found {len(parts)}"
    # reading order: rows top to bottom, then left to right
    row_h = img.height / 3
    parts.sort(key=lambda c: (int((c[0][1] + c[0][3] / 2) // row_h), c[0][0]))
    out = UI_OUT / "bag"
    out.mkdir(parents=True, exist_ok=True)
    for name, (bbox, mask) in zip(NAMES, parts):
        icon, _ = cut(img, bbox, mask)
        icon.thumbnail((160, 160), Image.LANCZOS)
        icon.save(out / f"{name}.png", optimize=True)
    print(f"wrote {len(NAMES)} icons to {out}")


if __name__ == "__main__":
    main()
