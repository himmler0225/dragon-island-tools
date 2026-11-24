"""Rồng Nụ Tầm Xuân (2026-11-23): a little green serpent dragon with a crown of rosebud petals and swirls, pink fairy
wings, four leaf feet and a lotus bud on its tail tip. It slithers on the ground (its body waves: DragonRig bodyWave),
paddling with its leaves; it never flies.

ref.png: the whole dragon; layout px = ref.png px. Pieces placed where they lie on ref.png (matched).
parts/head_leaves.png: head with the upper jaw (top left), the lower jaw (right), 4 leaf feet (bottom row).
parts/wing_body.png: the near wing (top), the body with the tail and its bud in ONE piece (bottom).
parts/wing_far.png: the far wing (drawn bigger: fitted to the near wing's height).
"""
from lib.paths import DRAGONS

P = DRAGONS / "rosebud_dragon" / "parts"
HL, WB = P / "head_leaves.png", P / "wing_body.png"
HK = 0.96                      # head sheet px -> layout px
WN_K, WN_AT = 0.68, (505, 273)  # near wing
WING_ROOT = (515, 575)          # both wings' root on the back, behind the petal collar

CONFIG = dict(
    name="Rồng Nụ Tầm Xuân",
    key="tight",   # pink wings and petals: only near-exact magenta is background
    body_src=WB,
    legs_src=HL,
    legs_crop=(0, 650, 1535, 1024),   # the leaf feet: the bottom row of head_leaves.png
    rigid_legs=True,   # each leaf swings whole from where it meets the body
    far_shade=0.8, wing_far_shade=0.85,
    leg_scale=1.0, leg_pull=0, ground=830,
    body={
        "torso": dict(src_img=WB, src=(796, 717), img_scale=0.86, at=(350, 383)),
        "jaw":   dict(src_img=HL, src=(1057, 502), img_scale=HK * 0.8, at=(118, 528)),
        "head":  dict(src_img=HL, src=(470, 320), img_scale=HK, at=(89, 41)),
        "wing_near": dict(src_img=WB, src=(725, 280), img_scale=WN_K, at=WN_AT),
        # wing_far.png is drawn bigger: scaled to the near wing's height, its root (sheet ~(400, 820)) on the back
        "wing_far": dict(src_img=P / "wing_far.png", src=(770, 490), img_scale=0.45, at=(529, 245)),
    },
    joints={
        "torso": (640, 660),
        "head": (360, 540),       # the back of the head, on the neck
        "jaw": (300, 590),        # the hinge at the back of the jaw
        "wing_near": WING_ROOT,
        "wing_far": (WING_ROOT[0] + 30, WING_ROOT[1] - 10),
    },
    parents={"jaw": "head"},
    motion={"noFly": True, "slither": True, "bodyWave": 1, "stance": [0, 0], "wingSpread": [0.1, -0.05],
            "sleepTail": [0, 0, 0]},
    # the leaves: near ones as drawn on ref.png, far ones a step ahead and a little up (as Hắc Long's far legs)
    legs={"fore_near": dict(pick=(246, 847), x=443, scale=0.6),
          "hind_near": dict(pick=(618, 843), x=765, scale=0.55),
          "fore_far":  dict(pick=(973, 848), x=410, scale=0.55, nudge={"upper": (0, -22)}),
          "hind_far":  dict(pick=(1320, 835), x=720, scale=0.5, nudge={"upper": (0, -26)})},
)
