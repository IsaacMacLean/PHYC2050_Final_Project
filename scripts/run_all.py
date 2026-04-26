"""Run every numbered analysis script in order.

Pass ``--quick`` to thread the flag through to every script, which uses
shorter ``tmax`` and fewer grid points so the full pipeline finishes in a few
minutes for smoke testing.
"""

from _setup import quick_mode

import importlib.util
import sys
from pathlib import Path

SCRIPTS = [
    "01_two_car_braking.py",
    "02_pedestrian_light.py",
    "03_demo_animations.py",
    "04_roundabout_volume_sweep.py",
    "05_asymmetric_traffic_contour.py",
    "06_roundabout_vs_lights.py",
    "07_cycle_length_sweep.py",
    "08_random_destinations.py",
    "09_radius_sensitivity.py",
]


def run_script(path: Path) -> None:
    print(f"\n=== {path.name} ===")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


def main() -> None:
    here = Path(__file__).resolve().parent
    for name in SCRIPTS:
        run_script(here / name)
    print("\nAll scripts completed.")


if __name__ == "__main__":
    # quick_mode() is read by individual scripts via _setup
    _ = quick_mode()
    main()
