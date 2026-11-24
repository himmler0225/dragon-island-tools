"""Rồng Cây (2026-11-01): a slim leaf-green dragon on two legs: the body loops from the head down to the belly
and up behind into the leaf tail, under a crest of autumn-leaf wings fanning back from behind the head.

ref.png: the whole dragon (mirrored to face left); layout px = ref.png px. parts/body.png (the sheet as
drawn, mirrored): far wing, near wing, the leg twice (the right one, toes forward, used for both) and the
body. parts/body_ref.png: that body scaled 0.87 and turned 12 deg onto ref.png (fitted), carved into head,
torso and a 2-piece tail. parts/wing_far.png: the far wing mirrored, so it fans back like the near one.
"""
from lib.paths import DRAGONS

P = DRAGONS / "leaf_dragon" / "parts"
carve = lambda keep, **kw: dict(sheet=P / "body_ref.png", src=(770, 600), at=(489, 195),   # the body island's top-left: body_ref px = layout px
                                  keep=[keep], **kw)

CONFIG = dict(
    name="Rồng Cây",
    size=0.5,    # as small as Rồng Lửa (its body is slim and the leaf crest tall: by body area it came out far bigger)
    body_src=P / "body.png",
    legs_src=P / "body.png",
    rigid_legs=True,   # each leg swings whole from the hip
    far_shade=0.8, wing_far_shade=0.85,
    leg_scale=1.0, leg_pull=0, ground=945,
    body={
        # the leaf crest: both wings fan up and back from behind the head (as on ref.png)
        "wing_far":  dict(sheet=P / "wing_far.png", src=(217, 330), at=(787, 209), img_scale=0.85, rot=-34),
        "tail_mid":  carve((860, 340, 1070, 580)),
        "tail_base": carve((920, 520, 1070, 810), fade_y=(570, 540)),
        "torso":     carve((550, 430, 975, 810), fade=(945, 975)),
        "head":      carve((470, 170, 860, 500), fade_y=(455, 495)),   # head and neck top, melting into the body
        "wing_near": dict(src=(647, 311), at=(755, 165), img_scale=1.05, rot=4),
    },
    joints={
        "torso": (760, 650),
        "head": (690, 470),          # where the neck meets the body
        "tail_base": (975, 730),     # where the tail turns up behind
        "tail_mid": (1000, 560),
        "wing_near": (768, 488),     # the leaf stems, behind the head
        "wing_far": (803, 471),
    },
    # the leaf crest grows from behind the head: both wings drawn behind the head and body, stems on the neck
    behind=["wing_near", "wing_far"],
    motion={"wingSpread": [0.1, -0.05], "flyLegs": "dangle", "sleepTail": [0.1, 0.15, 0.2], "stance": [0, 0],
            "rigidLegs": True, "stride": 70, "tailWave": [0.8, 1, 1, 1]},
    # a biped: both legs under the belly, the far one just behind the near one
    legs={"hind_near": dict(pick=(653, 741), scale=0.87, x=678), "hind_far": dict(pick=(653, 741), scale=0.8, x=585)},
)
