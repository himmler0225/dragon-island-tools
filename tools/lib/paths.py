"""Shared path constants for the tools package."""
import os
from pathlib import Path

# Resolve from this file's location: tools/lib/paths.py -> tools/ -> repo root
# When cwd ≠ repo root, Path(__file__).resolve().parent.parent lands in tools/ (not repo root).
# Detect by name: if we ended up in a "tools" directory, go one more level up.
_ROOT = Path(__file__).resolve().parent.parent
if _ROOT.name == "tools":
    _ROOT = _ROOT.parent
ROOT = _ROOT

ASSETS = ROOT / "assets"
# Output goes into the game repo's frontend/public. Default: sibling checkout
# ../dragon-island; override with DRAGON_ISLAND_PUBLIC.
PUBLIC = Path(os.environ.get("DRAGON_ISLAND_PUBLIC") or ROOT.parent / "dragon-island" / "frontend" / "public").resolve()
DRAGONS = ASSETS / "dragons"
OUT = PUBLIC / "dragons"
UI_OUT = PUBLIC / "ui"
