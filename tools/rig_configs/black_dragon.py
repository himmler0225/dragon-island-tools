"""Black Dragon layout. Celestial Dragon uses the same layout (recoloured)."""
from lib.paths import DRAGONS

# far legs slightly darker than near: much darker and they vanish into the body

def layout(dragon_id: str, name: str, wing_root=(641, 948)) -> dict:
  return dict(
    name=name,
    body_src=DRAGONS / dragon_id / "parts" / "body.png",
    # parts/legs_phoenix.png (2026-11-20): the phoenixes' legs (legs_noballs.png) recoloured for this dragon, same
    # pieces and places: assembled as theirs (pull, thigh over shin over paw, no caps). The old legs.png is unused.
    legs_src=DRAGONS / dragon_id / "parts" / "legs_phoenix.png",
    far_shade=0.78, wing_far_shade=0.84,
    # legs longer and sturdier than drawn (0.5 -> 0.56): standing tall as on the card art, legs about 2/5 of its height
    size=1.035,   # the longer legs count towards the body area: without this the whole rig shrinks
    leg_scale=0.6, leg_pull=(168, 170), ground=1015,   # the phoenix pull: the pieces overlap ~40 px
    # no cap behind the ankles (the disc took in toes and claws, which bulged out as the paw tipped in a step) or the
    # hips (it took in a piece of thigh, which stayed on the body while the leg stepped)
    no_caps=tuple(f"{leg}_{seg}" for leg in ("fore_near", "fore_far", "hind_near", "hind_far") for seg in ("upper", "lower", "paw")),
    legs_down=True, joint_fade=0,   # as the phoenixes / Hồng Ngọc Long: thigh over shin over paw, outlines as drawn, no caps
    # torso.png (redraw 2026-11-09): the body without the shoulder / haunch muscles painted on it (the legs are their own pieces)
    replace={"head": DRAGONS / dragon_id / "parts" / "head.png", "torso": DRAGONS / dragon_id / "parts" / "torso.png"},
    motion={"wingSpread": [0.22, -0.05], "flyLegs": "dangle", "flyPitch": 0.2, "stance": [0, 0]},   # far legs drawn a step ahead: all four show
    # parts/wing_far.png (redraw 2026-11-09): the far wing drawn upright, its root ornament at the bottom
    place={"wing_far": dict(src=DRAGONS / dragon_id / "parts" / "wing_far.png", root=wing_root,
                            height_of="wing_near", height=1.05)},
    body={
        "wing_far":  dict(src=(1174, 306), at=(470, 150)),
        "tail_tip":  dict(src=(1375, 684), at=(1010, 380)),
        "tail_mid":  dict(src=(1141, 772), at=(860, 600)),
        "tail_base": dict(src=(896, 698), at=(720, 560), rot=-12),   # raised: the tail sweeps up behind, not down with the leaning body
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
    legs={"fore_near": dict(col=0, x=320), "hind_near": dict(col=1, x=565, scale=1.1),
          "fore_far": dict(col=2, x=251), "hind_far": dict(col=3, x=499, scale=1.1)},
)

CONFIG = {**layout("black_dragon", "Hắc Long"),
          # wings on the ground (wing_rest: in flight they beat from where they are drawn), spread wide as on the card art:
          # the far wing rises behind the head, the near one from the back leaning towards the tail
          "wing_rest": {"wing_far": (-200, -80, -8, 0.95), "wing_near": (30, -20, 15, 1.1)}}
# legs redrawn crouched (round, overlapping joints): a low stance and shorter steps
# 2026-11-20: legs straight as drawn, as Hồng Ngọc Long (no sunk body, no jutting knees); the fore hips a little low so
# the front paws still reach the ground with the chest a little up
CONFIG["crouch"] = {"drop": 0, "raise": {"fore": -6}}
CONFIG["motion"] = {**CONFIG["motion"], "stride": 75,
                    "lean": -0.06}   # chest a little up, as Hồng Ngọc Long
CONFIG["wing_glow"] = {"color": (60, 170, 255)}   # a blue light on the wing rims, lit by the wing beat
CONFIG["body_aura"] = {"color": (70, 175, 255)}   # 2026-11-20: the whole body glows blue
