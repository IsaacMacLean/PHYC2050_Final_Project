"""Shared simulation primitives used by both the roundabout and the
traffic-light models: arrival process, exit-road follow logic, frame recording,
and per-run summary statistics.
"""

from __future__ import annotations

from typing import Iterable, Optional

import numpy as np

from .vehicle import (
    Vehicle,
    arm_angle,
    finite_mean,
    finite_std,
    vehicle_xy,
    TWOPI,
)


def spawn_rates_by_arm(spawn_rate_H=None, spawn_rate_V=None, spawn_rates=None):
    if spawn_rates is not None:
        arr = np.asarray(spawn_rates, dtype=float)
        if arr.shape != (4,):
            raise ValueError("spawn_rates must contain four values, one for each arm")
        return arr
    if spawn_rate_H is None or spawn_rate_V is None:
        raise ValueError("provide spawn_rate_H and spawn_rate_V, or provide spawn_rates")
    return np.array([spawn_rate_H, spawn_rate_V, spawn_rate_H, spawn_rate_V], dtype=float)


def can_spawn(cars: Iterable[Vehicle], arm: int, spawn_r: float, min_spawn_gap: float) -> bool:
    same_arm = [c for c in cars if c.state == "approach" and c.arm == arm]
    if not same_arm:
        return True
    farthest_r = max(c.r for c in same_arm)
    return farthest_r < spawn_r - min_spawn_gap


def update_exits(cars: Iterable[Vehicle], t: float, dt: float, road_vmax: float, finish_r: float) -> None:
    for exit_arm in range(4):
        exiting = [c for c in cars if c.state == "exit" and c.exit_arm == exit_arm]
        exiting.sort(key=lambda c: c.r, reverse=True)
        for i, car in enumerate(exiting):
            gap = None if i == 0 else exiting[i - 1].r - car.r - car.car_length
            car.cruise_control(gap, road_vmax, dt)
            car.r += car.velocity * dt
            if car.r >= finish_r:
                car.state = "done"
                car.finish_time = t
                car.velocity = 0.0


def record_frame(cars: Iterable[Vehicle], t: float, radius: float,
                 mode: str = "roundabout") -> dict:
    frame = []
    for car in cars:
        if car.state == "done":
            continue
        x, y = vehicle_xy(car, radius=radius, mode=mode)
        frame.append({
            "x": x,
            "y": y,
            "state": car.state,
            "color": car.color,
            "arm": car.arm,
            "exit_arm": car.exit_arm,
            "id": car.car_id,
        })
    return {"time": t, "cars": frame}


def summarize_result(cars, active_history, tmax: float, warmup: float) -> dict:
    finished_after_warmup = [c for c in cars if c.finish_time is not None and c.finish_time >= warmup]
    measured = [c for c in finished_after_warmup if c.spawn_time >= warmup]

    if len(measured) < 3:
        measured = finished_after_warmup

    totals = np.array([c.total_time() for c in measured], dtype=float)
    waits = np.array([c.wait_time() for c in measured], dtype=float)
    h_totals = np.array([c.total_time() for c in measured if c.road_group() == "H"], dtype=float)
    v_totals = np.array([c.total_time() for c in measured if c.road_group() == "V"], dtype=float)

    by_arm = []
    for arm in range(4):
        arm_values = [c.total_time() for c in measured if c.arm == arm]
        by_arm.append(finite_mean(arm_values))

    measurement_time = max(tmax - warmup, 1e-9)
    flow = len(finished_after_warmup) / measurement_time
    density = finite_mean(active_history) / (4.0 * 100.0) if len(active_history) else float("nan")

    return {
        "cars": cars,
        "n_spawned": len(cars),
        "n_finished": sum(c.finish_time is not None for c in cars),
        "n_measured": len(measured),
        "mean_all": finite_mean(totals),
        "std_all": finite_std(totals),
        "mean_wait": finite_mean(waits),
        "mean_H": finite_mean(h_totals),
        "mean_V": finite_mean(v_totals),
        "bias_H_minus_V": finite_mean(h_totals) - finite_mean(v_totals),
        "mean_by_arm": np.array(by_arm),
        "flow": float(flow),
        "density": float(density),
        "total_times": totals,
        "wait_times": waits,
    }
