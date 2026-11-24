"""Rồng Phi Tuyết (2026-11-17): a white-furred ice dragon with blue crystal horns, a gold beak and belly, two
turquoise fairy wings and a snowflake on its tail tip. Walks on 4 legs and flies.

ref.png: the whole dragon (card art, 1254 px square, with a background); layout px = ref.png px.
parts/body_raw.png: head with the upper jaw (left), the lower jaw (under it), the torso with the neck and the
tail (right). parts/wings_raw.png: near wing (left), far wing (right), roots at the bottom.
parts/legs_raw.png: 4 legs in columns (fore near, hind near, fore far, hind far), each thigh / shin / paw.
"""
from lib.paths import DRAGONS

P = DRAGONS / "snowflight_dragon" / "parts"
HK = 0.78                       # head sheet px -> layout px
HEAD_AT = (80, 312)             # the head piece's top-left on the layout
TK, TORSO_AT = 0.85, (179, 429)   # body_raw.png redrawn 2026-11-17 (old: body_old.png at (210, 430))
WK = 0.9                        # wings sheet px -> layout px
WING_NEAR_ROOT, WING_FAR_ROOT = (560, 700), (450, 690)

LEGS = ("fore_near", "fore_far", "hind_near", "hind_far")

CONFIG = dict(
    name="Rồng Phi Tuyết",
    body_src=P / "body_raw.png",
    legs_src=P / "legs_raw.png",
    far_shade=0.8, wing_far_shade=0.85,
    leg_scale=0.5, leg_pull=(100, 115), ground=1110, leg_widen=1.18,   # chunkier legs
    legs_down=True, joint_fade=0,
    no_caps=tuple(f"{leg}_{seg}" for leg in LEGS for seg in ("upper", "lower", "paw")),
    body={
        "torso": dict(src_img=P / "body_raw.png", src=(1150, 450), img_scale=TK, at=TORSO_AT),
        "jaw":   dict(src_img=P / "body_raw.png", src=(230, 700), img_scale=HK, at=(98, 632)),
        "head":  dict(src_img=P / "body_raw.png", src=(290, 320), img_scale=HK, at=HEAD_AT, scale=0.87),
        # the wings' roots: (sheet root - bbox top-left) * WK lands on the root point
        "wing_far":  dict(src_img=P / "wings_raw.png", src=(1090, 515), img_scale=WK,
                          at=(WING_FAR_ROOT[0] - 26 * WK, WING_FAR_ROOT[1] - 956 * WK)),
        "wing_near": dict(src_img=P / "wings_raw.png", src=(440, 515), img_scale=WK,
                          at=(WING_NEAR_ROOT[0] - 34 * WK, WING_NEAR_ROOT[1] - 960 * WK)),
    },
    joints={
        "torso": (620, 800),
        "head": (360, 640),   # the back of the head, on the neck
        "jaw": (290, 700),    # the hinge at the back of the jaw
        "wing_near": WING_NEAR_ROOT,
        "wing_far": WING_FAR_ROOT,
    },
    parents={"jaw": "head"},
    motion={"wingSpread": [0.22, -0.05], "flyLegs": "dangle", "flyPitch": 0.2, "stance": [0, 0],
            "gait": "trot", "duty": 0.55, "stride": 50, "liftScale": 0.45, "swingTilt": 0.3},
    # the far legs half a leg ahead of the near ones, so all four show
    legs={"fore_near": dict(col=0, x=300), "hind_near": dict(col=1, x=640),
          "fore_far": dict(col=2, x=190), "hind_far": dict(col=3, x=530)},
    crouch={"drop": 20},
    wing_glow={"color": (120, 220, 255)},
)
