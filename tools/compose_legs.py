"""Stack each column of a 3-piece legs sheet (thigh / shin / paw) into one whole leg, for build_rig.

The pieces are drawn with an outline at both ends, so a rig built straight from them shows a rim at
every knee and ankle. Here the thigh goes over the shin's round knee knob and the shin over the paw,
the outlined joint ends are trimmed and the overlapping ends melt out; build_rig then cuts the whole
leg again at its narrowest rows, through flesh.

    python compose_legs.py <dragon_id> [--no-thigh-ball COL ...]

--no-thigh-ball: columns whose round thigh top is dropped (the body sheet already draws that haunch;
fade the cut top in the rig config with fade_top).
Writes assets/dragons/<id>/parts/legs_whole.png.
"""
import sys

import numpy as np
from PIL import Image

from build_rig import components, cut, key_magenta
from lib.paths import DRAGONS


def trim(img, oy, h, top=0, bottom=0, fade=0):
    """Keep source rows [top, h - bottom) of a piece cut with offset oy; the last `fade` kept rows
    melt out downward, so the piece under them shows without a seam."""
    a = np.asarray(img).astype(np.float32)
    r = np.arange(a.shape[0]) - oy
    end = h - bottom
    a[..., 3] *= (np.clip((end - r) / fade, 0, 1) if fade else (r < end))[:, None]
    a[..., 3] *= (r >= top)[:, None]
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def edges(img, row):
    """Leftmost and rightmost solid x on image row `row`."""
    xs = np.nonzero(np.asarray(img)[row, :, 3] > 128)[0]
    return int(xs.min()), int(xs.max())


def compose(dragon, no_ball=()):
    src = key_magenta(Image.open(DRAGONS / dragon / "parts" / "legs.png"))
    cw = src.width / 4
    out = Image.new("RGBA", src.size)
    for c in range(4):
        col = sorted([p for p in components(src) if int((p[0][0] + p[0][2] / 2) // cw) == c], key=lambda p: p[0][1])
        (tb, _), (sb, _), (pb, _) = col
        (thigh, (tx, ty)), (shin, (sx, sy)), (paw, (px, py)) = (cut(src, b, m) for b, m in col)
        knob = int(sb[3] * 0.42)   # the shin's round knee knob: hidden under the thigh
        ball = int(tb[3] * 0.5) if c in no_ball else 0
        thigh = trim(thigh, ty, tb[3], top=ball, bottom=16, fade=40)   # (fade its new top with fade_top)
        shin = trim(shin, sy, sb[3], top=knob, bottom=16, fade=30)
        paw = trim(paw, py, pb[3], top=16)
        top = 60
        s_top = top + tb[3] - 16 - 60 - knob   # shin's kept part starts 60 px up under the thigh
        p_top = s_top + sb[3] - 16 - 40 - 16   # paw's kept part starts 40 px up under the shin
        # the paw sits straight under the shin: stretched sideways to the width of the shin's ankle
        # and lined up with it on both sides, so the ankle has no step (the fore shins flare wider
        # than their paws)
        (sl, sr), (pl, pr) = edges(shin, sy + sb[3] - 16 - 31), edges(paw, py + 16)
        k = (sr - sl) / (pr - pl)
        paw = paw.resize((round(paw.width * k), paw.height), Image.LANCZOS)
        out.alpha_composite(paw, (round(sb[0] - sx + sl - pl * k), p_top - py))
        for img, b, (ox, oy), y in ((shin, sb, (sx, sy), s_top), (thigh, tb, (tx, ty), top)):
            out.alpha_composite(img, (b[0] - ox, y - oy))
    bg = Image.new("RGBA", out.size, (255, 0, 255, 255))
    bg.alpha_composite(out)
    bg.convert("RGB").save(DRAGONS / dragon / "parts" / "legs_whole.png")


if __name__ == "__main__":
    args = sys.argv[1:]
    cols = [int(a) for a in args[args.index("--no-thigh-ball") + 1:]] if "--no-thigh-ball" in args else []
    compose(args[0], cols)
