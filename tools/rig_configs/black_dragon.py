"""Black Dragon layout. Celestial Dragon uses the same layout (recoloured)."""
from lib.paths import DRAGONS

# far legs slightly darker than near: much darker and they vanish into the body

def layout(dragon_id: str, name: str, wing_root=(330, 800)) -> dict:
  return dict(
    name=name,
    body_src=DRAGONS / dragon_id / "parts" / "body.png",
    legs_src=DRAGONS / dragon_id / "parts" / "legs.png",
    far_shade=0.78, wing_far_shade=0.72,
    leg_scale=0.42, leg_pull=(65, 50), ground=960,
    replace={"head": DRAGONS / dragon_id / "parts" / "head.png"},
    motion={"wingSpread": [0.22, -0.05], "flyLegs": "dangle", "flyPitch": 0.2},
    place={"wing_far": dict(src=DRAGONS / dragon_id / "parts" / "wing_far.png", root=wing_root,
                            height_of="wing_near", height=1.05, rot=-85)},
    body={
        "wing_far":  dict(src=(1174, 306), at=(470, 150)),
        "tail_tip":  dict(src=(1375, 684), at=(1010, 380)),
        "tail_mid":  dict(src=(1141, 772), at=(860, 600)),
        "tail_base": dict(src=(896, 698), at=(720, 560)),
        "torso":     dict(src=(566, 664), at=(330, 470)),
        "head":      dict(src=(223, 409), at=(150, 120)),
        "wing_near": dict(src=(709, 292), at=(400, 179)),
    },
    joints={
        "torso": (560, 700),
        "head": (370, 620),
        "wing_near": (520, 571),
        "wing_far": (540, 555),
        "tail_base": (770, 640),
        "tail_mid": (890, 660),
        "tail_tip": (1060, 740),
    },
    legs={"fore_near": dict(col=0, x=340), "hind_near": dict(col=1, x=600),
          "fore_far": dict(col=2, x=390), "hind_far": dict(col=3, x=640)},
)

CONFIG = layout("hac_long", "Hắc Long")
