"""Hỏa Linh (boss, 2026-10-28): a floating chibi fire spirit. Flame hair that streams behind it (the tail
chain, hung off the head), two clawed arms that thrust out to blast fire, two flame feet that dangle.

Every piece is carved straight out of ref.png (layout px = ref.png px), so the boss looks exactly like
the reference: the redrawn parts sheets (parts/*.png) were drawn in another style (long sleeved arms,
hollow leg tubes). The thighs stay on the torso; only the flame feet below the gold rings swing."""
import cv2
import numpy as np
from lib.paths import DRAGONS

REF = DRAGONS / "fire_spirit_boss" / "ref.png"
AT = (565, 183)   # top-left of the whole drawing in ref.png (carved pieces are placed from it)
ALL = (830, 520)  # any point on the drawing: it is one island

# limbs (ref px): the arms hang beside the torso, the flame feet hang under the gold knee rings
ARM_NEAR = [(660, 524), (612, 538), (598, 578), (560, 606), (552, 702), (626, 702), (626, 600), (648, 584), (660, 560)]
ARM_FAR = [(762, 524), (792, 518), (802, 560), (832, 588), (872, 608), (874, 702), (790, 702), (784, 640), (774, 600), (766, 570)]
FOOT_NEAR = [(638, 696), (712, 696), (714, 752), (741, 756), (741, 880), (638, 880)]
FOOT_FAR = [(720, 712), (802, 712), (852, 728), (852, 886), (741, 886), (741, 756), (716, 752)]


def shrink(poly, px=4):
    """The polygon pulled in by px: the torso keeps a thin strip of each limb under/over the limb's
    cut edge, so the two anti-aliased edges never leave a see-through seam."""
    m = np.zeros((1024, 1536), np.uint8)
    cv2.fillPoly(m, [np.array(poly, np.int32)], 1)
    m = cv2.erode(m, np.ones((2 * px + 1, 2 * px + 1), np.uint8))
    (c,), _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [tuple(int(v) for v in pt[0]) for pt in c]


LIMBS = [shrink(p) for p in (ARM_NEAR, ARM_FAR, FOOT_NEAR, FOOT_FAR)]

# hair: head keeps its left part, each later piece starts under the one before (drawn on top of it)
# and that one's right end fades out over it, so the cut never shows when the hair ripples
piece = lambda keep, fade=None, **kw: dict(src=ALL, at=AT, keep=[keep], **({"fade": fade} if fade else {}), **kw)

CONFIG = dict(
    name="Hỏa Linh",
    size=1.4,   # a boss: bigger than the dragons
    key="tight",   # pink-purple hair: magenta / distance keying would eat it
    body_src=REF, legs_src=REF, leg_ref=REF,
    far_shade=0.85, wing_far_shade=0.85,
    rigid_legs=True,   # each arm / flame foot swings whole from its shoulder / knee ring
    leg_scale=1.0, leg_pull=0, ground=880,
    body={
        "tail_tip":  piece((990, 170, 1150, 486)),
        "tail_mid":  piece((880, 170, 1040, 486), (1010, 1040)),
        "tail_base": piece((770, 170, 935, 486), (905, 935)),
        "head":      piece((540, 170, 825, 482), (795, 825)),
        "torso":     piece((540, 482, 900, 900), drop_poly=LIMBS),
    },
    joints={
        "torso": (705, 600),
        "head": (700, 482),        # the neck ring
        "tail_base": (790, 330),   # the hair streams back from the head
        "tail_mid": (900, 330),
        "tail_tip": (1010, 310),
    },
    parents={"tail_base": "head"},
    # float: never walks, the flame feet dangle; foreArms: the arms hang from the shoulders and swing;
    # tailWave: the hair streams and ripples harder than a tail
    motion={"float": True, "foreArms": True, "armPose": [[0, 0], [0, 0]], "sleepTail": [0, 0, 0], "stance": [0, 0],
            "tailWave": [1.0, 1.2, 1.4, 1.4], "flyHang": [0.08, 0.06]},
    legs={
        "fore_near": dict(poly=ARM_NEAR, top=524),
        "fore_far":  dict(poly=ARM_FAR, top=521),
        "hind_near": dict(poly=FOOT_NEAR, top=696),
        "hind_far":  dict(poly=FOOT_FAR, top=712),
    },
)
