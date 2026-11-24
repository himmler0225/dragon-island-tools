"""Băng Lộc Long (2026-11-09, tên tạm): a chubby chibi ice dragon with crystal antlers, an ice-crystal mane, small
black bat wings and an ice-crystal fan on its tail. Walks on 4 legs, never flies.

ref.png: the whole dragon; layout px = ref.png px. parts/body.png: head (with the upper jaw and the spiked collar),
lower jaw, near wing, far wing, torso (redraw 2026-11-09: from the neck tube to the
crystal fan at the end of the tail, smooth belly, no legs: one piece). parts/legs.png: 4 legs
in columns (fore near, hind near, fore far, hind far), each a round thigh crowned with an ice-crystal tuft / shin / clawed paw.
"""
from lib.paths import DRAGONS

P = DRAGONS / "frost_dragon" / "parts"
HK = 1.12          # head / jaw: body.png -> layout
TK = 1.0           # torso

CONFIG = dict(
    name="Băng Lộc Long",
    size=1.15,   # a size up from the default
    body_src=P / "body.png",
    legs_src=P / "legs.png",
    far_shade=0.78, wing_far_shade=0.85,
    leg_scale=0.57, leg_pull=(100, 72), ground=975,   # pieces overlapping ~35 px (sheet)
    # thigh drawn over shin over paw: each piece's bottom end melts into the top of the next one (no line across
    # the joint), the lower piece's round top under it
    legs_down=True,
    # no joint caps on the legs: the hip one took in a piece of thigh (a second thigh showed when the leg moved off it),
    # and the pieces already overlap with outlines kept
    no_caps=tuple(f"{leg}_{seg}" for leg in ("fore_near", "fore_far", "hind_near", "hind_far") for seg in ("upper", "lower", "paw")),
    body={
        "wing_far":  dict(src=(1334, 327), at=(610, 410), img_scale=0.7),
        "torso":     dict(src=(669, 731), at=(398, 460), img_scale=TK),   # the body with its whole tail and the crystal fan: one piece
        "jaw":       dict(src=(604, 421), at=(345, 425), img_scale=HK),
        "head":      dict(src=(328, 278), at=(309, 51), img_scale=HK),
        "wing_near": dict(src=(974, 324), at=(680, 494), img_scale=0.78),   # its root on the back, between the two ice tufts
    },
    joints={
        "torso": (650, 760),
        "head": (530, 600),        # the neck, under the mane
        "jaw": (573, 435),         # the back end of the jaw, under the mane
        "wing_near": (687, 680),   # its root ball sunk into the back, between the two ice tufts
        "wing_far": (616, 551),
    },
    parents={"jaw": "head"},
    motion={"noFly": True, "stance": [0, 0],
            # a chubby trot (as Rồng Lửa): diagonal pairs taking turns, short low even steps, the paws hardly tipping
            "gait": "trot", "duty": 0.55, "stride": 42, "liftScale": 0.42, "swingTilt": 0.3},
    # as Rồng Lửa: the 4 legs in a row under the body, standing straight, each far leg (a little smaller) half a leg
    # ahead of its near one so all four show; the thighs where the shoulder / hip sit (fore ~570, hind ~815)
    # standing nearly straight, the knees soft enough to step; raise < 0: the legs sit a little lower on the body
    crouch={"drop": 40, "raise": {"fore": 10, "hind": 10}},
    legs={"fore_near": dict(col=0, x=487), "hind_near": dict(col=1, x=747),
          "fore_far": dict(col=2, x=410, scale=0.92), "hind_far": dict(col=3, x=670, scale=0.92)},
)
