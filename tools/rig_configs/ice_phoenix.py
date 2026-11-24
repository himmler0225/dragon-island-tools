"""Ice Phoenix: fire phoenix recoloured (same pieces, same positions) - shares its layout."""
from .fire_phoenix import layout

CONFIG = {**layout("ice_phoenix", "Phượng Hoàng Băng", wing_root=(653, 946)),
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
                  "fore_far": {**CONFIG["legs"]["fore_far"], "nudge": {s: (30, 9) for s in ("upper", "lower", "paw")}},
                  "hind_far": {**CONFIG["legs"]["hind_far"], "nudge": {s: (-8, -5) for s in ("upper", "lower", "paw")}}}
