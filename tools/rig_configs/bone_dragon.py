"""Rồng Xương (redesign 2026-10-14): chibi bone WYVERN — two legs, the wings are its front limbs."""
from lib.paths import DRAGONS

# parts/body.png: skull+neck, jaw, ribcage, both wings, 3 tail pieces (joint ends are bone knobs);
# parts/legs.png: the two legs (bottom half; the top half repeats the wings and is cropped away).

CONFIG = dict(
    name="Rồng Xương",
    size=0.88,   # on-screen size vs the others (bone gaps count as empty, so area alone makes it too big)
    body_src=DRAGONS / "rong_xuong" / "parts" / "body.png",
    legs_src=DRAGONS / "rong_xuong" / "parts" / "legs.png",
    legs_crop=(0, 455, 1536, 1024),
    far_shade=0.82, wing_far_shade=0.78,
    # legs 0.95 (were 1.15 and read too big for the body); ground raised with them so the hips stay put
    leg_scale=0.95, leg_pull=(45, 30), ground=1140,   # bone knobs overlap so the knee never gapes
    body={
        "wing_far":  dict(src=(548, 272), at=(353, 150)),
        "tail_tip":  dict(src=(1417, 649), at=(1190, 536)),
        "tail_mid":  dict(src=(1234, 743), at=(1072, 699)),
        "tail_base": dict(src=(1052, 735), at=(922, 675)),
        "torso":     dict(src=(718, 676), at=(476, 523)),
        "jaw":       dict(src=(225, 730), at=(150, 628)),
        "head":      dict(src=(287, 526), at=(80, 369)),
        "wing_near": dict(src=(1066, 348), at=(676, 146)),
    },
    joints={
        "torso": (718, 690),
        "head": (520, 645),        # neck knob on the front of the ribcage
        "jaw": (358, 648),         # hinge knob at the back of the jaw, under the skull
        "wing_far": (600, 560),    # shoulder knobs on top of the ribcage
        "wing_near": (700, 575),
        "tail_base": (935, 700),   # pelvis knob
        "tail_mid": (1090, 745),
        "tail_tip": (1210, 735),
    },
    parents={"jaw": "head"},
    # stance: far foot a step ahead when standing; idleHover: rests in the air, wings beating;
    # flyHang: its short legs hang down in flight (trailing back they read as tucked)
    motion={"sleepTail": [0.06, 0.08, 0.1], "stance": [0, -70], "idleHover": 70, "flyHang": [0.35, 0.35]},
    # a biped: both hips sit together under the pelvis (far one a touch behind, for depth) so the two
    # legs scissor around the same point; set apart, they met in the middle and read as one leg stepping
    legs={"hind_near": dict(col=1, x=690), "hind_far": dict(col=2, x=715)},
)
