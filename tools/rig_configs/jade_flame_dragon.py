"""Rồng Lửa Mắt Xanh (2026-10-28): a chubby orange baby dragon with a green eye that breathes green fire.
Four legs and two wings; it fights from the air in battle."""
from lib.paths import DRAGONS

# parts/body.png: head with the upper jaw (no neck), near wing, far wing, the old body (neck to tail flame,
# with a hip ball) and the lower jaw. ref.png: the whole dragon; layout px = ref.png px.
BODY = DRAGONS / "jade_flame_dragon" / "parts" / "body.png"
# parts/torso.png (redraw 2026-10-30): the body from the neck to the flame tail tip in one piece, no hip
# ball, no leg stumps. Carved into torso + a 3-piece tail: each piece starts under the one drawn over it
# (torso > tail_base > tail_mid > tail_tip) and that one's cut end fades out over it. Placed at TORSO_K with
# its top-left at TORSO_AT (where the old body piece was).
TORSO = DRAGONS / "jade_flame_dragon" / "parts" / "torso.png"
TORSO_AT, TORSO_K = (480, 453), 0.69
carve = lambda keep, fade=None, **kw: dict(sheet=TORSO, src=(780, 550), at=TORSO_AT, img_scale=TORSO_K, keep=[keep],
                                           **({"fade": fade} if fade else {}), **kw)

CONFIG = dict(
    name="Rồng Lửa Mắt Xanh",
    size=0.85,   # a baby dragon: a little smaller than the big ones
    body_src=BODY,
    # parts/legs.png (redraw 2026-10-30, in the shape of Rồng Lửa's legs): 4 whole chibi legs in one row
    # (fore near, hind near, fore far, hind far), one piece each, swinging from the hip. The hind legs'
    # inner S crease lines are painted out (the upload as drawn: legs_raw.png).
    # Older sheets: legs_old.png (thigh / shin / paw) and legs_whole_old.png (compose_legs.py of it).
    legs_src=DRAGONS / "jade_flame_dragon" / "parts" / "legs.png",
    rigid_legs=True,
    far_shade=0.82, wing_far_shade=0.82,
    leg_scale=1.0, leg_pull=0, ground=955,
    body={
        # src: a point inside the piece on body.png; at: its top-left on ref.png
        "wing_far":  dict(src_img=BODY, src=(1307, 285), img_scale=1.0, at=(700, 240)),
        "tail_tip":  carve((1240, 150, 1520, 900)),
        "tail_mid":  carve((1100, 150, 1270, 900), (1240, 1270)),
        "tail_base": carve((960, 150, 1130, 900), (1100, 1130)),
        "torso":     carve((100, 150, 1000, 900), (970, 1000)),
        "wing_near": dict(src_img=BODY, src=(906, 266), img_scale=1.0, at=(770, 262)),
        "jaw":       dict(src_img=BODY, src=(226, 683), img_scale=0.85, at=(315, 410)),
        "head":      dict(src_img=BODY, src=(349, 287), img_scale=1.04, at=(238, 20)),
    },
    joints={
        "torso": (850, 720),
        "tail_base": (1070, 769),   # the underside of the tail root: turning about it never lifts the underside off the body
        "tail_mid": (1167, 693),
        "tail_tip": (1263, 603),
        "head": (560, 480),        # the back of the head, on the end of the neck
        "jaw": (540, 455),         # the hinge at the back of the jaw, under the cheek
        "wing_near": (800, 575),   # the wing roots on the shoulders
        "wing_far": (725, 555),
    },
    parents={"jaw": "head"},
    motion={"wingSpread": [0.22, -0.05], "flyLegs": "dangle", "sleepTail": [0.1, 0.15, 0.2],
            "stance": [0, 0],   # the far legs are already placed a step apart (as on ref.png)
            "rigidLegs": True, "stride": 60},   # small chibi steps
    # as on ref.png: the far fore leg peeks out in front of the near one, the far hind one behind it
    # (mostly hidden: in front of the near hind leg it reads as two legs on one side)
    legs={"fore_near": dict(pick=(223, 544), scale=0.7, x=640), "hind_near": dict(pick=(598, 518), scale=0.7, x=870),
          "fore_far": dict(pick=(973, 558), scale=0.7, x=520), "hind_far": dict(pick=(1336, 535), scale=0.7, x=765)},
    # wings on the ground (wing_rest: in flight they beat from where they are drawn), set as one V on every winged species (chibi: the far wing root tucked just behind the near one on the back, leaning a little forward)
    wing_rest={"wing_far": (60, 30, -8, 0.9), "wing_near": (0, 0, 0, 1.0)},
)
