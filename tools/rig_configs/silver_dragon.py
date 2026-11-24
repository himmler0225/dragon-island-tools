"""Silver Dragon: the gold dragon recoloured (same pieces, same positions) - shares its layout."""
from .gold_dragon import layout

CONFIG = {**layout("silver_dragon", "Rồng Bạc", wing_root=(636, 940)),
          # on the ground the far wing peeks up ahead of the near one, both a little smaller than drawn;
          # in flight both beat from where they are drawn (wing_rest, not wing_fit)
          "wing_rest": {"wing_far": (-60, -90, 0, 0.85), "wing_near": (20, -30, 8, 1.0)}}

# 2026-11-20: the far legs placed as Hắc Long's: each far paw a step ahead of its near twin and a little up (it stands
# behind the body), the same offsets as Hắc Long's (with the rig editor tweaks): the whole far leg moved (layout px)
CONFIG["legs"] = {**CONFIG["legs"],
                  "fore_far": {**CONFIG["legs"]["fore_far"], "nudge": {s: (26, -43) for s in ("upper", "lower", "paw")}},
                  "hind_far": {**CONFIG["legs"]["hind_far"], "nudge": {s: (13, -18) for s in ("upper", "lower", "paw")}}}
# (2026-11-20, later: a biped lifting its far hind leg as high as Hắc Long's reads as a step: only ~8 rig px up)
