"""Black Dragon: dark winged four-legged dragon. Celestial Dragon is the same drawing recoloured (pieces at
the same sheet positions), so both use this layout through `layout(id, name, wing_root)`."""
from lib.paths import DRAGONS

# far legs are only a little darker (0.8): any darker and they vanish into the body, so the walk
# looks like only the near legs move

def layout(dragon_id: str, name: str, wing_root=(330, 800)) -> dict:
  return dict(
    name=name,
    body_src=DRAGONS / dragon_id / "parts" / "body.png",
    legs_src=DRAGONS / dragon_id / "parts" / "legs.png",
    far_shade=0.78, wing_far_shade=0.72,
    leg_scale=0.42, leg_pull=(65, 50), ground=960,   # deep overlap: the long stride bends the joints far
    # head redrawn without the dark spiky crest (it read as a stiff third wing); aligned onto the
    # original head piece by its face and neck (the lower 60%, which did not change)
    replace={"head": DRAGONS / dragon_id / "parts" / "head.png"},
    # on the ground the wings spread into a V (near wing leans back, far wing forward) so both show
    # wings flap in flight while the four legs hang stretched out, swaying a little
    motion={"wingSpread": [0.22, -0.05], "flyLegs": "dangle", "flyPitch": 0.2},   # flies nose-up
    # far wing drawn on its own (the sheet's far wing was a copy of the near one and hid behind it):
    # its root (the swirl, source px of wing_far.png) goes on the joint, sized relative to the near wing,
    # and turned to rise up and forward behind the head (like the original art) while the near wing
    # fans back toward the tail, so the two read as a V
    place={"wing_far": dict(src=DRAGONS / dragon_id / "parts" / "wing_far.png", root=wing_root,
                            height_of="wing_near", height=1.05, rot=-85)},   # rises up and forward, behind the head
    body={
        # wings sit ON the back; the far wing sits a little higher and further back than the near
        # one, so both are seen beating
        "wing_far":  dict(src=(1174, 306), at=(470, 150)),
        "tail_tip":  dict(src=(1375, 684), at=(1010, 380)),
        "tail_mid":  dict(src=(1141, 772), at=(860, 600)),
        "tail_base": dict(src=(896, 698), at=(720, 560)),
        "torso":     dict(src=(566, 664), at=(330, 470)),
        "head":      dict(src=(223, 409), at=(150, 120)),   # neck plates tucked onto the chest (they stood out as a second chest)
        "wing_near": dict(src=(709, 292), at=(400, 179)),
    },
    joints={
        "torso": (560, 700),       # body root: middle of the torso
        "head": (370, 620),        # base of the neck
        "wing_near": (520, 571),   # wing root: bottom of the stub where it meets the back
        "wing_far": (540, 555),    # far shoulder, on the back just ahead of the near wing root
        "tail_base": (770, 640),
        "tail_mid": (890, 660),
        "tail_tip": (1060, 740),
    },
    legs={"fore_near": dict(col=0, x=340), "hind_near": dict(col=1, x=600),
          "fore_far": dict(col=2, x=390), "hind_far": dict(col=3, x=640)},
)


CONFIG = layout("hac_long", "Hắc Long")
