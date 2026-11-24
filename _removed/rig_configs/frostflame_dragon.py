"""Băng Diễm Long (2026-11-15, tên tạm): a chunky ice dragon with a snout horn, a green spirit-flame mane, a wing of
floating ice crystals and a green flame tuft on its tail. Walks on 4 legs, never flies.

ref.png: the whole dragon; layout px = ref.png px. parts/body.png: the head with the upper jaw (left), the lower jaw
with a dark mouth inside (under it), the torso with the tail and the wing's crystals (right; the crystals are loose
islands). parts/torso.png: body.png without the head and jaw (all its islands are the torso: the crystals ride on it).
parts/legs.png: 4 legs in columns (fore near, hind near, fore far, hind far), each thigh / shin / paw.
"""
from lib.paths import DRAGONS

P = DRAGONS / "frostflame_dragon" / "parts"
HEAD_AT = (288, 186)            # the head's top-left on ref.png (body.png piece at (58, 128))
TK, TORSO_AT = 0.92, (497, 132)  # torso.png -> layout, its top-left (the piece's box starts at (578, 124))

CONFIG = dict(
    name="Băng Diễm Long",
    body_src=P / "body.png",
    legs_src=P / "legs.png",
    far_shade=0.78, wing_far_shade=0.85,
    leg_scale=0.55, leg_pull=(100, 90), ground=890,
    # thigh over shin over paw, outlines kept; no joint caps on the legs
    legs_down=True, joint_fade=0,
    no_caps=tuple(f"{leg}_{seg}" for leg in ("fore_near", "fore_far", "hind_near", "hind_far") for seg in ("upper", "lower", "paw")),
    body={
        "torso": dict(src_img=P / "torso.png", whole=True, img_scale=TK, at=TORSO_AT),
        "jaw":   dict(src_img=P / "body.png", src=(266, 751), at=(355, 468)),
        "head":  dict(src_img=P / "body.png", src=(323, 342), at=HEAD_AT),
    },
    joints={
        "torso": (700, 650),
        "head": (560, 560),   # the back of the head, on the neck
        "jaw": (570, 525),    # the hinge at the back of the jaw
    },
    parents={"jaw": "head"},
    motion={"noFly": True, "stance": [0, 0], "gait": "trot", "duty": 0.55, "stride": 46, "liftScale": 0.45, "swingTilt": 0.3},
    # the far legs half a leg ahead of the near ones, so all four show
    legs={"fore_near": dict(col=0, x=470), "hind_near": dict(col=1, x=760),
          "fore_far": dict(col=2, x=560), "hind_far": dict(col=3, x=840)},
    crouch={"drop": 22},
)
