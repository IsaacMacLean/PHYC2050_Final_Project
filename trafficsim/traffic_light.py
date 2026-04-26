"""Two-phase traffic-light intersection simulation.

The geometry mirrors the roundabout (same arms, same exit roads, same
car-following physics) so that the two intersection types can be compared on
equal footing. A left-turn lane of length equal to the roundabout radius runs
in parallel with the through lane, so left-turning cars do not block through
traffic (per project spec).
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ._common import (
    can_spawn,
    record_frame,
    spawn_rates_by_arm,
    summarize_result,
    update_exits,
)
from .vehicle import (
    Vehicle,
    arm_angle,
    choose_exit_arm,
    turn_type,
)

LIGHT_COLORS = ["tab:blue", "tab:green", "tab:red", "tab:purple"]


def light_phase(t: float, cycle: float = 40.0) -> str:
    if cycle <= 0:
        raise ValueError("cycle must be positive")
    return "H" if (t % cycle) < (cycle / 2.0) else "V"


def _is_green(arm: int, t: float, cycle: float) -> bool:
    road = "H" if arm in (0, 2) else "V"
    return light_phase(t, cycle) == road


def _lane_index(car: Vehicle, radius: float, left_lane_length: float) -> int:
    if turn_type(car.arm, car.exit_arm) == "left" and car.r <= radius + left_lane_length:
        return 1
    return 0


def _update_approach(cars, t, dt, radius, road_vmax, cycle,
                     last_departure, discharge_headway, left_lane_length):
    stop_r = radius
    for arm in range(4):
        arm_cars = [c for c in cars if c.state == "approach" and c.arm == arm]
        lane_groups = {0: [], 1: []}
        for car in arm_cars:
            lane_groups[_lane_index(car, radius, left_lane_length)].append(car)

        for lane_index in (0, 1):
            approaching = lane_groups[lane_index]
            approaching.sort(key=lambda c: c.r)

            for i, car in enumerate(approaching):
                if i == 0:
                    green = _is_green(arm, t, cycle)
                    headway_ok = (t - last_departure[arm, lane_index]) >= discharge_headway
                    blocked = car.r <= stop_r + 0.25 and not (green and headway_ok)
                    gap = 0.1 if blocked else None
                else:
                    front = approaching[i - 1]
                    gap = car.r - front.r - car.car_length

                car.cruise_control(gap, road_vmax, dt)
                car.r -= car.velocity * dt

                if car.r <= stop_r:
                    green = _is_green(arm, t, cycle)
                    headway_ok = (t - last_departure[arm, lane_index]) >= discharge_headway
                    if green and headway_ok:
                        car.state = "crossing"
                        car.r = stop_r
                        car.crossing_s = 0.0
                        car.entry_time = t
                        car.velocity = max(1.0, car.velocity)
                        last_departure[arm, lane_index] = t
                    else:
                        car.r = stop_r
                        car.velocity = 0.0


def _update_crossing(cars, t, dt, radius, intersection_vmax):
    crossing = [c for c in cars if c.state == "crossing"]
    for car in crossing:
        car.cruise_control(None, intersection_vmax, dt)
        car.crossing_s += car.velocity * dt
        if car.crossing_s >= 2.0 * radius:
            car.state = "exit"
            car.exit_time = t
            car.r = radius
            car.angle = arm_angle(car.exit_arm)


def run_traffic_light_sim(spawn_rate_H: float = 0.08, spawn_rate_V: float = 0.08,
                          spawn_rates=None,
                          tmax: float = 220.0, warmup: float = 50.0, dt: float = 0.1,
                          seed: int = 0,
                          radius: float = 15.0, road_length: float = 95.0,
                          exit_length: float = 35.0,
                          road_vmax: float = 11.0, intersection_vmax: float = 8.0,
                          cycle: float = 40.0, discharge_headway: float = 1.5,
                          min_spawn_gap: float = 10.0, random_dest: bool = False,
                          left_lane_length: Optional[float] = None,
                          record: bool = False, record_stride: int = 5) -> dict:
    rng = np.random.default_rng(seed)
    rates = spawn_rates_by_arm(spawn_rate_H, spawn_rate_V, spawn_rates)
    finish_r = radius + exit_length
    left_lane_length = radius if left_lane_length is None else left_lane_length

    cars: List[Vehicle] = []
    frames: List[dict] = []
    active_history: List[int] = []
    last_departure = np.full((4, 2), -1e9, dtype=float)
    next_id = 0
    n_steps = int(np.ceil(tmax / dt))

    for step in range(n_steps):
        t = step * dt

        for arm, rate in enumerate(rates):
            arrivals = rng.poisson(rate * dt)
            for _ in range(arrivals):
                if can_spawn(cars, arm, road_length, min_spawn_gap):
                    exit_arm = choose_exit_arm(arm, rng, random_dest=random_dest)
                    car = Vehicle(
                        car_id=next_id,
                        arm=arm,
                        exit_arm=exit_arm,
                        spawn_time=t,
                        r=road_length,
                        angle=arm_angle(arm),
                        velocity=road_vmax * 0.65,
                        color=LIGHT_COLORS[arm],
                    )
                    cars.append(car)
                    next_id += 1

        _update_approach(cars, t, dt, radius, road_vmax, cycle, last_departure,
                         discharge_headway, left_lane_length)
        _update_crossing(cars, t, dt, radius, intersection_vmax)
        update_exits(cars, t, dt, road_vmax, finish_r)

        active_history.append(sum(c.state != "done" for c in cars))
        if record and step % record_stride == 0:
            frame = record_frame(cars, t, radius, mode="traffic_light")
            frame["phase"] = light_phase(t, cycle)
            frames.append(frame)

    out = summarize_result(cars, active_history, tmax, warmup)
    out.update({
        "kind": "traffic_light",
        "frames": frames,
        "radius": radius,
        "road_length": road_length,
        "finish_r": finish_r,
        "spawn_rates": rates,
        "cycle": cycle,
        "left_lane_length": left_lane_length,
        "tmax": tmax,
        "warmup": warmup,
        "dt": dt,
        "random_dest": random_dest,
    })
    return out
