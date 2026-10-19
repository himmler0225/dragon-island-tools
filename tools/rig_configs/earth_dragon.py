"""Rồng Đất: chibi wingless earth dragon, like a little armoured dinosaur (redraw 2026-10-18). Walks on
4 stubby legs, never flies.

ref.png: the whole dragon (the layout below follows it, in body-sheet px: ref px / 1.1).
parts/body.png: head with neck stub, torso (shoulder + hip bumps, neck and tail sockets), tail base,
tail tip. parts/legs.png: 4 whole chibi legs in one row (fore near, hind near, fore far, hind far).
Older sheets: parts/body_old2.png, legs_old2.png.
"""
from lib.paths import DRAGONS

P = DRAGONS / "rong_dat_nau" / "parts"

CONFIG = dict(
    size=0.85,   # a bit smaller than the bigger dragons
    name="Rồng Đất",
    body_src=P / "body.png",
    legs_src=P / "legs.png",
    far_shade=0.82, wing_far_shade=0.8,
    leg_scale=1.0, leg_pull=0, ground=844, rigid_legs=True,
    body={
        "tail_base": dict(src_img=P / "tail.png", img_scale=0.55, at=(1001, 442)),   # one short chibi tail (parts/tail.png)
        "torso":     dict(src=(834, 487), at=(455, 199), drop=[(1128, 520, 1160, 720)]),   # tail-socket face
        "head":      dict(src_img=P / "head.png", img_scale=0.62, at=(83, 70), feather=dict(x=480, y=330, px=20)),   # big head only (parts/head.png); its back outline melts into the neck
    },
    joints={
        "torso": (750, 450),
        "head": (480, 470),        # where the head sits on the neck
        "tail_base": (1035, 590),  # in the torso's tail socket
    },
    motion={"sleepTail": [0.1, 0.12, 0.15], "noFly": True, "rigidLegs": True, "stride": 45, "stance": [0, 0]},
    legs={"fore_near": dict(pick=(264, 409), scale=0.68, x=490), "fore_far": dict(pick=(1314, 419), scale=0.62, x=360),
          "hind_near": dict(pick=(803, 382), scale=0.7, x=770), "hind_far": dict(pick=(1895, 398), scale=0.64, x=720)},
)
