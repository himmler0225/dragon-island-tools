"""Cut a skill animation sheet: bands stacked top to bottom, each an icon (left, a framed card) and 10 animation
frames in 2 rows of 5, glowing on black. Every frame of a band is cut with the same box (the union of what is drawn
in all of them), so the animation does not jump when played.

  assets/dragons/<id>/skills/anims.png -> frontend/public/dragons/<id>/skills/
    vfx_<first + band * 10 + k>.png (k = 0..9, kept on black: the game draws them with additive blending;
      written UP x the sheet's size, sharpened)
    icon_<slot>.png per band (the card, black outside it made transparent)

Usage: .venv/bin/python tools/slice_skill_anims.py <id> <first vfx number> <slot of band 1> <slot of band 2> ...
  e.g. slice_skill_anims.py black_dragon 40 ultimate passive skill
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

from lib.paths import DRAGONS, OUT

ICON_W, FRAME_MAX = 256, 320
# frames are written UP x their size on the sheet (Lanczos, then sharpened, the faint glow lifted a little): drawn
# scaled 2-3x on the field they blurred. The game draws them at 1 / UP (combatFx ANIM_RES) so their size is unchanged.
UP = 2


def crisp(f):
    f = f.resize((f.width * UP, f.height * UP), Image.LANCZOS)
    f = f.filter(ImageFilter.UnsharpMask(radius=2.2, percent=90, threshold=2))
    a = np.asarray(f).astype(float)
    a = np.clip((a - 4) * 1.08, 0, 255)   # black stays black, the glow a touch brighter
    return Image.fromarray(a.astype(np.uint8))


def bands(img):
    """y ranges of the bands: split at the thin grey separator rows (bright, low-saturation, spanning the width)."""
    a = np.asarray(img.convert("RGB")).astype(int)
    lit = (a.max(axis=2) > 90) & (a.max(axis=2) - a.min(axis=2) < 30)
    rows = np.nonzero(lit.mean(axis=1) > 0.6)[0]
    cuts = [0]
    for r in rows:
        if r - cuts[-1] > 50:
            cuts.append(int(r))
    cuts.append(img.height)
    return list(zip(cuts[:-1], cuts[1:]))


def main(did, first, slots):
    src = Image.open(DRAGONS / did / "skills" / "anims.png").convert("RGB")
    out = OUT / did / "skills"
    W = src.width
    for b, (y0, y1) in enumerate(bands(src)):
        band = src.crop((0, y0 + 3, W, y1 - 3))
        lum = np.asarray(band.convert("L")).astype(int)
        # the icon: the bright card frame at the left; frames: the rest in a 5 x 2 grid
        # (the card's width varies by sheet: it ends at the first dark gap after its bright left rim)
        lit_col = (lum[10:-10, : W // 2] > 60).any(axis=0)   # (not the separator line's last rows)
        x0 = int(np.argmax(lit_col))
        gap = np.nonzero(~lit_col[x0:])[0]
        icon_x1 = x0 + int(gap[0]) if len(gap) else W // 7
        if icon_x1 - x0 < 40:   # the rim only (an empty card): fall back to the old guess
            cols = np.nonzero((lum[:, : W // 7] > 60).any(axis=0))[0]
            icon_x1 = int(cols.max()) + 1 if len(cols) else W // 7
        grid_x0 = icon_x1 + 8
        cw, ch = (W - grid_x0) / 5, band.height / 2
        cells = [band.crop((round(grid_x0 + c * cw), round(r * ch), round(grid_x0 + (c + 1) * cw), round((r + 1) * ch)))
                 for r in range(2) for c in range(5)]
        # the second row's glow reaches up over the split: black out the top row's last rows
        for k in range(5):
            cells[k].paste((0, 0, 0), (0, cells[k].height - 16, cells[k].width, cells[k].height))
        union = None
        for cell in cells:
            ys, xs = np.nonzero(np.asarray(cell.convert("L")) > 14)
            if len(xs):
                box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
                union = box if union is None else (min(union[0], box[0]), min(union[1], box[1]), max(union[2], box[2]), max(union[3], box[3]))
        union = (max(0, union[0] - 6), max(0, union[1] - 6), union[2] + 6, union[3] + 6)
        for k, cell in enumerate(cells):
            f = cell.crop(union)
            s = min(1, FRAME_MAX / max(f.size))
            f = crisp(f.resize((round(f.width * s), round(f.height * s)), Image.LANCZOS))
            f.save(out / f"vfx_{first + b * 10 + k}.png")
        print(f"band {b + 1}: frames vfx_{first + b * 10}..{first + b * 10 + 9}, {f.size}")
        if b < len(slots):
            ic = band.crop((0, 0, icon_x1, band.height))
            ys, xs = np.nonzero(np.asarray(ic.convert("L")) > 60)
            ic = ic.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).convert("RGBA")
            a = np.asarray(ic).copy()
            # outside the rounded card: black -> transparent (flood from the corners would be exact; the card's
            # rim is bright, so a dark pixel outside its rim's box is enough)
            dark = a[..., :3].max(axis=2) < 18
            h, w = dark.shape
            mask = np.zeros_like(dark)
            for y in range(h):
                for x0, step in ((0, 1), (w - 1, -1)):
                    x = x0
                    while 0 <= x < w and dark[y, x]:
                        mask[y, x] = True
                        x += step
            a[mask, 3] = 0
            ic = Image.fromarray(a)
            ic = ic.resize((ICON_W, round(ic.height * ICON_W / ic.width)), Image.LANCZOS)
            ic.save(out / f"icon_{slots[b]}.png")
            print(f"  icon_{slots[b]}.png {ic.size}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3:])
