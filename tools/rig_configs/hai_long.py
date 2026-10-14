"""Hải Long: wingless serpentine Eastern dragon."""
from lib.paths import DRAGONS

# body.png (redrawn 2026-10-15): head, jaw, front body, rear body, then three tail slices of one
# continuous tube, the last with the peacock fan. Pieces were pulled ~40 px apart along the body
# line; each is shifted back by ~35 px per step to close the gaps.
# rear body tucked 40 px under the front body and raised to its back line; the front body's cut end
# fades out (fade, sheet x) so it melts into the rear body instead of showing a rim.

CONFIG = dict(
    name="Hải Long",
    body_src=DRAGONS / "hai_long" / "parts" / "body.png",
    legs_src=DRAGONS / "hai_long" / "parts" / "legs.png",
    far_shade=0.8, wing_far_shade=0.66,
    leg_scale=0.58, leg_pull=30, ground=960,
    body={
        "tail_fan":  dict(src=(1408, 504), at=(1110, 263)),
        "tail_tip":  dict(src=(1224, 723), at=(1000, 648)),
        "tail_mid":  dict(src=(1045, 719), at=(834, 622)),
        "tail_base": dict(src=(817, 606), at=(582, 450)),    # rear body: back + hips
        "torso":     dict(src=(514, 594), at=(335, 440), fade=(620, 668)),    # front body: chest + shoulders
        "jaw":       dict(src=(134, 648), at=(98, 468)),    # lower jaw + beard, right under the snout
        "head":      dict(src=(247, 420), at=(27, 159)),
    },
    joints={
        "torso": (493, 633),
        "head": (300, 720),        # base of the neck, tucked into the chest
        "jaw": (190, 482),         # hinge at the back of the jaw
        "tail_base": (582, 624),   # where the rear body leaves the front body
        "tail_mid": (834, 744),
        "tail_tip": (1000, 775),
        "tail_fan": (1110, 705),
    },
    parents={"jaw": "head"},
    # flies standing on a cloud (assets/dragons/hai_long/cloud.png, tools/slice_cloud.py) instead of wings
    # tail_base is the whole rear body: it only sways a little; the real tail pieces do the swishing
    motion={"sleepTail": [0.08, 0.1, 0.15], "rideCloud": True, "tailWave": [0.25, 0.45, 0.5, 0.55]},
    legs={"fore_near": dict(col=0, x=360), "hind_near": dict(col=1, x=705, parent="tail_base"),
          "fore_far": dict(col=2, x=420), "hind_far": dict(col=3, x=765, parent="tail_base")},
)
