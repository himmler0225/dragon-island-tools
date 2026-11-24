"""Fire Phoenix layout. Ice Phoenix uses the same layout (recoloured)."""
from lib.paths import DRAGONS

def layout(dragon_id: str, name: str, wing_root=(669, 946)) -> dict:
    return dict(
        name=name,
        body_src=DRAGONS / dragon_id / "parts" / "body.png",
        # legs.png with its round joint balls taken off (tools/strip_joint_balls.py): the pieces overlap instead
        legs_src=DRAGONS / dragon_id / "parts" / "legs_noballs.png",
        far_shade=0.8, wing_far_shade=0.88,
        size=1.035,   # the longer legs count towards the body area: without this the whole rig shrinks
        # legs longer than drawn (0.53 -> 0.59): standing tall as Hắc Long on its card art
        # the gaps the balls left (108 / 114 px) closed and ~40 px of overlap: thigh over shin over paw, outlines kept
        leg_scale=0.66, leg_pull=(168, 170), ground=1050,
        legs_down=True, joint_fade=0,
        no_caps=tuple(f"{leg}_{seg}" for leg in ("fore_near", "fore_far", "hind_near", "hind_far") for seg in ("upper", "lower", "paw")),
        # parts/wing_far.png (2026-11-09): the far wing drawn upright as Hắc Long's, its root ornament at the bottom
        place={"wing_far": dict(src=DRAGONS / dragon_id / "parts" / "wing_far.png", root=wing_root,
                                height_of="wing_near", height=1.0)},
        body={
            "wing_far":  dict(src=(1234, 321), at=(403, 330), rot=-30),
            "tail_tip":  dict(src=(1355, 763), at=(835, 520)),
            "tail_base": dict(src=(825, 752), at=(595, 615), rot=-18),   # raised: the tail sweeps up behind, not down with the leaning body
            # parts/torso_old.png (redraw 2026-11-01) places the body; parts/torso.png (redraw 2026-11-09, shaped as
            # Hắc Long's: a deep chest and a full belly, no legs painted on) is fitted over it (replace)
            "torso":     dict(src_img=DRAGONS / dragon_id / "parts" / "torso_old.png", img_scale=0.492, at=(135, 583)),
            "head":      dict(src=(206, 455), at=(95, 318)),
            "wing_near": dict(src=(701, 281), at=(444, 275), rot=-20),
        },
        replace={"torso": DRAGONS / dragon_id / "parts" / "torso.png"},
        parents={"tail_tip": "tail_base"},
        joints={
            "torso": (440, 760),
            "head": (270, 625),
            "wing_near": (470, 610),
            "wing_far": (420, 580),
            "tail_base": (625, 715),
            "tail_tip": (865, 755),
        },
        motion={"wingSpread": [0.22, -0.05], "flyLegs": "dangle", "flyPitch": 0.2, "stance": [0, 0]},   # far legs drawn a step ahead: all four show
        legs={"fore_near": dict(col=0, x=190), "hind_near": dict(col=1, x=480),
              "fore_far": dict(col=2, x=123), "hind_far": dict(col=3, x=419)},
    )


CONFIG = {**layout("fire_phoenix", "Phượng Hoàng Lửa"),
          # wings on the ground (wing_rest: in flight they beat from where they are drawn), as Hắc Long: the far wing fans up behind the head, its root on the back (turned forward rather than raised: no gap at the nape)
          "wing_rest": {"wing_far": (-120, -50, 0, 1.0), "wing_near": (-15, -5, 5, 1.1)},
          "wing_fly": {"wing_far": (0, 40)},   # in flight: the far wing's root down onto the back
          # legs straight as drawn, as Hồng Ngọc Long (2026-11-20; was a low crouch with the knees jutting)
          # (raise fore < 0: the shoulders sit low on the chest, so leaning back (motion.lean) still lets the front legs reach the ground)
          "crouch": {"drop": 0, "raise": {"fore": -6}}}
# crouched: shorter, lower steps (the default long stride stretched the bent legs out flat)
CONFIG["motion"] = {**CONFIG["motion"], "stride": 90, "liftScale": 0.7,
                    "lean": -0.06}   # chest a little up, as Hồng Ngọc Long
# (2026-11-20: no wing glow)

# 2026-11-20: the far legs placed as Hắc Long's: each far paw a step ahead of its near twin and a little up (it stands
# behind the body), the same offsets as Hắc Long's (with the rig editor tweaks): the whole far leg moved (layout px)
CONFIG["legs"] = {**CONFIG["legs"],
                  "fore_far": {**CONFIG["legs"]["fore_far"], "nudge": {s: (32, 7) for s in ("upper", "lower", "paw")}},
                  "hind_far": {**CONFIG["legs"]["hind_far"], "nudge": {s: (1, -13) for s in ("upper", "lower", "paw")}}}
