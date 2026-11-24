"""Rồng Ma Thạch (2026-10-31): a floating armored serpent with red crystal wings, two clawed arms and a
tail tip set with red crystal lenses; its ultimate fires a red beam from the tail. Flies in battle.

parts/body.png: head (open jaw), near wing (big, middle top), far wing (right top), near arm (left, upper),
far arm (left, lower) and an old body with the tail stretched back (unused: torso.png). The head sits on
the neck tube, the arms hang from the shoulder socket, the wings rise from the back.
"""
from lib.paths import DRAGONS

P = DRAGONS / "stone_ghost_dragon" / "parts" / "body.png"
# parts/head.png (redraw 2026-11-09): the head split for an opening mouth: the upper head with a dark mouth
# interior under its teeth (left) and the lower jaw drawn level (right), placed at HK. The jaw is turned JAW_ROT
# about its hinge (the round end under the cheek) to lie closed under the upper teeth.
H = DRAGONS / "stone_ghost_dragon" / "parts" / "head.png"
HK, HEAD_AT = 0.5, (480, 120)
HL = lambda x, y: (HEAD_AT[0] + (x - 45) * HK, HEAD_AT[1] + (y - 92) * HK)   # head.png px -> layout px
JK, JAW_ROT = HK * 0.885, 9.4
T = DRAGONS / "stone_ghost_dragon" / "parts" / "torso.png"
# torso.png (redraw 2026-10-31): neck + body + the tail curling down and FORWARD in a "C", its lens tip in
# front under the arms. Drawn bigger than body.png's pieces: placed at 0.8, layout = torso px * 0.8 + 300.
# Carved into torso + a 3-piece tail (polygons in torso.png px), each piece under the one drawn over it
# (torso > tail_base > tail_mid > tail_tip), whose cut end fades out over it.
K, O = 0.8, 300
L = lambda x, y: (x * K + O, y * K + O)   # torso.png px -> layout px
# parts/torso_split.png (redraw 2026-11-20, latest: each end a closed, rounded dark cap): the same body split in two by the artist: the body (left) and the tail curl with the lenses (right), both at SK x torso.png's size. Placed
# where they lie on torso.png (matched): the tail under the body, swaying gently about the ring where they meet.
SPLIT, SK = DRAGONS / "stone_ghost_dragon" / "parts" / "torso_split.png", 1.0
TAIL_JOINT = (964, 750)   # torso.png px: the body's end ring, over the tail's
carve = lambda poly, **kw: dict(sheet=T, src=(771, 539), at=L(389, 65), img_scale=K, keep_poly=[poly], **kw)

CONFIG = dict(
    name="Rồng Ma Thạch",
    size=0.95,
    key="distance",   # purple eye: key_magenta would read it as background
    body_src=P,
    legs_src=P,
    rigid_legs=True,   # each arm swings whole from its shoulder ball
    far_shade=0.8, wing_far_shade=0.8,
    leg_scale=1.0, leg_pull=0, ground=1170,   # below the tail: it floats
    body={
        "wing_far":  dict(src=(1254, 256), at=(790, 163), rot=-22),
        # the whole body in ONE piece (neck, body and the tail curled forward): carved into torso + 3 tail bones, the
        # cuts by the chest opened up whenever the tail swayed
        "torso":     dict(src_img=SPLIT, src=(440, 420), img_scale=K * SK, at=L(498, 72)),
        "tail_tip":  dict(src_img=SPLIT, src=(1325, 500), img_scale=K * SK, at=L(400, 408)),
        "jaw":       dict(src_img=H, src=(1150, 700), img_scale=JK,
                          at=(HL(470, 680)[0] - (1360 - 956) * JK, HL(470, 680)[1] - (620 - 575) * JK), rot=JAW_ROT),
        "head":      dict(src_img=H, src=(400, 400), img_scale=HK, at=HEAD_AT),
        "wing_near": dict(src=(754, 247), at=(842, 138), rot=-12),
    },
    parents={"jaw": "head", "tail_tip": "torso"},
    joints={
        "torso": L(800, 500),
        "tail_tip": L(*TAIL_JOINT),
        "head": (765, 431),        # on the neck tube
        "jaw": HL(470, 680),       # the hinge: the round back end of the jaw, under the cheek
        "wing_near": (860, 452),   # the wing roots on the back, behind the neck
        "wing_far": (810, 430),
    },
    # float: the arms keep their own pose (foreArms) and the body bobs; it flies in battle
    motion={"float": True, "foreArms": True, "armPose": [[0, 0], [0, 0]], "flyLegs": "dangle",
            "sleepTail": [0, 0, 0], "stance": [0, 0], "wingSpread": [0.05, -0.05],
            "tailWave": [1, 1, 0.55, 1]},   # the tail sways gently (~4 deg) about the ring where it meets the body
    # the arms hang from the torso's shoulder socket (their shoulder balls on it), the far one a step behind
    legs={"fore_near": dict(pick=(265, 578), x=598, top=513),
          "fore_far":  dict(pick=(275, 828), x=592, top=506)},   # just behind the near arm: its shoulder ball hidden under the near one
)
