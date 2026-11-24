"""Nguyệt Long (2026-10-30): a chibi ice-blue moon dragon with a crescent-moon horn, a green toothy grin
and a moon orb. Four legs and two wings; it fights from the air in battle.

ref.png: the whole dragon; layout px = ref.png px. parts/body.png (redraw 2026-10-31): an open-mouthed head
(unused), far wing (tall, left), near wing (wide, right), moon orb (cut out as parts/moon.png), the body from the neck to
the tail tip in one piece (no legs) and an old lower jaw (unused). parts/head.png: the whole head with its
green lower jaw closed, split by tools/split_head_jaw.py moon_dragon 35 85 into head_upper.png and
head_jaw.png (the jaw over a dark mouth): cut from one drawing, they fit exactly. parts/legs.png: 4 whole
chibi legs in one row (fore near, hind near, fore far, hind far), one piece each, swinging from the hip.
"""
from lib.paths import DRAGONS

P = DRAGONS / "moon_dragon" / "parts"
# the body (neck to tail tip, top-left (474, 593) on body.png) carved into torso + a 3-piece tail: each
# piece starts under the one drawn over it (torso > tail_base > tail_mid > tail_tip) and that one's cut
# end fades out over it. Placed at BODY_K with its top-left at BODY_AT.
BODY_AT, BODY_K = (395, 560), 0.9
carve = lambda keep, fade=None, **kw: dict(src=(849, 763), at=BODY_AT, img_scale=BODY_K, keep=[keep],
                                          **({"fade": fade} if fade else {}), **kw)
CONFIG = dict(
    name="Nguyệt Long",
    size=0.8,    # a chibi dragon
    key="distance",   # lilac shading and purple spots: key_magenta would eat them
    body_src=P / "body.png",
    legs_src=P / "legs.png",
    rigid_legs=True,
    far_shade=0.82, wing_far_shade=0.85,
    leg_scale=1.0, leg_pull=0, ground=950,
    body={
        # src: a point inside the piece on body.png; at: its top-left on ref.png
        "wing_far":  dict(src=(669, 362), at=(575, 140), img_scale=0.9, rot=-10),   # its root down behind the back
        "tail_tip":  carve((1280, 550, 1480, 960)),
        "tail_mid":  carve((1140, 550, 1340, 960), (1310, 1340)),
        "tail_base": carve((990, 550, 1200, 960), (1170, 1200), rot=-10),   # the tail raised: it fills in under the near wing as on ref.png
        "torso":     carve((450, 550, 1050, 960), (1020, 1050)),
        "wing_near": dict(src=(1011, 391), at=(655, 200), img_scale=1.28, rot=10),   # lower than on ref.png: its bottom edge rests on the back (the redrawn body is lower)
        "jaw":       dict(src_img=P / "head_jaw.png", at=(232, 490), img_scale=0.64),
        "head":      dict(src_img=P / "head_upper.png", at=(187, 178), img_scale=0.64),
        # the moon floating over the tail tip, as on ref.png (parts/moon.png: cut off body.png with its pink
        # halo by tools/cut_glow.py ... body.png 1170 275 1500 600 moon.png)
        "orb":       dict(src_img=P / "moon.png", rgba=True, whole=True, at=(1075, 287), img_scale=0.96),
    },
    joints={
        "torso": (760, 720),
        "tail_base": (877, 785),   # the underside of the tail root: turning about it never lifts the underside off the body
        "tail_mid": (1012, 718),
        "tail_tip": (1138, 634),
        "head": (540, 580),        # the back of the head, on the end of the neck
        "orb": (1215, 425),        # the moon's centre: it bobs about it
        "jaw": (483, 559),         # the hinge: the back end of the jaw, under the cheek
        "wing_near": (690, 680),   # the wing roots on the shoulders
        "wing_far": (610, 590),
    },
    parents={"jaw": "head"},
    motion={"wingSpread": [0.15, -0.05], "flyLegs": "dangle", "sleepTail": [0.1, 0.15, 0.2],
            "stance": [0, 0],   # the far legs are already placed a step apart (as on ref.png)
            "rigidLegs": True, "stride": 60},   # small chibi steps
    # as on ref.png: the far fore leg peeks out in front of the near one, the far hind one behind it
    legs={"fore_near": dict(pick=(222, 544), scale=0.6, x=484), "hind_near": dict(pick=(594, 518), scale=0.55, x=686),
          "fore_far": dict(pick=(965, 567), scale=0.6, x=420), "hind_far": dict(pick=(1326, 550), scale=0.55, x=591)},
    # wings on the ground (wing_rest: in flight they beat from where they are drawn), set as one V on every winged species (chibi: the far wing root tucked just behind the near one on the back, leaning a little forward)
    wing_rest={"wing_far": (70, 70, -6, 0.9), "wing_near": (0, 0, 0, 1.0)},
)
