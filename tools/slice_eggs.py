"""Dragon eggs (10 levels) and the incubator nest -> frontend/public/eggs/.

  assets/eggs/eggs.png   5 x 2 grid of eggs on magenta, level 1..10 left-to-right, top row first
  assets/eggs/nest.png   the nest the egg sits in on the first island, on magenta

Writes frontend/public/eggs/egg_<1..10>.png (cropped, EGG_HEIGHT px tall incl. glow) and nest.png.
Usage: .venv/bin/python tools/slice_eggs.py
"""
import numpy as np
from PIL import Image

from lib.image import key_distance, key_magenta
from lib.paths import ASSETS, PUBLIC

SRC = ASSETS / "eggs"
OUT = PUBLIC / "eggs"
COLS, ROWS = 5, 2
EGG_HEIGHT = 320   # px; shown at ~120 px in the breeding panel, ~60 px on the island
NEST_WIDTH = 480


def crop(img, pad=6):
    a = np.asarray(img)[..., 3]
    ys, xs = np.nonzero(a > 12)
    return img.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), xs.max() + pad + 1, ys.max() + pad + 1))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # colour-distance keying: the amethyst egg and the violet glows would be eaten by key_magenta
    sheet = key_distance(Image.open(SRC / "eggs.png"), near=60, far=150)
    cw, ch = sheet.width / COLS, sheet.height / ROWS
    for k in range(COLS * ROWS):
        c, r = k % COLS, k // COLS
        cell = crop(sheet.crop((round(c * cw), round(r * ch), round((c + 1) * cw), round((r + 1) * ch))))
        cell = cell.resize((round(cell.width * EGG_HEIGHT / cell.height), EGG_HEIGHT), Image.LANCZOS)
        cell.save(OUT / f"egg_{k + 1}.png", optimize=True)
    nest = crop(key_magenta(Image.open(SRC / "nest.png")))
    nest = nest.resize((NEST_WIDTH, round(nest.height * NEST_WIDTH / nest.width)), Image.LANCZOS)
    nest.save(OUT / "nest.png", optimize=True)
    print(f"wrote {COLS * ROWS} eggs + nest.png to {OUT}")


if __name__ == "__main__":
    main()
