"""Traffic flow simulation for the PHYC2050/MATH2052 final project.

Compares a four-arm roundabout with a two-phase traffic-light intersection
under Poisson arrivals, identical car-following physics, and a left-turn lane
of length equal to the roundabout radius (per project spec).
"""

from .vehicle import (
    Vehicle,
    arm_angle,
    turn_type,
    choose_exit_arm,
    passed_angle,
    vehicle_xy,
    finite_mean,
    finite_std,
    TWOPI,
)
from .roundabout import run_roundabout_sim
from .traffic_light import run_traffic_light_sim, light_phase
from .analysis import run_repeated, SUMMARY_METRICS
from .plotting import (
    draw_base_roads,
    plot_frame,
    animate_result,
    animate_roundabout,
)

__all__ = [
    "Vehicle",
    "arm_angle",
    "turn_type",
    "choose_exit_arm",
    "passed_angle",
    "vehicle_xy",
    "finite_mean",
    "finite_std",
    "TWOPI",
    "run_roundabout_sim",
    "run_traffic_light_sim",
    "light_phase",
    "run_repeated",
    "SUMMARY_METRICS",
    "draw_base_roads",
    "plot_frame",
    "animate_result",
    "animate_roundabout",
]
