"""Per-species rig layouts. Each module exports a `CONFIG` dict consumed by tools/build_rig.py."""
from . import ice_dragon, forest_dragon, earth_dragon, fire_dragon
from . import ice_phoenix, fire_phoenix
from . import black_dragon, sea_dragon, qilin, silver_dragon, gold_dragon, bone_dragon, celestial_dragon, void_serpent, stag_dragon

CONFIGS = {
    "hac_long":   black_dragon.CONFIG,
    "rong_xuong": bone_dragon.CONFIG,
    "tuan_long":  stag_dragon.CONFIG,
    "hai_long":   sea_dragon.CONFIG,
    "ki_lan":     qilin.CONFIG,
    "tu_xa_long": void_serpent.CONFIG,
    "phuong_hoang_lua": fire_phoenix.CONFIG,
    "phuong_hoang_bang": ice_phoenix.CONFIG,
    "rong_dat_nau": earth_dragon.CONFIG,
    "rong_bang_xanh_bien": ice_dragon.CONFIG,
    "rong_lua_do": fire_dragon.CONFIG,
    "rong_cay_xanh_la": forest_dragon.CONFIG,
    "rong_vang":   gold_dragon.CONFIG,
    "rong_bac":    silver_dragon.CONFIG,
    "than_long":   celestial_dragon.CONFIG,
}

# shared across all species
LEG_SIDES = {
    "fore_near": False, "hind_near": False,
    "fore_far": True,   "hind_far": True,
}
