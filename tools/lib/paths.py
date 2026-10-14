"""Shared path constants for the tools package."""
from pathlib import Path

# Resolve from this file's location: tools/lib/paths.py -> tools/ -> repo root
# When cwd ≠ repo root, Path(__file__).resolve().parent.parent lands in tools/ (not repo root).
# Detect by name: if we ended up in a "tools" directory, go one more level up.
_ROOT = Path(__file__).resolve().parent.parent
if _ROOT.name == "tools":
    _ROOT = _ROOT.parent
ROOT = _ROOT

ASSETS = ROOT / "assets"
PUBLIC = ROOT / "frontend" / "public"
DRAGONS = ASSETS / "dragons"
OUT = PUBLIC / "dragons"
UI_OUT = PUBLIC / "ui"
