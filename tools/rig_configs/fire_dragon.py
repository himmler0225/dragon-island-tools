"""Rồng Lửa: chibi red fire dragon (redraw 2026-10-18). Walks on 4 stubby legs, flies with its small
bat wings, breathes fire.

ref.png: the whole dragon (the layout below follows it, in body-sheet px: ref px / 1.067).
parts/body.png: head with neck, torso (shoulder + hip bumps, neck and tail sockets), far wing (smaller,
left), near wing (right), tail base, tail tip. parts/legs.png: 4 whole chibi legs in one row
(fore near, hind near, fore far, hind far), one piece each, swinging from the hip.
Older sheets: parts/body_old*.png, body_v2/v3.png, legs_old2.png.
"""
from lib.paths import DRAGONS

P = DRAGONS / "rong_lua_do" / "parts"

CONFIG = dict(
    size=0.85,   # a bit smaller than the bigger dragons
    name="Rồng Lửa",
    body_src=P / "body.png",
    legs_src=P / "legs.png",
    far_shade=0.8, wing_far_shade=0.85,
    leg_scale=1.0, leg_pull=0, ground=902,
    rigid_legs=True,
    body={
        "wing_far":  dict(src=(817, 205), at=(675, 266), rot=-10),
        "tail_base": dict(src_img=P / "tail.png", img_scale=0.5, at=(970, 502)),   # one short chibi tail (parts/tail.png)
        "torso":     dict(src=(811, 570), at=(490, 368), drop=[(1072, 440, 1110, 720)]),   # its tail-socket face: the tail fills it
        "head":      dict(src_img=P / "head.png", img_scale=0.5, at=(255, 66)),   # head only (parts/head.png), over the end of the torso's neck tube
        "wing_near": dict(src=(1232, 239), at=(789, 268), rot=-10),
    },
    joints={
        "torso": (760, 560),
        "head": (560, 430),        # where the head sits on the neck
        "wing_near": (811, 575),   # root balls on the back
        "wing_far": (694, 549),
        "tail_base": (985, 605),  # in the torso's tail socket
    },
    motion={"sleepTail": [0.1, 0.12, 0.15], "tailWave": [0.6, 1, 1, 1], "flyLegs": "dangle", "rigidLegs": True,
            "stride": 45, "stance": [0, 0]},   # small chibi steps
    legs={"fore_near": dict(pick=(206, 542), scale=0.74, x=600), "fore_far": dict(pick=(940, 546), scale=0.68, x=480),
          "hind_near": dict(pick=(572, 523), scale=0.74, x=840), "hind_far": dict(pick=(1313, 524), scale=0.68, x=790)},
)
