"""Line of cars passing a single pedestrian crossing (project hint #4).

This is the one-road, one-light warm-up before we glue four arms together.
The plot shows trajectories x(t) for each car so it is easy to see the
"queue forms while the light is red, discharges in waves when it goes green"
behaviour.
"""

from _setup import FIGURES_DIR

import numpy as np
import matplotlib.pyplot as plt

from trafficsim import Vehicle


def is_red(t: float, cycle: float) -> bool:
    return (t % cycle) < (cycle / 2.0)


def run(n_cars: int = 10, spacing: float = 18.0, vmax: float = 11.0,
        cycle: float = 18.0, tmax: float = 90.0, dt: float = 0.05,
        light_position: float = 0.0) -> dict:
    cars = [Vehicle(car_id=i, arm=0, exit_arm=2, spawn_time=0.0,
                    r=-200.0 + i * spacing, angle=0.0, velocity=vmax,
                    color="tab:blue")
            for i in range(n_cars)]

    times = []
    trajectory = []
    light_state = []
    n_steps = int(tmax / dt)
    for step in range(n_steps):
        t = step * dt
        red = is_red(t, cycle)
        # cars are sorted leader-to-tail; index 0 is at the back
        for i, car in enumerate(cars):
            front_x = cars[i + 1].r if i + 1 < len(cars) else None
            stop_block = (red and car.r < light_position
                          and (front_x is None or light_position < front_x))
            target = light_position if stop_block else front_x
            if target is None:
                car.cruise_control(None, vmax, dt)
            else:
                gap = target - car.r - car.car_length
                car.cruise_control(gap, vmax, dt)
            car.r += car.velocity * dt

        times.append(t)
        trajectory.append([c.r for c in cars])
        light_state.append("red" if red else "green")

    return {"time": np.array(times),
            "trajectory": np.array(trajectory),
            "light_state": light_state,
            "cycle": cycle}


def main() -> None:
    data = run()

    fig, ax = plt.subplots(figsize=(10, 5))
    for j in range(data["trajectory"].shape[1]):
        ax.plot(data["time"], data["trajectory"][:, j], lw=1.5, alpha=0.85)

    cycle = data["cycle"]
    tmax = data["time"][-1]
    n_periods = int(tmax / cycle) + 1
    for k in range(n_periods):
        red_start = k * cycle
        red_end = red_start + cycle / 2
        ax.axvspan(red_start, min(red_end, tmax), color="red", alpha=0.07)

    ax.axhline(0.0, color="k", ls="--", lw=1, label="stop line")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("position along road (m)")
    ax.set_title("Figure 2 -- Pedestrian-light queue discharge",
                 fontweight="bold")
    ax.legend(loc="lower right")
    plt.tight_layout()
    out = FIGURES_DIR / "fig2_pedestrian_light.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("saved", out)


if __name__ == "__main__":
    main()
