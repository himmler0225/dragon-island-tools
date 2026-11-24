"""Rồng Rùa (2026-10-31): a stubby teal turtle dragon under a golden rock shell. Attacks with two cannons that
rise out of its shell, eyes lit and mouth open. Walks on 4 legs, never flies.

parts/body.png: the head (left, unused) and the body with the neck, shell and short tail in one piece (no
legs); layout px = body.png px. parts/head.png: the head with its yellow lower jaw closed, split by
tools/split_head_jaw.py turtle_dragon 18 38 --up 200 (with a tall dark mouth interior: an opened jaw shows a mouth, not the island) into head_upper.png and head_jaw.png, placed over the head
on body.png (head.png px x 421/798), moved onto the neck. parts/legs.png (redraw 2026-11-17, legs_old.png: 2026-11-09): 4 jointed legs in columns
(fore near, hind near, fore far, hind far), each a round shoulder ball / shin / clawed paw. parts/cannons.png: the two shell cannons, base at the bottom, muzzle up-left.
"""
from lib.paths import DRAGONS

P = DRAGONS / "turtle_dragon" / "parts"
HK = 421 / 798   # head.png -> layout (the old head)
NK = 0.70          # heads.png -> layout
NEW_AT = (250, 285)   # the new head's top-left on the layout
JAW_UP = 140        # heads.png px the jaw is drawn up from where the sheet has it: tucked under the upper teeth
JAW_X = 22          # and px to the right
CK = 0.5         # cannons.png -> layout

CONFIG = dict(
    name="Rồng Rùa",
    size=1.15,   # the bigger legs count towards the body area: without this the whole rig shrinks
    key="tight",   # pink belly stripe and purple shade under the shell: magenta keying would eat them
    body_src=P / "body.png",
    legs_src=P / "legs.png",
    far_shade=0.8, wing_far_shade=0.8,
    # short sturdy legs: the pieces overlap well past their gaps (ball over shin, shin over paw), a little widened
    # ball drawn over shin over paw (legs_down), outlines kept, no joint caps on the legs: bent in a step, a cap showed
    # as a second ball / shin round the knee
    legs_down=True, joint_fade=0,   # outlines kept: the outer edge runs on unbroken from piece to piece
    no_caps=tuple(f"{leg}_{seg}" for leg in ("fore_near", "fore_far", "hind_near", "hind_far") for seg in ("upper", "lower", "paw")),
    # legs.png (redraw 2026-11-17): thigh / shin / foot drawn 47 / 40 px apart, lined up and as wide where they meet;
    # ~65 px of overlap so the joints hold when bent
    leg_scale=0.7, leg_pull=(150, 100), ground=950, leg_widen=1.1,   # the shin tucked up past the thigh's narrow neck into the ball: their outlines join
    body={
        # the cannons fully out (a strike), each through one of the two holes on top of the shell (the
        # swirl-stone mouths: front (665, 252), back (790, 190)), the barrel's middle in the hole; at rest
        # they sink cannon_drop px into the shell
        "cannon_far":  dict(src_img=P / "cannons.png", src=(1136, 522), at=(675, 4), img_scale=CK),
        "cannon_near": dict(src_img=P / "cannons.png", src=(484, 524), at=(554, 68), img_scale=CK),
        "torso":       dict(src=(952, 523), at=(488, 155), fade=(540, 500)),   # the neck tube's rim melts away under the head
        # heads.png (redraw 2026-11-10; split at x 740 into heads_normal.png / heads_lit.png, as the tight keying joins the
        # two heads through the eye glow's ray): the head (left), the same head lit for a strike (right: glowing eyes, a ray to
        # the left) and the lower jaw (under them). NK: heads.png px -> layout; NEW_AT: the head's top-left (layout)
        # (heads.png redraw 2026-11-10: the jaw drawn with its tongue: no dark mouth band behind it)
        "jaw":         dict(src_img=P / "heads_normal.png", src=(429, 756), img_scale=NK,
                            at=(NEW_AT[0] + (194 - 153 + JAW_X) * NK, NEW_AT[1] + (662 - 159 - JAW_UP) * NK)),
        "head":        dict(src_img=P / "heads_normal.png", src=(438, 398), img_scale=NK, at=NEW_AT,
                            feather=dict(x=NEW_AT[0] + 470 * NK, px=16)),   # the back of the head melts into the neck
        # the lit head drawn over it, its right edge on the head's (matched on the horns: 99 px further left)
        "head_attack": dict(src_img=P / "heads_lit.png", src=(1080, 400), img_scale=NK, at=(NEW_AT[0] - 107 * NK + 10, NEW_AT[1]),   # matched on the horns
                            feather=dict(x=NEW_AT[0] + 470 * NK, px=16)),
    },
    cannon_drop=260,
    joints={
        "torso": (900, 560),
        "head": (685, 510),          # on the neck
        "jaw": (640, 560),           # the back end of the jaw, under the cheek
        "head_attack": (685, 510),   # = the head's
        "cannon_near": (665, 252),   # the shell holes they come out of
        "cannon_far": (790, 190),
    },
    parents={"jaw": "head", "head_attack": "head"},
    motion={"noFly": True, "stance": [0, 0], "sleepTail": [0, 0, 0],
            # an even plod: short, low, regular steps under a steady shell
            "stride": 48, "liftScale": 0.5, "sway": 0.3, "gait": "trot",
            "duty": 0.5,   # each diagonal pair on the ground exactly half the cycle: they take turns, never both up / down
            "eye": [0.43, 0.64]},   # the pupil on head.png (glowing eyes in its skills)
    # the far legs a step ahead of the near ones, so all four show standing and their whole step shows
    legs={"fore_near": dict(col=0, x=618), "hind_near": dict(col=1, x=1003),
          "fore_far": dict(col=2, x=520), "hind_far": dict(col=3, x=905)},
    # the body sinks a little: the jointed legs stand bent instead of locked straight, so the knees can fold to step
    crouch={"drop": 18},
)
