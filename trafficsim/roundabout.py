"""Polar-coordinate roundabout simulation.

Cars arrive at the four arms via a Poisson process, decelerate toward the
yield line at ``r = radius + stop_buffer``, and enter the circulating lane
when no oncoming car violates a time-gap criterion. Inside the circle they
travel along an arc and exit when they sweep past their target arm angle.
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
    TWOPI,
    Vehicle,
    arm_angle,
    choose_exit_arm,
    passed_angle,
)

ROUNDABOUT_COLORS = ["tab:blue", "tab:green", "tab:red", "tab:purple"]


def _can_enter(car: Vehicle, circle_cars: List[Vehicle], radius: float,
               min_entry_gap: float, reaction_time: float, capacity_gap: float) -> bool:
    if not circle_cars:
        return True

    max_capacity = max(1, int((TWOPI * radius) // capacity_gap))
    if len(circle_cars) >= max_capacity:
        return False

    entry = arm_angle(car.arm)
    speed_scale = max([car.velocity] + [c.velocity for c in circle_cars])
    yield_gap = max(min_entry_gap, reaction_time * speed_scale)
    follow_gap = max(min_entry_gap, car.car_length + 2.0)

    for other in circle_cars:
        approaching_arc = radius * ((entry - other.angle) % TWOPI)
        ahead_arc = radius * ((other.angle - entry) % TWOPI)
        if 0.0 < approaching_arc < yield_gap:
            return False
        if 0.0 < ahead_arc < follow_gap:
            return False
    return True


def _update_approach(cars, t, dt, radius, road_vmax, circle_vmax,
                     min_entry_gap, reaction_time, stop_buffer, capacity_gap):
    stop_r = radius + stop_buffer
    circle_cars = [c for c in cars if c.state == "circle"]

    for arm in range(4):
        approaching = [c for c in cars if c.state == "approach" and c.arm == arm]
        approaching.sort(key=lambda c: c.r)

        for i, car in enumerate(approaching):
            if i == 0:
                can_enter = _can_enter(car, circle_cars, radius, min_entry_gap,
                                       reaction_time, capacity_gap)
                blocked = car.r <= stop_r + 0.25 and not can_enter
                gap = 0.1 if blocked else None
            else:
                front = approaching[i - 1]
                gap = car.r - front.r - car.car_length

            speed_limit = (min(road_vmax, circle_vmax * 1.4)
                           if car.r < radius + 18.0 else road_vmax)
            car.cruise_control(gap, speed_limit, dt)
            car.r -= car.velocity * dt

            if car.r <= stop_r:
                can_enter = _can_enter(car, circle_cars, radius, min_entry_gap,
                                       reaction_time, capacity_gap)
                if can_enter:
                    car.state = "circle"
                    car.r = radius
                    car.angle = arm_angle(car.arm)
                    car.velocity = max(0.6, min(car.velocity, circle_vmax))
                    car.entry_time = t
                    circle_cars.append(car)
                else:
                    car.r = stop_r
                    car.velocity = 0.0


def _update_circle(cars, t, dt, radius, circle_vmax, circle_follow_gap):
    circle_cars = [c for c in cars if c.state == "circle"]
    if not circle_cars:
        return

    circle_cars.sort(key=lambda c: c.angle % TWOPI)
    gaps = {}
    if len(circle_cars) == 1:
        gaps[circle_cars[0].car_id] = None
    else:
        for i, car in enumerate(circle_cars):
            front = circle_cars[(i + 1) % len(circle_cars)]
            arc_gap = radius * ((front.angle - car.angle) % TWOPI) - car.car_length
            gaps[car.car_id] = max(0.0, arc_gap)

    for car in circle_cars:
        car.cruise_control(gaps[car.car_id], circle_vmax, dt)
        if gaps[car.car_id] is not None and gaps[car.car_id] < circle_follow_gap:
            car.brake(gaps[car.car_id], dt)

    for car in list(circle_cars):
        old_angle = car.angle % TWOPI
        car.angle = (car.angle + car.velocity * dt / radius) % TWOPI
        target = arm_angle(car.exit_arm)
        if passed_angle(old_angle, car.angle, target):
            car.state = "exit"
            car.r = radius
            car.angle = target
            car.exit_time = t
            car.velocity = max(0.6, min(car.velocity, circle_vmax))


def run_roundabout_sim(spawn_rate_H: float = 0.08, spawn_rate_V: float = 0.08,
                       spawn_rates=None,
                       tmax: float = 220.0, warmup: float = 50.0, dt: float = 0.1,
                       seed: int = 0,
                       radius: float = 15.0, road_length: float = 95.0,
                       exit_length: float = 35.0,
                       road_vmax: float = 11.0, circle_vmax: float = 5.5,
                       min_entry_gap: float = 8.0, reaction_time: float = 1.2,
                       circle_follow_gap: float = 7.5, capacity_gap: float = 7.0,
                       min_spawn_gap: float = 10.0, random_dest: bool = False,
                       record: bool = False, record_stride: int = 5) -> dict:
    rng = np.random.default_rng(seed)
    rates = spawn_rates_by_arm(spawn_rate_H, spawn_rate_V, spawn_rates)
    stop_buffer = 2.0
    finish_r = radius + exit_length

    cars: List[Vehicle] = []
    active_history: List[int] = []
    frames: List[dict] = []
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
                        color=ROUNDABOUT_COLORS[arm],
                    )
                    cars.append(car)
                    next_id += 1

        _update_approach(cars, t, dt, radius, road_vmax, circle_vmax,
                         min_entry_gap, reaction_time, stop_buffer, capacity_gap)
        _update_circle(cars, t, dt, radius, circle_vmax, circle_follow_gap)
        update_exits(cars, t, dt, road_vmax, finish_r)

        active_history.append(sum(c.state != "done" for c in cars))
        if record and step % record_stride == 0:
            frames.append(record_frame(cars, t, radius, mode="roundabout"))

    out = summarize_result(cars, active_history, tmax, warmup)
    out.update({
        "kind": "roundabout",
        "frames": frames,
        "radius": radius,
        "road_length": road_length,
        "finish_r": finish_r,
        "spawn_rates": rates,
        "tmax": tmax,
        "warmup": warmup,
        "dt": dt,
        "random_dest": random_dest,
    })
    return out
