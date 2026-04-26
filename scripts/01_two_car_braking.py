"""Two-car braking check (project hint #3).

The follower must avoid colliding with the leader during a hard stop and then
resume normal cruise speed once the leader moves again. This sanity-checks
that the car-following physics behaves intuitively before we drop hundreds of
cars into the intersection sims.
"""

from _setup import FIGURES_DIR

import numpy as np
import matplotlib.pyplot as plt

from trafficsim import Vehicle


def run(tmax: float = 35.0, dt: float = 0.05, vmax: float = 11.0) -> dict:
    leader = Vehicle(0, arm=0, exit_arm=2, spawn_time=0.0,
                     r=40.0, angle=0.0, velocity=8.0, color="tab:orange")
    follower = Vehicle(1, arm=0, exit_arm=2, spawn_time=0.0,
                       r=10.0, angle=0.0, velocity=8.0, color="tab:blue")

    times, leader_x, follower_x, gaps, follower_v = [], [], [], [], []
    for step in range(int(tmax / dt)):
        t = step * dt

        # Force the leader into a hard brake between t=8 and t=14 to test the
        # follower's reaction; otherwise it cruises at vmax.
        if 8.0 <= t <= 14.0:
            leader.brake(2.0, dt)
        else:
            leader.cruise_control(None, vmax, dt)
        leader.r += leader.velocity * dt

        gap = leader.r - follower.r - follower.car_length
        follower.cruise_control(gap, vmax, dt)
        follower.r += follower.velocity * dt

        times.append(t)
        leader_x.append(leader.r)
        follower_x.append(follower.r)
        gaps.append(gap)
        follower_v.append(follower.velocity)

    return {
        "time": np.array(times),
        "leader_x": np.array(leader_x),
        "follower_x": np.array(follower_x),
        "gap": np.array(gaps),
        "follower_v": np.array(follower_v),
    }


def main() -> None:
    data = run()

    fig, axes = plt.subplots(1, 3, figsize=(14, 3.8))
    axes[0].plot(data["time"], data["leader_x"], label="lead car")
    axes[0].plot(data["time"], data["follower_x"], label="following car")
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel("position (m)")
    axes[0].legend()

    axes[1].plot(data["time"], data["gap"], color="tab:red")
    axes[1].axhline(0, color="k", ls="--", lw=1)
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("bumper gap (m)")
    axes[1].set_title(f"minimum gap = {np.min(data['gap']):.2f} m")

    axes[2].plot(data["time"], data["follower_v"], color="tab:green")
    axes[2].set_xlabel("time (s)")
    axes[2].set_ylabel("follower speed (m/s)")

    plt.suptitle("Figure 1 -- Two-car braking check", fontweight="bold")
    plt.tight_layout()
    out = FIGURES_DIR / "fig1_two_car_braking.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("saved", out)


if __name__ == "__main__":
    main()
