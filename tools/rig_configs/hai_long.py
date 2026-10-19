"""Hải Long: wingless serpentine Eastern dragon."""
from lib.paths import DRAGONS

# body.png (redrawn 2026-10-15): head, jaw, front body, rear body, then three tail slices of one
# continuous tube, the last with the peacock fan. Pieces were pulled ~40 px apart along the body
# line; each is shifted back by ~35 px per step to close the gaps.
# The front and rear body pieces never joined cleanly (both ends were drawn as rounded caps, leaving a
# notch in the back), so the middle body was redrawn as ONE piece: parts/body_mid.png (2026-10-15).
# It is the torso; the tail starts straight at tail_mid and the hind legs hang from the torso.

CONFIG = dict(
    name="Hải Long",
    size=1.2,   # on-screen size vs the others (its pieces overlap a lot, so area alone makes it too small)
    body_src=DRAGONS / "hai_long" / "parts" / "body.png",
    legs_src=DRAGONS / "hai_long" / "parts" / "legs.png",
    far_shade=0.8, wing_far_shade=0.66,
    # knee 75 / ankle 50 px of overlap: with the longer stride the joints bend far enough to open gaps
    leg_scale=0.58, leg_pull=(95, 65), ground=960,
    body={
        "tail_fan":  dict(src=(1408, 504), at=(1110, 263)),
        "tail_tip":  dict(src=(1224, 723), at=(1000, 648)),
        "tail_mid":  dict(src=(1045, 719), at=(834, 622)),
        # whole middle body (chest, arched back, hips) from its own image, scaled to the sheet
        "torso":     dict(src_img=DRAGONS / "hai_long" / "parts" / "body_mid.png", img_scale=0.45, at=(330, 440)),
        "jaw":       dict(src=(134, 648), at=(178, 408)),    # lower jaw + beard, right under the snout
        # the head piece has a lower jaw drawn on it (hanging open with the beard): cut away, the
        # separate jaw piece (which opens when it spits) takes its place - no second jaw
        "head":      dict(src=(247, 420), at=(107, 99), drop_poly=[[(80, 478), (172, 478), (180, 498), (246, 512), (246, 548), (176, 548), (150, 600), (80, 600)]]),   # neck set into the chest of body_mid
    },
    joints={
        "torso": (493, 633),
        "head": (380, 660),        # base of the neck, tucked into the chest
        "jaw": (270, 422),         # hinge at the back of the jaw
        "tail_mid": (834, 744),
        "tail_tip": (1000, 775),
        "tail_fan": (1110, 705),
    },
    # the head piece carries the long neck down over the chest: the near front leg is drawn in front of it
    front=("fore_near_upper", "fore_near_lower", "fore_near_paw"),
    parents={"jaw": "head", "tail_mid": "torso"},
    # flies standing on a cloud (assets/dragons/hai_long/cloud.png, tools/slice_cloud.py) instead of wings
    motion={"sleepTail": [0.08, 0.1, 0.15], "rideCloud": True, "tailWave": [0, 0.45, 0.5, 0.55],
            "stride": 80},   # shorter steps: long strides bent its knees far enough to open them
    # front legs 15% taller: their tops reach up into the chest (feet stay on the ground)
    legs={"fore_near": dict(col=0, x=350, scale=1.35), "hind_near": dict(col=1, x=705),
          "fore_far": dict(col=2, x=410, scale=1.35), "hind_far": dict(col=3, x=765)},
)
