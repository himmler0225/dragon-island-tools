"""Rain effect -> frontend/public/weather/.

  assets/weather/rain.png   4 x 3 grid on magenta:
                            raindrop streaks (4 lengths) / splash on grass (4 frames) / ripple on water (4 frames)

Writes rain_1..4.png (each trimmed), splash_1..4.png and ripple_1..4.png (each row one shared crop,
so the frames of an animation stay in place).
Usage: .venv/bin/python tools/slice_rain.py
"""
import numpy as np
from PIL import Image

from lib.image import key_magenta
from lib.paths import ASSETS, PUBLIC

SRC, OUT = ASSETS / "weather", PUBLIC / "weather"


def cells(img, cols, rows):
    cw, ch = img.width / cols, img.height / rows
    return [img.crop((round(c * cw), round(r * ch), round((c + 1) * cw), round((r + 1) * ch)))
            for r in range(rows) for c in range(cols)]


def bbox(*imgs, pad=3):
    a = np.max([np.asarray(im)[..., 3] for im in imgs], axis=0) > 12
    ys, xs = np.nonzero(a)
    return (max(0, xs.min() - pad), max(0, ys.min() - pad), xs.max() + pad + 1, ys.max() + pad + 1)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    grid = cells(key_magenta(Image.open(SRC / "rain.png")), 4, 3)
    for k, im in enumerate(grid[0:4]):
        im.crop(bbox(im)).save(OUT / f"rain_{k + 1}.png", optimize=True)
    for name, row in (("splash", grid[4:8]), ("ripple", grid[8:12])):
        box = bbox(*row)
        for k, im in enumerate(row):
            im.crop(box).save(OUT / f"{name}_{k + 1}.png", optimize=True)
    print(f"wrote rain_1..4, splash_1..4, ripple_1..4 to {OUT}")


if __name__ == "__main__":
    main()
