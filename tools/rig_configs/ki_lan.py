"""Kì Lân: qilin."""
from lib.paths import DRAGONS

# body.png has head, lower jaw (with the red beard) and body+tail in one piece; the
# tail is carved off the body (sheet rects) so it can swish.
# legs.png has 2 pieces per leg (thigh, shin+paw); the lower one is split at the ankle.

CONFIG = dict(
    name="Kì Lân",
    body_src=DRAGONS / "ki_lan" / "parts" / "body.png",
    legs_src=DRAGONS / "ki_lan" / "parts" / "legs.png",
    far_shade=0.8, wing_far_shade=0.8,
    key="distance",            # purple mane: magenta-ness keying would eat it
    # knee pulled in 50 px: the thigh ends round, so the shin must start well inside it or the knee gapes
    leg_scale=0.56, leg_pull=(50, 24), ground=1050, leg_split="last",
    body={
        # tail: everything right of the hip tuft and below it (drawn behind the body, overlapping it)
        "tail_base": dict(src=(931, 595), at=(359, 299), keep=[(1010, 470, 1536, 1024)]),
        "torso":     dict(src=(931, 595), at=(359, 299), drop=[(1040, 600, 1536, 1024), (1130, 470, 1536, 1024)]),
        "jaw":       dict(src=(170, 631), at=(105, 470)),
        # head 85% (it read too big for the body), tucked 25 px closer onto the neck
        "head":      dict(src=(247, 276), at=(70, 110), scale=0.85),
    },
    joints={
        "torso": (760, 650),
        "head": (445, 485),        # back of the head, on the neck
        "jaw": (275, 485),         # hinge at the back of the jaw
        "tail_base": (1035, 620),  # tail root under the hip tuft
    },
    parents={"jaw": "head"},
    # hind legs are drawn with the knee bent back (like the front ones): keep it that way in the IK
    motion={"sleepTail": [0.12, 0, 0], "hindKnee": "back"},
    legs={"fore_near": dict(col=0, x=420), "hind_near": dict(col=1, x=780),
          "fore_far": dict(col=2, x=460), "hind_far": dict(col=3, x=820)},
)
