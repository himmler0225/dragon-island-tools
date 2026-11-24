"""Celestial Dragon: black dragon recoloured pearl-white and gold (same pieces, same positions) - shares its layout."""
from .black_dragon import layout

# its own wing_far.png: the root ornament sits at a different source px
CONFIG = {**layout("celestial_dragon", "Thần Long", wing_root=(635, 945)),
          # wings on the ground (wing_rest: in flight they beat from where they are drawn), spread wide as on the card art:
          # the far wing rises behind the head, the near one from the back leaning towards the tail
          "wing_rest": {"wing_far": (-200, -80, -8, 0.95), "wing_near": (30, -20, 15, 1.1)}}
# legs redrawn crouched (round, overlapping joints): a low stance and shorter steps
# 2026-11-20: legs straight as drawn, as Hồng Ngọc Long (no sunk body, no jutting knees); the fore hips a little low so
# the front paws still reach the ground with the chest a little up
CONFIG["crouch"] = {"drop": 0, "raise": {"fore": -6}}
CONFIG["motion"] = {**CONFIG["motion"], "stride": 75,
                    "lean": -0.06}   # chest a little up, as Hồng Ngọc Long
CONFIG["wing_glow"] = True   # a golden light on the wing rims, lit by the wing beat
CONFIG["body_aura"] = {"color": (255, 205, 90)}   # 2026-11-20: the whole body glows gold

# 2026-11-20: the far legs placed as Hắc Long's: each far paw a step ahead of its near twin and a little up (it stands
# behind the body), the same offsets as Hắc Long's (with the rig editor tweaks): the whole far leg moved (layout px)
CONFIG["legs"] = {**CONFIG["legs"],
                  "fore_far": {**CONFIG["legs"]["fore_far"], "nudge": {s: (18, 3) for s in ("upper", "lower", "paw")}},
                  "hind_far": {**CONFIG["legs"]["hind_far"], "nudge": {s: (-11, -9) for s in ("upper", "lower", "paw")}}}
