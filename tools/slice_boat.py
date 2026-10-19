"""Food boat + food items -> frontend/public/boat/.

  assets/boat/boat.png   2 cells side by side on magenta: loaded boat (left), empty boat (right)
  assets/boat/food.png   4 x 2 grid on magenta: ham, fish, apple, dragon fruit /
                         crate burst, water splash, food pile on grass, heart

Writes boat_full.png, boat_empty.png, food_1..8.png (trimmed).
Usage: .venv/bin/python tools/slice_boat.py
"""
import numpy as np
from PIL import Image

from lib.image import key_magenta
from lib.paths import ASSETS, PUBLIC

SRC, OUT = ASSETS / "boat", PUBLIC / "boat"


def trim(img, pad=4):
    ys, xs = np.nonzero(np.asarray(img)[..., 3] > 12)
    return img.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), xs.max() + pad + 1, ys.max() + pad + 1))


def cells(img, cols, rows):
    cw, ch = img.width / cols, img.height / rows
    return [img.crop((round(c * cw), round(r * ch), round((c + 1) * cw), round((r + 1) * ch)))
            for r in range(rows) for c in range(cols)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    full, empty = cells(key_magenta(Image.open(SRC / "boat.png")), 2, 1)
    for name, im in (("boat_full", full), ("boat_empty", empty)):
        im = trim(im)
        im.thumbnail((520, 520), Image.LANCZOS)
        im.save(OUT / f"{name}.png", optimize=True)
    for k, im in enumerate(cells(key_magenta(Image.open(SRC / "food.png")), 4, 2)):
        im = trim(im)
        im.thumbnail((220, 220), Image.LANCZOS)
        im.save(OUT / f"food_{k + 1}.png", optimize=True)
    print(f"wrote boat_full/empty + food_1..8 to {OUT}")


if __name__ == "__main__":
    main()
