"""Vehicle model and shared geometry helpers.

The ``Vehicle`` dataclass tracks a single car. Cars accelerate toward a target
speed and brake with an exponential drag term (one of the two forms suggested
in the project spec):

    a_brake = exp(brake_d / gap) * v

This produces gentle following behaviour at large gaps and a hard brake when
``gap`` shrinks toward zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

TWOPI = 2.0 * np.pi


@dataclass
class Vehicle:
    car_id: int
    arm: int
    exit_arm: int
    spawn_time: float
    r: float
    angle: float
    velocity: float = 0.0
    state: str = "approach"
    color: str = "tab:blue"
    amax: float = 5.0
    brake_d: float = 7.0
    car_length: float = 4.5
    entry_time: Optional[float] = None
    exit_time: Optional[float] = None
    finish_time: Optional[float] = None
    crossing_s: float = 0.0
    history: list = field(default_factory=list)

    def accelerate(self, vmax: float, dt: float) -> None:
        self.velocity = min(abs(vmax), self.velocity + self.amax * dt)

    def brake(self, gap: float, dt: float) -> None:
        gap = max(float(gap), 0.15)
        decel = np.exp(self.brake_d / gap) * self.velocity
        self.velocity = max(0.0, self.velocity - decel * dt)

    def cruise_control(self, gap: Optional[float], vmax: float, dt: float) -> None:
        if gap is not None and gap < self.brake_d:
            self.brake(gap, dt)
        else:
            self.accelerate(vmax, dt)

    def total_time(self) -> float:
        if self.finish_time is None:
            return float("nan")
        return self.finish_time - self.spawn_time

    def wait_time(self) -> float:
        if self.entry_time is None:
            return float("nan")
        return self.entry_time - self.spawn_time

    def road_group(self) -> str:
        return "H" if self.arm in (0, 2) else "V"


def arm_angle(arm: int) -> float:
    return (arm % 4) * np.pi / 2.0


def turn_type(arm: int, exit_arm: int) -> str:
    diff = (exit_arm - arm) % 4
    if diff == 2:
        return "straight"
    if diff == 1:
        return "left"
    if diff == 3:
        return "right"
    return "u"


def choose_exit_arm(arm: int, rng: np.random.Generator, random_dest: bool = False) -> int:
    if not random_dest:
        return (arm + 2) % 4
    choices = [a for a in range(4) if a != arm]
    return int(rng.choice(choices))


def passed_angle(old_angle: float, new_angle: float, target_angle: float) -> bool:
    travelled = (new_angle - old_angle) % TWOPI
    target = (target_angle - old_angle) % TWOPI
    return 0.0 <= target <= travelled


def vehicle_xy(car: Vehicle, radius: float = 15.0, lane_offset: float = 2.8,
               mode: str = "roundabout") -> tuple[float, float]:
    if mode == "traffic_light" and car.state == "crossing":
        start = np.array([radius * np.cos(arm_angle(car.arm)),
                          radius * np.sin(arm_angle(car.arm))])
        end = np.array([radius * np.cos(arm_angle(car.exit_arm)),
                        radius * np.sin(arm_angle(car.exit_arm))])
        frac = np.clip(car.crossing_s / max(2.0 * radius, 1e-9), 0.0, 1.0)
        x, y = start * (1.0 - frac) + end * frac
        return float(x), float(y)

    theta = car.angle % TWOPI
    x = car.r * np.cos(theta)
    y = car.r * np.sin(theta)
    nx, ny = -np.sin(theta), np.cos(theta)
    lane = lane_offset

    if (mode == "traffic_light" and car.state == "approach"
            and turn_type(car.arm, car.exit_arm) == "left"
            and car.r <= 2.0 * radius):
        lane = 2.0 * lane_offset

    if car.state == "approach":
        x += lane * nx
        y += lane * ny
    elif car.state == "exit":
        x -= lane_offset * nx
        y -= lane_offset * ny
    return float(x), float(y)


def finite_mean(values) -> float:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    return float(np.mean(arr)) if len(arr) else float("nan")


def finite_std(values) -> float:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    return float(np.std(arr)) if len(arr) else float("nan")
