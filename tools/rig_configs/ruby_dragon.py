"""Hồng Ngọc Long (2026-11-02): a chibi red dragon with a gold belly, a sapphire on its chest, white feather
wings and an icy feather fan on its tail; it fights with ruby crystals. Four legs and two wings, but it never flies: it always walks.

ref.png: the whole dragon; layout px = ref.png px. parts/body.png: head, near wing, far wing. parts/torso.png:
the body from the neck to the tail tip in one piece (no legs) and the tail fan. parts/legs.png: 4 legs in
columns (fore near, hind near, fore far, hind far), each thigh / shin / paw (redraw 2026-11-09).
"""
from lib.paths import DRAGONS

P = DRAGONS / "ruby_dragon" / "parts"
# the body carved into torso + a 3-piece tail: each piece starts under the one drawn over it (torso >
# tail_base > tail_mid > tail_tip) and that one's cut end fades out over it. Placed at TORSO_K, top-left at TORSO_AT.
TORSO_AT, TORSO_K = (268, 490), 0.74
_carve = lambda keep, fade=None: dict(sheet=P / "torso.png", src=(741, 360), at=TORSO_AT, img_scale=TORSO_K, keep=[keep],
                                     **({"fade": fade} if fade else {}))

CONFIG = dict(
    name="Hồng Ngọc Long",
    size=1.2,   # a chibi dragon, shown a size up (the bigger legs count towards the body area: without this the whole rig shrinks)
    body_src=P / "body.png",
    legs_src=P / "legs.png",
    far_shade=0.72, wing_far_shade=0.93,
    # legs a little stouter than drawn: bigger still (0.76, widen 1.26) the thighs covered the belly, the
    # the 3 pieces of each leg as drawn, stacked: each overlaps the one above by about 45 px (sheet), so the joints close
    leg_scale=0.72, leg_pull=(80, 80), ground=985,   # long legs: the body stands high on them
    # thigh drawn over shin over paw: each piece's bottom end melts into the top of the next one (no line across
    # the joint), the lower piece's round top under it
    legs_down=True, joint_fade=0,   # crisp joints, outlines as drawn (fading them smudged the hind legs)
    # no joint caps on the legs: the hip one took in a piece of thigh (a second thigh showed when the leg moved off it),
    # and the pieces already overlap with outlines kept
    no_caps=tuple(f"{leg}_{seg}" for leg in ("fore_near", "fore_far", "hind_near", "hind_far") for seg in ("upper", "lower", "paw")),
    body={
        # src: the middle of the piece on its sheet; at: its top-left on ref.png
        "wing_far":  dict(src=(1259, 548), at=(205, 85), img_scale=0.95),   # the two wings as ref.png draws them: one V over the back
        "tail_fan":  dict(sheet=P / "torso.png", src=(1215, 675), at=(1203, 148), img_scale=0.75),
        "torso":     dict(sheet=P / "torso.png", src=(741, 360), at=TORSO_AT, img_scale=TORSO_K),   # with its whole tail: one piece
        # parts/head.png (2026-11-23): the head redrawn (fierce eyes, ref_new_head.png); its sheet is drawn ~6% smaller
        # than body.png (head 440 px wide there, 467 here): scaled to the old head's size, on the old head's box
        "head":      dict(src_img=P / "head.png", src=(271, 569), at=(230, 305), img_scale=0.61 * 467 / 440),
        "wing_near": dict(src=(765, 475), at=(456, 13), img_scale=0.84),
    },
    joints={
        "torso": (601, 740),
        "tail_fan": (1228, 533),   # the root of the fan, on the end of the tail
        "head": (400, 540),        # the back of the head, on the end of the neck
        "wing_near": (495, 650),   # both wings beat about the shoulder, the point of the V
        "wing_far": (470, 640),
    },
    parents={"tail_fan": "torso"},
    motion={"noFly": True,   # always on foot: never takes off (the island picks a walk instead)
            "wingSpread": [0.15, -0.05], "sleepTail": [0.1, 0.15, 0.2], "stance": [0, 0],
            "lean": -0.06,   # chest a little up
            "stride": 56, "liftScale": 0.5},
    # each column of legs.png (x: its left edge on the layout, scale: x leg_scale); each far leg half a leg ahead of its
    # near one (as Rồng Lửa), so all four show;
    # the hind shin and paw nudged back under the end of the thigh, the front paw forward under the end of the shin
    legs={"fore_near": dict(col=0, x=405, nudge={"paw": (-30, 0)}), "hind_near": dict(col=1, x=700, nudge={"lower": (34, -16), "paw": (2, 0)}),
          "fore_far": dict(col=2, x=318, scale=0.92, nudge={"paw": (-28, 0)}), "hind_far": dict(col=3, x=615, scale=0.92, nudge={"lower": (32, -15), "paw": (6, 0)})},
    # standing: the body sinks a little so every leg bends into a soft V, the front paws pushed forward (as on ref.png)
    crouch={"drop": -114, "reach": {"fore": 6, "hind": 44}, "raise": {"fore": -150, "hind": -140}},   # a tall stance: the body high on long legs, the hind shins leaning back (raise < 0: the legs sit lower on the body)
)
