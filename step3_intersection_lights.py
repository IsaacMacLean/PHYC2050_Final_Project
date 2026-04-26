import random
import matplotlib.pyplot as plt

from sim_core import Lane, Signal


def main():
    random.seed(7)
    dt = 0.01
    T = 90.0
    period = 20.0
    n = int(T / dt)

    sig_h = Signal(loc=0.0, period=period, offset=0.0)
    sig_v = Signal(loc=0.0, period=period, offset=period / 2)
    lane_h = Lane(signal=sig_h, entry_s=-200.0, exit_s=200.0)
    lane_v = Lane(signal=sig_v, entry_s=-200.0, exit_s=200.0)

    snaps_h, snaps_v, ts = [], [], []
    for i in range(n):
        t = i * dt
        lane_h.try_spawn(t, dt, rate=0.4)
        lane_v.try_spawn(t, dt, rate=0.4)
        lane_h.step(t, dt)
        lane_v.step(t, dt)
        if i % 30 == 0:
            ts.append(t)
            snaps_h.append(lane_h.positions)
            snaps_v.append(lane_v.positions)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-220, 220)
    ax.set_ylim(-220, 220)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.axhline(0, color="lightgray", lw=10, zorder=0)
    ax.axvline(0, color="lightgray", lw=10, zorder=0)

    snap_idx = -1
    xs_h = snaps_h[snap_idx]
    ys_v = snaps_v[snap_idx]
    ax.scatter(xs_h, [0] * len(xs_h), s=80, color="navy", edgecolor="white", label="horizontal cars")
    ax.scatter([0] * len(ys_v), ys_v, s=80, color="darkorange", edgecolor="white", label="vertical cars")

    t_show = ts[snap_idx]
    h_red = sig_h.red(t_show)
    v_red = sig_v.red(t_show)
    ax.scatter([0], [0], s=400,
               color=("crimson" if h_red else "limegreen"),
               edgecolor="black", zorder=5,
               label=f"signal H={'R' if h_red else 'G'} V={'R' if v_red else 'G'}")
    ax.set_title(f"Crossroads with opposing-phase lights, snapshot at t = {t_show:.1f} s")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig("fig_step3_intersection_lights.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
