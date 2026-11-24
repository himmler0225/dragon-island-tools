"""Rồng Lửa: chibi red fire dragon (redraw 2026-10-18). Walks on 4 stubby legs, flies with its small
bat wings, breathes fire.

ref.png: the whole dragon (the layout below follows it, in body-sheet px: ref px / 1.067).
parts/body.png: head with neck, the old torso (with leg stumps and a tail socket), far wing (smaller,
left), near wing (right), tail base, tail tip; only the wings are used. parts/torso.png (redraw 2026-10-30):
the body from the neck to the tail spike in one piece, no leg stumps, no socket. parts/legs.png: 4 whole
chibi legs in one row (fore near, hind near, fore far, hind far), one piece each, swinging from the hip.
Older sheets: parts/body_old*.png, body_v2/v3.png, legs_old2.png, tail.png.
"""
from lib.paths import DRAGONS

P = DRAGONS / "fire_dragon" / "parts"
# torso.png carved into torso + a 2-piece tail: each piece starts under the one drawn over it (torso >
# tail_base > tail_mid) and that one's cut end fades out over it. Placed at TORSO_K, top-left at TORSO_AT.
TORSO_AT, TORSO_K = (490, 370), 0.6
carve = lambda keep, fade=None: dict(sheet=P / "torso.png", src=(700, 500), at=TORSO_AT, img_scale=TORSO_K, keep=[keep],
                                     **({"fade": fade} if fade else {}))

CONFIG = dict(
    size=0.7,    # clearly smaller than the bigger dragons (baby dragons)
    name="Rồng Lửa",
    body_src=P / "body.png",
    legs_src=P / "legs.png",
    far_shade=0.8, wing_far_shade=0.92,
    leg_scale=1.0, leg_pull=0, ground=902,
    rigid_legs=True,
    body={
        "wing_far":  dict(src=(817, 205), at=(675, 266), rot=-10),
        "tail_mid":  carve((1170, 150, 1500, 880)),
        "tail_base": carve((960, 150, 1230, 880), (1200, 1230)),
        "torso":     carve((60, 150, 1030, 880), (1000, 1030)),
        "head":      dict(src_img=P / "head.png", img_scale=0.5, at=(255, 66)),   # head only (parts/head.png), over the end of the torso's neck tube
        "wing_near": dict(src=(1232, 239), at=(789, 268), rot=-10),
    },
    joints={
        "torso": (760, 560),
        "head": (560, 430),        # where the head sits on the neck
        "wing_near": (811, 575),   # root balls on the back
        "wing_far": (694, 549),
        "tail_base": (1029, 680),   # the underside of the tail root: turning about it never lifts the underside off the body
        "tail_mid": (1158, 569),
    },
    motion={"sleepTail": [0.1, 0.12, 0.15], "tailWave": [0.6, 1, 1, 1], "flyLegs": "dangle", "rigidLegs": True,
            "stride": 45, "stance": [0, 0],   # small chibi steps
            "gait": "trot", "duty": 0.5,   # diagonal pairs taking turns: every step as long, evenly spaced
            "flyPitch": 0.25},   # flies in battle with its head held up a little (pose.ts dips flyers 0.1)
    legs={"fore_near": dict(pick=(206, 542), scale=0.74, x=600), "fore_far": dict(pick=(940, 546), scale=0.68, x=480),
          "hind_near": dict(pick=(572, 523), scale=0.74, x=840), "hind_far": dict(pick=(1313, 524), scale=0.68, x=733)},
    # wings on the ground (wing_rest: in flight they beat from where they are drawn), set as one V on every winged species (chibi: the far wing root tucked just behind the near one on the back, leaning a little forward)
    wing_rest={"wing_far": (80, 30, -8, 0.9), "wing_near": (0, 0, 0, 1.0)},
)
