"""Per-species rig layouts. Each module exports a `CONFIG` dict consumed by tools/build_rig.py."""
from . import earth_dragon, fire_dragon
from . import ice_phoenix, fire_phoenix
from . import peacock, jade_flame_dragon, fire_spirit_boss, moon_dragon, stone_ghost_dragon, turtle_dragon, leaf_dragon, immortal_bird, ruby_dragon, frost_dragon, snowflight_dragon, rosebud_dragon
from . import black_dragon, sea_dragon, qilin, silver_dragon, gold_dragon, bone_dragon, celestial_dragon

CONFIGS = {
    "black_dragon":   black_dragon.CONFIG,
    "bone_dragon": bone_dragon.CONFIG,
    "sea_dragon":   sea_dragon.CONFIG,
    "peacock": peacock.CONFIG,
    "jade_flame_dragon": jade_flame_dragon.CONFIG,
    "moon_dragon": moon_dragon.CONFIG,
    "stone_ghost_dragon": stone_ghost_dragon.CONFIG,
    "turtle_dragon": turtle_dragon.CONFIG,
    "leaf_dragon": leaf_dragon.CONFIG,
    "immortal_bird": immortal_bird.CONFIG,
    "ruby_dragon": ruby_dragon.CONFIG,
    "frost_dragon": frost_dragon.CONFIG,
    "snowflight_dragon": snowflight_dragon.CONFIG,
    "rosebud_dragon": rosebud_dragon.CONFIG,
    "fire_spirit_boss": fire_spirit_boss.CONFIG,
    "qilin":     qilin.CONFIG,
    "fire_phoenix": fire_phoenix.CONFIG,
    "ice_phoenix": ice_phoenix.CONFIG,
    "earth_dragon": earth_dragon.CONFIG,
    "fire_dragon": fire_dragon.CONFIG,
    "gold_dragon":   gold_dragon.CONFIG,
    "silver_dragon":    silver_dragon.CONFIG,
    "celestial_dragon":   celestial_dragon.CONFIG,
}

# shared across all species
LEG_SIDES = {
    "fore_near": False, "hind_near": False,
    "fore_far": True,   "hind_far": True,
}
