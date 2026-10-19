"""Tử Xà Long: legless purple sea serpent. It crawls on the island (the body undulates) and in battle
reaches out of a time rift.

parts/body.png (ChatGPT): head (drawn with the mouth open, lower jaw included), a separate lower jaw,
the front coil (neck + chest) and the whole rest of the body + tail + fan as ONE piece. That long
piece is carved here into 4 bones by sheet-x ranges (keep); each one runs a little past its cut and
fades out over the next across a wide 80 px band (fade), and since they come from one continuous drawing the joints don't show.
"""
from lib.paths import DRAGONS

SHEET = DRAGONS / "tu_xa_long" / "parts" / "body.png"
LONG = (420, 255)   # where the long body piece goes: its sheet top-left (400, 155) moved to join the coil

CONFIG = dict(
    name="Tử Xà Long",
    body_src=SHEET,
    legs_src=SHEET,           # no legs
    key="distance",           # purple dragon: magenta-ness keying would eat it
    far_shade=0.8, wing_far_shade=0.8,
    leg_scale=1.0, leg_pull=0, ground=1070,   # belly rests on the ground
    body={
        "tail_fan":  dict(src=(952, 567), at=LONG, keep=[(1150, 0, 1536, 1024)]),
        "tail_tip":  dict(src=(952, 567), at=LONG, keep=[(875, 0, 1265, 1024)], fade=(1185, 1265)),
        "tail_mid":  dict(src=(952, 567), at=LONG, keep=[(590, 0, 1000, 1024)], fade=(920, 1000)),
        "tail_base": dict(src=(952, 567), at=LONG, keep=[(380, 0, 720, 1024)], fade=(640, 720)),
        "torso":     dict(src=(271, 672), at=(98, 442)),          # front coil: neck + chest
        # the head was drawn with its mouth open: the drawn-in lower jaw is cut away (polygon below
        # the upper teeth, the throat behind it stays) and the separate jaw piece is used instead
        "jaw":       dict(src=(164, 433), at=(130, 299)),
        "head":      dict(src=(318, 236), at=(50, 89),
                          drop_poly=[[(150, 318), (185, 300), (230, 289), (264, 281), (283, 300), (286, 350),
                                      (268, 393), (138, 393), (132, 350)]]),
    },
    joints={
        "torso": (260, 700),
        "head": (315, 495),        # base of the neck, on the top of the coil
        "jaw": (305, 327),         # hinge at the back of the jaw
        "tail_base": (450, 870),   # where the long body leaves the coil
        "tail_mid": (720, 700),
        "tail_tip": (1000, 920),
        "tail_fan": (1265, 740),
    },
    parents={"jaw": "head"},
    # crawling: the body waves along its whole length (tail_base included)
    motion={"sleepTail": [0.12, 0.15, 0.2], "tailWave": [0.6, 0.9, 1.0, 0.8], "slither": True},
    legs={},
)
