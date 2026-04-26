"""Per-script setup: makes the trafficsim package importable when running the
scripts directly (``python scripts/04_roundabout_volume_sweep.py``) and exposes
shared output paths and matplotlib styling.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = REPO_ROOT / "figures"
MOVIES_DIR = REPO_ROOT / "figures"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

GLOBAL_SEED = 2050

plt.rcParams.update({
    "figure.dpi": 115,
    "savefig.dpi": 160,
    "font.size": 11,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def quick_mode() -> bool:
    return "--quick" in sys.argv
