"""Tuấn Long: chubby frost antler dragon."""
from lib.paths import DRAGONS

# The exploded view keeps the pieces near their places, so the layout is the sheet layout
# with the ~40 px gaps closed.

CONFIG = dict(
    name="Tuấn Long",
    body_src=DRAGONS / "tuan_long" / "parts" / "body.png",
    legs_src=DRAGONS / "tuan_long" / "parts" / "legs.png",
    far_shade=0.8, wing_far_shade=0.62,
    # knee pulled in 48 px (was 30): the thigh and shin read as one leg instead of stacked clumps
    leg_scale=0.42, leg_pull=(70, 50), ground=1080,
    body={
        "wing_far":  dict(src=(1236, 365), at=(380, 250)),
        "tail_tip":  dict(src=(1378, 685), at=(1105, 520)),
        "tail_mid":  dict(src=(1106, 824), at=(850, 728)),
        "tail_base": dict(src=(860, 787), at=(731, 690)),
        "torso":     dict(src=(488, 718), at=(230, 560)),
        "jaw":       dict(src=(102, 581), at=(107, 535)),     # teeth tucked under the upper lip
        "head":      dict(src=(315, 335), at=(87, 72)),   # pulled 35 px in onto the chest ruff
        "wing_near": dict(src=(715, 364), at=(430, 290)),
    },
    joints={
        "torso": (518, 735),
        "head": (385, 665),        # base of the neck, inside the chest ruff
        "jaw": (232, 563),         # hinge under the snout
        "wing_near": (472, 593),   # dark stub at the wing root, on the shoulder
        "wing_far": (422, 551),
        "tail_base": (760, 780),
        "tail_mid": (875, 798),
        "tail_tip": (1128, 808),
    },
    parents={"jaw": "head"},
    # hind legs 20 px forward so the thighs sit on the haunch drawn on the torso
    legs={"fore_near": dict(col=0, x=300), "hind_near": dict(col=1, x=580),
          "fore_far": dict(col=2, x=350), "hind_far": dict(col=3, x=620)},
)
