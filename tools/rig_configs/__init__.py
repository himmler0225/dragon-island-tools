"""Per-species rig layouts. Each module exports a `CONFIG` dict consumed by tools/build_rig.py."""
from . import earth_dragon, fire_dragon
from . import ice_phoenix, fire_phoenix
from . import peacock
from . import east_sea_dragon, west_sea_dragon, north_sea_dragon, south_sea_dragon
from . import black_dragon, sea_dragon, qilin, silver_dragon, gold_dragon, bone_dragon, celestial_dragon, void_serpent, stag_dragon

CONFIGS = {
    "black_dragon":   black_dragon.CONFIG,
    "bone_dragon": bone_dragon.CONFIG,
    "stag_dragon":  stag_dragon.CONFIG,
    "sea_dragon":   sea_dragon.CONFIG,
    "peacock": peacock.CONFIG,
    "east_sea_dragon": east_sea_dragon.CONFIG,
    "west_sea_dragon": west_sea_dragon.CONFIG,
    "north_sea_dragon": north_sea_dragon.CONFIG,
    "south_sea_dragon": south_sea_dragon.CONFIG,
    "qilin":     qilin.CONFIG,
    "void_serpent": void_serpent.CONFIG,
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
