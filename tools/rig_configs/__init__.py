"""Per-species rig layouts.

Every dragon has the same bones (head, torso, wings, 3 tail pieces, 4 legs × 3 pieces) so the game
animates them all with the same code; a species may add optional bones (e.g. "jaw").

Each module exports a single `CONFIG` dict consumed by tools/build_rig.py.
This package's __init__ aggregates them into the `CONFIGS` dict expected by the pipeline.
"""
from . import rong_bang_xanh_bien, rong_cay_xanh_la, rong_lua_do
from . import phuong_hoang_bang, phuong_hoang_lua
from . import hac_long, hai_long, ki_lan, rong_bac, rong_dat_nau, rong_vang, rong_xuong, than_long, tu_xa_long, tuan_long

CONFIGS = {
    "hac_long":   hac_long.CONFIG,
    "rong_xuong": rong_xuong.CONFIG,
    "tuan_long":  tuan_long.CONFIG,
    "hai_long":    hai_long.CONFIG,
    "ki_lan":      ki_lan.CONFIG,
    "tu_xa_long":  tu_xa_long.CONFIG,
    "phuong_hoang_lua": phuong_hoang_lua.CONFIG,
    "phuong_hoang_bang": phuong_hoang_bang.CONFIG,
    "rong_dat_nau": rong_dat_nau.CONFIG,
    "rong_bang_xanh_bien": rong_bang_xanh_bien.CONFIG,
    "rong_lua_do": rong_lua_do.CONFIG,
    "rong_cay_xanh_la": rong_cay_xanh_la.CONFIG,
    "rong_vang":   rong_vang.CONFIG,
    "rong_bac":    rong_bac.CONFIG,
    "than_long":   than_long.CONFIG,
}

# shared across all species
LEG_SIDES = {
    "fore_near": False, "hind_near": False,
    "fore_far": True,   "hind_far": True,
}
