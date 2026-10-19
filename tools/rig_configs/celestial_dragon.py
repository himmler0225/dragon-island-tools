"""Celestial Dragon: black dragon recoloured pearl-white and gold (same pieces, same positions) - shares its layout."""
from .black_dragon import layout

# wing_far.png was redrawn a little smaller: its root swirl sits at a different source px
CONFIG = layout("than_long", "Thần Long", wing_root=(335, 742))
