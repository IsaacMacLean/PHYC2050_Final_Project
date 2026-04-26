import math
import random
import matplotlib.pyplot as plt
import numpy as np

from round_core import RoundaboutSim


def main():
    random.seed(3)
    dt = 0.05
    T = 80.0
    n = int(T / dt)

    sim = RoundaboutSim(radius=20.0, arm_len=200.0, ring_speed=9.0,
                        yield_threshold=math.pi / 3)

    snapshots = []
    snap_times = []
    for i in range(n):
        t = i * dt
        sim.step(t, dt, rate_h=0.4, rate_v=0.4)
        if i % 20 == 0:
            snapshots.append(sim.positions_xy())
            snap_times.append(t)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-230, 230)
    ax.set_ylim(-230, 230)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")

    ax.axhline(0, color="lightgray", lw=10, zorder=0)
    ax.axvline(0, color="lightgray", lw=10, zorder=0)

    theta_circle = np.linspace(0, 2 * math.pi, 200)
    R = sim.radius
    ax.plot(R * np.cos(theta_circle), R * np.sin(theta_circle), color="black", lw=1.5)
    ax.fill(R * np.cos(theta_circle), R * np.sin(theta_circle),
            color="seagreen", alpha=0.15)

    snap = snapshots[-1]
    if snap['h_in']:
        xs, ys = zip(*snap['h_in'])
        ax.scatter(xs, ys, s=70, color="navy", edgecolor="white", label="H entering")
    if snap['v_in']:
        xs, ys = zip(*snap['v_in'])
        ax.scatter(xs, ys, s=70, color="darkorange", edgecolor="white", label="V entering")
    if snap['h_out']:
        xs, ys = zip(*snap['h_out'])
        ax.scatter(xs, ys, s=70, color="royalblue", edgecolor="white", label="H exiting")
    if snap['v_out']:
        xs, ys = zip(*snap['v_out'])
        ax.scatter(xs, ys, s=70, color="goldenrod", edgecolor="white", label="V exiting")
    if snap['ring_x']:
        ax.scatter(snap['ring_x'], snap['ring_y'], s=90, color="firebrick",
                   edgecolor="white", label="in ring")

    ax.set_title(f"Roundabout snapshot at t = {snap_times[-1]:.1f} s "
                 f"(H rate = V rate = 0.4 cars/s)")
    ax.legend(loc="upper right", fontsize=9)
    plt.tight_layout()
    plt.savefig("fig_step4_roundabout.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
