"""Rồng Băng: chibi ice dragon with crystal wings (redraw 2026-10-18). Stands and walks upright on 2
plump legs, 2 small arms in front; flies with its crystal wings.

ref.png: the whole dragon (layout below follows it, in body-sheet px: ref px / 0.89).
parts/body.png: head (no neck), near crystal wing (bigger, left), far crystal wing (its torso and tail are
not used). parts/torso.png: the body with its tail in one piece (neck socket on top). parts/legs.png: near arm, near leg, far arm,
far leg (one piece each).
"""
from lib.paths import DRAGONS

P = DRAGONS / "rong_bang_xanh_bien" / "parts"

CONFIG = dict(
    size=0.85,   # a basic dragon: a bit smaller than the big ones
    name="Rồng Băng",
    body_src=P / "body.png",
    legs_src=P / "legs.png",
    far_shade=0.8, wing_far_shade=0.85,
    leg_scale=1.0, leg_pull=0, ground=1082, rigid_legs=True,
    body={
        "wing_far":  dict(src=(1317, 357), at=(867, 299)),
        "torso":     dict(src_img=P / "torso.png", img_scale=0.70, at=(531, 605)),   # body with its tail in one piece (parts/torso.png)
        "head":      dict(src=(312, 295), at=(397, 214)),    # sits over the top of the neck tube
        "wing_near": dict(src=(848, 297), at=(917, 278)),
    },
    joints={
        "torso": (870, 820),
        "head": (680, 600),
        "wing_near": (1019, 643),   # the round gems on the back
        "wing_far": (960, 600),
    },
    motion={"sleepTail": [0.1, 0.12, 0.15], "rigidLegs": True, "foreArms": True, "flyLegs": "dangle",
            "stride": 45, "stance": [0, -60]},
    legs={"hind_near": dict(pick=(552, 512), scale=0.66, x=735, fade_top=0.25), "hind_far": dict(pick=(1327, 512), scale=0.62, x=690, fade_top=0.25),
          "fore_near": dict(pick=(174, 504), scale=0.55, x=610, top=780, fade_top=0.2),   # little arms on the chest
          "fore_far": dict(pick=(925, 503), scale=0.5, x=495, top=795, fade_top=0.3)},   # its hand sticks out in front of the chest
)
