"""Rồng Rừng: slim green forest dragon with an autumn-leaf crest (redraw 2026-10-18). Stands and walks
upright on 2 bird-like legs, 2 small arms held in front; no wings (never flies).

ref.png: the whole dragon (layout below follows it, in body-sheet px: ref px / 0.91).
parts/torso.png: the upright body with its tail in one piece (neck socket on top). parts/head.png: head
with leaf crest, no neck. parts/body.png: the first parts sheet (only loaded as the body sheet). parts/legs.png: near leg, far leg, near arm, far arm
(one piece each).
"""
from lib.paths import DRAGONS

P = DRAGONS / "rong_cay_xanh_la" / "parts"

CONFIG = dict(
    size=0.85,   # a basic dragon: a bit smaller than the big ones
    name="Rồng Rừng",
    body_src=P / "body.png",
    legs_src=P / "legs.png",
    far_shade=0.8, wing_far_shade=0.8,
    leg_scale=1.0, leg_pull=0, ground=1092, rigid_legs=True,
    body={
        "torso":     dict(src_img=P / "torso.png", img_scale=0.50, at=(640, 524)),   # body with its tail in one piece (parts/torso.png)
        "head":      dict(src_img=P / "head.png", img_scale=0.6, at=(440, 140)),   # head only (parts/head.png), over the end of the neck
    },
    joints={
        "torso": (860, 720),
        "head": (663, 550),
    },
    # stands upright: the arms ("fore" limbs) hang from the chest and sway; only the legs walk
    motion={"sleepTail": [0.1, 0.12, 0.15], "noFly": True, "rigidLegs": True, "foreArms": True,
            "stride": 45, "stance": [0, -60]},
    legs={"hind_near": dict(pick=(263, 551), scale=0.6, x=740, fade_top=0.22), "hind_far": dict(pick=(692, 543), scale=0.56, x=645, fade_top=0.22),
          "fore_near": dict(pick=(1115, 634), scale=0.47, x=644, top=721, fade_top=0.25),
          "fore_far": dict(pick=(1394, 642), scale=0.43, x=605, top=715, fade_top=0.25)},
)
