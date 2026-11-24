"""Cut the Christmas event art (assets/events/christmas/) for the game -> frontend/public/events/christmas/.

  tree_1.png, tree_3.png, tree_4.png  the tree at stages 1, 3, 4 (one per image); sheet.png: the 4 stages small,
  the banner, the ornaments, the icon and the snow decor (stage 2 and the banner are taken from it)
  ornaments.png  8 ornament balls (4x2): red, gold, ice blue, green, violet, pink, candy, the rare dragon-egg one
  icon_decor.png the event icon, a snowy bush, a snowman, a lamp post, a pile of gifts

Writes tree_1..4.png (520 px tall), orn_1..8.png (128 px), icon.png (256 px), banner.png,
snowman.png, bush.png, lamp.png, gifts.png.

Usage: .venv/bin/python tools/slice_event.py
"""
from PIL import Image

from lib.image import components, cut, key_magenta
from lib.paths import ASSETS, OUT

SRC = ASSETS / "events" / "christmas"
DST = OUT.parent / "events" / "christmas"   # OUT is public/dragons


def pieces(name):
    """The islands of a magenta sheet, big ones only, in reading order (rows ~150 px)."""
    im = key_magenta(Image.open(SRC / f"{name}.png"))
    parts = [c for c in components(im) if c[0][2] * c[0][3] > 1500]
    parts.sort(key=lambda c: (c[0][1] // 150, c[0][0]))
    return im, parts


def save(img, name, height=None, width=None):
    if height:
        img = img.resize((round(img.width * height / img.height), height), Image.LANCZOS)
    elif width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    img.save(DST / name)
    print(name, img.size)


def main():
    DST.mkdir(parents=True, exist_ok=True)
    sheet, parts = pieces("sheet")
    pick = lambda x, y: min(parts, key=lambda c: (c[0][0] - x) ** 2 + (c[0][1] - y) ** 2)
    for k in (1, 3, 4):
        im, tree = pieces(f"tree_{k}")
        save(cut(im, *tree[0])[0], f"tree_{k}.png", height=520)
    save(cut(sheet, *pick(193, 101))[0], "tree_2.png", height=520)
    banner = pick(19, 406)
    save(cut(sheet, *banner)[0].convert("RGB"), "banner.png")
    im, parts = pieces("ornaments")
    for k, p in enumerate(parts, 1):
        save(cut(im, *p)[0], f"orn_{k}.png", height=128)
    im, parts = pieces("icon_decor")
    names = {(22, 26): "icon.png", (562, 127): "bush.png", (1019, 27): "snowman.png", (339, 472): "lamp.png", (732, 569): "gifts.png"}
    for p in parts:
        name = min(names.items(), key=lambda kv: (kv[0][0] - p[0][0]) ** 2 + (kv[0][1] - p[0][1]) ** 2)[1]
        save(cut(im, *p)[0], name, height=256)


if __name__ == "__main__":
    main()
