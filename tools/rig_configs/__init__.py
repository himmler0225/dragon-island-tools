"""Per-species rig layouts.

Every dragon has the same bones (head, torso, wings, 3 tail pieces, 4 legs × 3 pieces) so the game
animates them all with the same code; a species may add optional bones (e.g. "jaw").

Each module exports a single `CONFIG` dict consumed by tools/build_rig.py.
This package's __init__ aggregates them into the `CONFIGS` dict expected by the pipeline.
"""
from . import hac_long, hai_long, ki_lan, rong_xuong, tuan_long

CONFIGS = {
    "hac_long":   hac_long.CONFIG,
    "rong_xuong": rong_xuong.CONFIG,
    "tuan_long":  tuan_long.CONFIG,
    "hai_long":    hai_long.CONFIG,
    "ki_lan":      ki_lan.CONFIG,
}

# shared across all species
LEG_SIDES = {
    "fore_near": False, "hind_near": False,
    "fore_far": True,   "hind_far": True,
}
