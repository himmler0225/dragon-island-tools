"""Status-effect art -> frontend/public/status/<kind>_<n>.png (glowing, kept on black: drawn additive).

  assets/status/freeze.png  4x2: 1 ice shell, 2 ground frost, 3 shatter, 4 snowflakes,
                                 5 cold mist, 6 icicles, 7 icon, 8 apply flash
  assets/status/burn.png    4x2: 1 body flames, 2 small flames, 3 embers, 4 smoke,
                                 5 burn tick, 6 scorched ground, 7 icon, 8 ignite flash
  assets/status/curse.png   4x2: 1 skull sigil, 2 rune ring, 3 miasma, 4 chains,
                                 5 drips, 6 ground hex, 7 icon, 8 apply burst

Usage: .venv/bin/python tools/slice_status.py
"""
from PIL import Image

from lib.paths import ASSETS, PUBLIC
from slice_skills import grid, vfx

SRC, OUT = ASSETS / "status", PUBLIC / "status"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for kind in ("freeze", "burn", "curse"):
        for k, cell in enumerate(grid(Image.open(SRC / f"{kind}.png"), 4, 2), 1):
            vfx(cell).save(OUT / f"{kind}_{k}.png", optimize=True)
        print(f"{kind}: 8 effects -> {OUT}")


if __name__ == "__main__":
    main()
