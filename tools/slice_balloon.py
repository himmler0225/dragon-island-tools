"""Food balloon + hunger icons -> frontend/public/balloon/.

  assets/balloon/balloon.png   3 cells side by side on magenta: loaded balloon (food net hanging under
                               the basket), empty balloon, food crate on a parachute
  assets/balloon/hunger.png    4 cells side by side on magenta: "hungry" bubble (ham), "starving"
                               bubble (cracked bowl), drool drop, stomach-growl swirl

Writes balloon_full.png + balloon_empty.png (one shared crop, so swapping them does not jump),
crate.png and hunger_1..4.png.
Usage: .venv/bin/python tools/slice_balloon.py
"""
import numpy as np
from PIL import Image

from lib.image import key_magenta
from lib.paths import ASSETS, PUBLIC

SRC, OUT = ASSETS / "balloon", PUBLIC / "balloon"


def cells(img, cols, rows):
    cw, ch = img.width / cols, img.height / rows
    return [img.crop((round(c * cw), round(r * ch), round((c + 1) * cw), round((r + 1) * ch)))
            for r in range(rows) for c in range(cols)]


def bbox(*imgs, pad=4):
    """One box around the opaque pixels of every image (same-size cells)."""
    a = np.max([np.asarray(im)[..., 3] for im in imgs], axis=0) > 12
    ys, xs = np.nonzero(a)
    return (max(0, xs.min() - pad), max(0, ys.min() - pad), xs.max() + pad + 1, ys.max() + pad + 1)


def save(im, name, size):
    im = im.copy()
    im.thumbnail((size, size), Image.LANCZOS)
    im.save(OUT / f"{name}.png", optimize=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    full, empty, crate = cells(key_magenta(Image.open(SRC / "balloon.png")), 3, 1)
    box = bbox(full, empty)
    save(full.crop(box), "balloon_full", 520)
    save(empty.crop(box), "balloon_empty", 520)
    save(crate.crop(bbox(crate)), "crate", 260)
    for k, im in enumerate(cells(key_magenta(Image.open(SRC / "hunger.png")), 4, 1)):
        save(im.crop(bbox(im)), f"hunger_{k + 1}", 180)
    print(f"wrote balloon_full/empty, crate, hunger_1..4 to {OUT}")


if __name__ == "__main__":
    main()
