"""Per-species rig layouts for tools/build_rig.py.

Every dragon has the same bones (head, torso, wings, 3 tail pieces, 4 legs x 3 pieces) so the game
animates them all with the same code; a species may add optional bones (e.g. "jaw").

Layout px = body-sheet px. For each body piece:
  src    centre of the piece's bounding box in parts/body.png (picks the piece)
  at     layout position of the bounding box's top-left corner (the rest pose)
  scale  optional size factor about the joint (pieces hanging off it scale too)
  fade   optional sheet x range (from, to) over which the piece fades out, so a cut end melts into
         the piece drawn under it
joints   layout point each bone rotates about
skip     body pieces to leave out of the rig
crest    cut the top of the head piece into a separate "crest" bone (or drop it)
replace  piece name -> redrawn image (one piece on magenta) used instead of the body-sheet piece
place    piece name -> standalone image: its `root` (source px) is put on the joint, scaled to `height`
         x the height of piece `height_of`
motion   optional per-species overrides for public/rig.js (e.g. sleepTail angles)
legs     col = column in parts/legs.png (0..3), x = left edge in the layout
ground   layout y of the ground line; leg_scale = leg sheet px -> layout px;
leg_pull = px ChatGPT pulled leg pieces apart (closed again); one value or (knee, ankle)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAGONS = ROOT / "assets" / "dragons"

# far legs are only a little darker (0.8): any darker and they vanish into the body, so the walk
# looks like only the near legs move
LEG_SIDES = {"fore_near": False, "hind_near": False, "fore_far": True, "hind_far": True}

HAC_LONG = dict(
    name="Hắc Long",
    body_src=DRAGONS / "hac_long" / "parts" / "body.png",
    legs_src=DRAGONS / "hac_long" / "parts" / "legs.png",
    far_shade=0.78, wing_far_shade=0.72,
    leg_scale=0.42, leg_pull=42, ground=960,
    # head redrawn without the dark spiky crest (it read as a stiff third wing); aligned onto the
    # original head piece by its face and neck (the lower 60%, which did not change)
    replace={"head": DRAGONS / "hac_long" / "parts" / "head.png"},
    # on the ground the wings spread into a V (near wing leans back, far wing forward) so both show
    # wings flap in flight while the four legs hang stretched out, swaying a little
    motion={"wingSpread": [0.22, -0.05], "flyLegs": "dangle", "flyPitch": 0.2},   # flies nose-up
    # far wing drawn on its own (the sheet's far wing was a copy of the near one and hid behind it):
    # its root (the swirl, source px of wing_far.png) goes on the joint, sized relative to the near wing,
    # and turned to rise up and forward behind the head (like the original art) while the near wing
    # fans back toward the tail, so the two read as a V
    place={"wing_far": dict(src=DRAGONS / "hac_long" / "parts" / "wing_far.png", root=(330, 800),
                            height_of="wing_near", height=1.05, rot=-85)},   # rises up and forward, behind the head
    body={
        # wings sit ON the back; the far wing sits a little higher and further back than the near
        # one, so both are seen beating
        "wing_far":  dict(src=(1174, 306), at=(470, 150)),
        "tail_tip":  dict(src=(1375, 684), at=(1010, 380)),
        "tail_mid":  dict(src=(1141, 772), at=(860, 600)),
        "tail_base": dict(src=(896, 698), at=(720, 560)),
        "torso":     dict(src=(566, 664), at=(330, 470)),
        "head":      dict(src=(223, 409), at=(110, 140)),
        "wing_near": dict(src=(709, 292), at=(400, 179)),
    },
    joints={
        "torso": (560, 700),       # body root: middle of the torso
        "head": (330, 640),        # base of the neck
        "wing_near": (520, 571),   # wing root: bottom of the stub where it meets the back
        "wing_far": (540, 555),    # far shoulder, on the back just ahead of the near wing root
        "tail_base": (770, 640),
        "tail_mid": (890, 660),
        "tail_tip": (1060, 740),
    },
    legs={"fore_near": dict(col=0, x=340), "hind_near": dict(col=1, x=600),
          "fore_far": dict(col=2, x=390), "hind_far": dict(col=3, x=640)},
)

# Rồng Xương (redesign 2026-10-14): chibi bone WYVERN — two legs, the wings are its front limbs.
# parts/body.png: skull+neck, jaw, ribcage, both wings, 3 tail pieces (joint ends are bone knobs);
# parts/legs.png: the two legs (bottom half; the top half repeats the wings and is cropped away).
RONG_XUONG = dict(
    name="Rồng Xương",
    body_src=DRAGONS / "rong_xuong" / "parts" / "body.png",
    legs_src=DRAGONS / "rong_xuong" / "parts" / "legs.png",
    legs_crop=(0, 455, 1536, 1024),
    far_shade=0.82, wing_far_shade=0.78,
    leg_scale=1.15, leg_pull=0, ground=1218,
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
    motion={"sleepTail": [0.06, 0.08, 0.1]},
    legs={"hind_near": dict(col=1, x=630), "hind_far": dict(col=2, x=760)},   # one leg forward, one back
)

# Tuấn Long: chubby frost antler dragon; the exploded view keeps the pieces near their places,
# so the layout is the sheet layout with the ~40 px gaps closed.
TUAN_LONG = dict(
    name="Tuấn Long",
    body_src=DRAGONS / "tuan_long" / "parts" / "body.png",
    legs_src=DRAGONS / "tuan_long" / "parts" / "legs.png",
    far_shade=0.8, wing_far_shade=0.62,
    leg_scale=0.42, leg_pull=30, ground=1080,
    body={
        "wing_far":  dict(src=(1236, 365), at=(380, 250)),
        "tail_tip":  dict(src=(1378, 685), at=(1105, 520)),
        "tail_mid":  dict(src=(1106, 824), at=(850, 728)),
        "tail_base": dict(src=(860, 787), at=(731, 690)),
        "torso":     dict(src=(488, 718), at=(230, 560)),
        "jaw":       dict(src=(102, 581), at=(62, 539)),
        "head":      dict(src=(315, 335), at=(52, 57)),
        "wing_near": dict(src=(715, 364), at=(430, 290)),
    },
    joints={
        "torso": (518, 735),
        "head": (350, 650),        # base of the neck, inside the chest ruff
        "jaw": (192, 564),         # hinge under the snout
        "wing_near": (472, 593),   # dark stub at the wing root, on the shoulder
        "wing_far": (422, 551),
        "tail_base": (760, 780),
        "tail_mid": (875, 798),
        "tail_tip": (1128, 808),
    },
    parents={"jaw": "head"},
    legs={"fore_near": dict(col=0, x=290), "hind_near": dict(col=1, x=600),
          "fore_far": dict(col=2, x=340), "hind_far": dict(col=3, x=640)},
)

# Hải Long: wingless serpentine Eastern dragon. The sheet has 6 body pieces: head, jaw, front body,
# rear body (the arched back + hips), a short tail piece and the tail fan. The rear body is used as
# tail_base so the whole back undulates; the hind legs hang from it (parent) so they follow the hips.
HAI_LONG = dict(
    name="Hải Long",
    body_src=DRAGONS / "hai_long" / "parts" / "body.png",
    legs_src=DRAGONS / "hai_long" / "parts" / "legs.png",
    far_shade=0.8, wing_far_shade=0.66,
    leg_scale=0.58, leg_pull=30, ground=960,
    # body.png (redrawn 2026-10-15): head, jaw, front body, rear body, then three tail slices of one
    # continuous tube, the last with the peacock fan. Pieces were pulled ~40 px apart along the body
    # line; each is shifted back by ~35 px per step to close the gaps.
    # rear body tucked 40 px under the front body and raised to its back line; the front body's cut end
    # fades out (fade, sheet x) so it melts into the rear body instead of showing a rim
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

# Kì Lân: qilin. body.png has head, lower jaw (with the red beard) and body+tail in one piece; the
# tail is carved off the body (sheet rects) so it can swish. legs.png has 2 pieces per leg
# (thigh, shin+paw); the lower one is split at the ankle.
KI_LAN = dict(
    name="Kì Lân",
    body_src=DRAGONS / "ki_lan" / "parts" / "body.png",
    legs_src=DRAGONS / "ki_lan" / "parts" / "legs.png",
    far_shade=0.8, wing_far_shade=0.8,
    key="distance",            # purple mane: magenta-ness keying would eat it
    # knee pulled in 50 px: the thigh ends round, so the shin must start well inside it or the knee gapes
    leg_scale=0.56, leg_pull=(50, 24), ground=1050, leg_split="last",
    body={
        # tail: everything right of the hip tuft and below it (drawn behind the body, overlapping it)
        "tail_base": dict(src=(931, 595), at=(359, 299), keep=[(1010, 470, 1536, 1024)]),
        "torso":     dict(src=(931, 595), at=(359, 299), drop=[(1040, 600, 1536, 1024), (1130, 470, 1536, 1024)]),
        "jaw":       dict(src=(170, 631), at=(105, 470)),
        # head 85% (it read too big for the body), tucked 25 px closer onto the neck
        "head":      dict(src=(247, 276), at=(70, 110), scale=0.85),
    },
    joints={
        "torso": (760, 650),
        "head": (445, 485),        # back of the head, on the neck
        "jaw": (275, 485),         # hinge at the back of the jaw
        "tail_base": (1035, 620),  # tail root under the hip tuft
    },
    parents={"jaw": "head"},
    # hind legs are drawn with the knee bent back (like the front ones): keep it that way in the IK
    motion={"sleepTail": [0.12, 0, 0], "hindKnee": "back"},
    legs={"fore_near": dict(col=0, x=420), "hind_near": dict(col=1, x=780),
          "fore_far": dict(col=2, x=460), "hind_far": dict(col=3, x=820)},
)

CONFIGS = {"hac_long": HAC_LONG, "rong_xuong": RONG_XUONG, "tuan_long": TUAN_LONG, "hai_long": HAI_LONG, "ki_lan": KI_LAN}
