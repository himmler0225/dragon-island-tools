"""Cut each dragon's skill art into single files for the game.

  assets/dragons/<id>/skills/icons.png  2x2 grid: passive, basic, skill, ultimate (framed cards on black)
  assets/dragons/<id>/skills/vfx.png    4x2 grid of glowing effects on pure black

Writes frontend/public/dragons/<id>/skills/:
  icon_passive.png ... icon_ultimate.png   black outside the card frame made transparent
  vfx_1.png ... vfx_8.png                  kept on black: the game draws them with ADD blending,
                                           where black is transparent and glow adds light
  jaw_upper.png, jaw_lower.png             optional (skills/jaws.png): giant jaws for bite attacks

Usage: .venv/bin/python tools/slice_skills.py [dragon_id ...]   (default: every dragon with skills/)
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DRAGONS = ROOT / "assets" / "dragons"
OUT = ROOT / "frontend" / "public" / "dragons"
ICON_ORDER = ["passive", "basic", "skill", "ultimate"]
ICON_WIDTH = 256        # exported icon width (they are shown at ~64-96 px)
VFX_MAX = 384           # longest side of an exported effect


def grid(img, cols, rows):
    w, h = img.width / cols, img.height / rows
    return [img.crop((round(c * w), round(r * h), round((c + 1) * w), round((r + 1) * h)))
            for r in range(rows) for c in range(cols)]


def icon_cells(img, search=80, tol=26):
    """2x2 icon sheet -> 4 cells, cut along the most background-like row/column near the middle
    (cards are often drawn almost touching, so an exact half-split catches neighbour edges)."""
    rgb = np.asarray(img.convert("RGB")).astype(int)
    bg = np.median(np.array([rgb[2, 2], rgb[2, -3], rgb[-3, 2], rgb[-3, -3]]), axis=0)
    isbg = np.abs(rgb - bg).max(axis=2) <= tol
    h, w = isbg.shape
    def best(profile, mid):
        lo, hi = mid - search, mid + search
        return lo + int(np.argmax(profile[lo:hi]))
    cy, cx = best(isbg.mean(axis=1), h // 2), best(isbg.mean(axis=0), w // 2)
    boxes = [(0, 0, cx, cy), (cx, 0, w, cy), (0, cy, cx, h), (cx, cy, w, h)]
    return [img.crop(b) for b in boxes]


def icon(cell, tol=26):
    """Card on a plain dark background: flood-fill the background (colour taken from the corners)
    from the borders, make it transparent, and keep only the card (drops slivers of neighbours)."""
    rgb = np.asarray(cell.convert("RGB"))
    h, w = rgb.shape[:2]
    corners = np.array([rgb[2, 2], rgb[2, -3], rgb[-3, 2], rgb[-3, -3]]).astype(int)
    bg = np.median(corners, axis=0)
    near = (np.abs(rgb.astype(int) - bg).max(axis=2) <= tol).astype(np.uint8)
    outside = np.zeros((h + 2, w + 2), np.uint8)
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if near[y, x] and not outside[y + 1, x + 1]:
            cv2.floodFill(near.copy(), outside, (x, y), 1, flags=4 | (1 << 8))
    solid = (outside[1:-1, 1:-1] == 0).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(solid)
    if n > 2:   # keep the biggest region: the card itself
        solid = (labels == 1 + int(np.argmax(stats[1:, 4]))).astype(np.uint8)
    alpha = cv2.GaussianBlur(solid * 255, (0, 0), 0.8)               # soft edge on the rounded corners
    out = Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), "RGBA")
    out = out.crop(out.getchannel("A").getbbox())
    return out.resize((ICON_WIDTH, round(out.height * ICON_WIDTH / out.width)), Image.LANCZOS)


ICON_FROM_VFX = {"ki_lan": (7, 4, 1, 3)}   # effect number shown on each placeholder icon
FRAME = {"passive": (190, 196, 206), "basic": (176, 112, 60), "skill": (90, 140, 200), "ultimate": (232, 184, 70)}


def placeholder_icon(effect, slot, size=ICON_WIDTH):
    """Dark rounded card with a coloured frame and the effect glowing in the middle."""
    from PIL import ImageDraw
    card = Image.new("RGBA", (size, size))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([2, 2, size - 3, size - 3], radius=size // 7, fill=(18, 24, 38, 255), outline=FRAME[slot] + (255,), width=size // 22)
    fx = effect.convert("RGB")
    fx.thumbnail((int(size * 0.74), int(size * 0.74)), Image.LANCZOS)
    glow = Image.new("RGB", card.size)
    glow.paste(fx, ((size - fx.width) // 2, (size - fx.height) // 2))
    base = np.asarray(card).astype(np.int32)
    inside = base[..., 3] > 0
    base[..., :3] = np.where(inside[..., None], np.minimum(255, base[..., :3] + np.asarray(glow)), base[..., :3])
    return Image.fromarray(base.astype(np.uint8), "RGBA")


def vfx(cell, pad=6):
    rgb = np.asarray(cell.convert("RGB")).copy()
    # drop slivers of a neighbouring effect that spill over the cell edge: always keep the biggest
    # glow region; drop smaller ones that touch the left/right border
    lit = (rgb.max(axis=2) > 10).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(cv2.dilate(lit, np.ones((15, 15), np.uint8)))
    w = rgb.shape[1]
    regions = [i for i in range(1, n) if stats[i][4] > 50]
    big = max(regions, key=lambda i: stats[i][4])
    keep = [i for i in regions if i == big or (stats[i][0] > 0 and stats[i][0] + stats[i][2] < w)]
    rgb[~np.isin(labels, keep)] = 0
    ys, xs = np.nonzero(rgb.max(axis=2) > 10)
    box = (max(0, xs.min() - pad), max(0, ys.min() - pad), min(cell.width, xs.max() + pad), min(cell.height, ys.max() + pad))
    out = Image.fromarray(rgb).crop(box)
    k = min(1.0, VFX_MAX / max(out.size))
    return out.resize((round(out.width * k), round(out.height * k)), Image.LANCZOS)


def main(ids):
    for dragon_id in ids:
        src, dst = DRAGONS / dragon_id / "skills", OUT / dragon_id / "skills"
        dst.mkdir(parents=True, exist_ok=True)
        effects = [vfx(cell) for cell in grid(Image.open(src / "vfx.png"), 4, 2)]
        for k, fx in enumerate(effects, 1):
            fx.save(dst / f"vfx_{k}.png", optimize=True)
        if (src / "icons.png").exists():
            for name, cell in zip(ICON_ORDER, icon_cells(Image.open(src / "icons.png"))):
                icon(cell).save(dst / f"icon_{name}.png", optimize=True)
        else:   # no icon art yet: stand-in icons from the effects (which effect per slot: ICON_FROM_VFX)
            for name, k in zip(ICON_ORDER, ICON_FROM_VFX.get(dragon_id, (7, 4, 1, 1))):
                placeholder_icon(effects[k - 1], name).save(dst / f"icon_{name}.png", optimize=True)
        jaws = src / "jaws.png"   # optional: upper jaw (left) + lower jaw (right) on black, for bite attacks
        if jaws.exists():
            for name, cell in zip(("jaw_upper", "jaw_lower"), grid(Image.open(jaws), 2, 1)):
                vfx(cell).save(dst / f"{name}.png", optimize=True)
        print(f"{dragon_id}: 4 icons + 8 vfx{' + jaws' if jaws.exists() else ''} -> {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(p.parent.parent.name for p in DRAGONS.glob("*/skills/vfx.png")))
