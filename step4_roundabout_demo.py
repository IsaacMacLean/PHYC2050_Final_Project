import math
import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

from round_core import RoundaboutSim


GRASS = "#9bc78a"
ISLAND = "#5d8a48"
ASPHALT = "#3b3b3b"
EDGE = "#d9d9d9"
CENTER = "#f1c40f"
STOP_LINE = "#ffffff"


def draw_roundabout(ax, R=20.0, ring_w=14.0, road_w=24.0, span=230.0):
    ax.add_patch(Rectangle((-span, -span), 2 * span, 2 * span,
                           facecolor=GRASS, edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((-span, -road_w / 2), 2 * span, road_w,
                           facecolor=ASPHALT, edgecolor="none", zorder=1))
    ax.add_patch(Rectangle((-road_w / 2, -span), road_w, 2 * span,
                           facecolor=ASPHALT, edgecolor="none", zorder=1))
    ax.add_patch(Circle((0, 0), R + ring_w / 2,
                        facecolor=ASPHALT, edgecolor="none", zorder=2))
    ax.add_patch(Circle((0, 0), R - ring_w / 2,
                        facecolor=ISLAND, edgecolor="black", lw=1.5, zorder=3))
    theta = np.linspace(0, 2 * math.pi, 200)
    ax.plot((R + ring_w / 2) * np.cos(theta), (R + ring_w / 2) * np.sin(theta),
            color=EDGE, lw=1.0, zorder=4)
    ax.plot((R - ring_w / 2) * np.cos(theta), (R - ring_w / 2) * np.sin(theta),
            color=EDGE, lw=1.0, zorder=4)
    for sign in (-1, 1):
        ax.plot([sign * (R + ring_w / 2), sign * span], [road_w / 2, road_w / 2],
                color=EDGE, lw=1.0, zorder=4)
        ax.plot([sign * (R + ring_w / 2), sign * span], [-road_w / 2, -road_w / 2],
                color=EDGE, lw=1.0, zorder=4)
        ax.plot([road_w / 2, road_w / 2], [sign * (R + ring_w / 2), sign * span],
                color=EDGE, lw=1.0, zorder=4)
        ax.plot([-road_w / 2, -road_w / 2], [sign * (R + ring_w / 2), sign * span],
                color=EDGE, lw=1.0, zorder=4)
    for x0 in np.arange(R + ring_w / 2 + 6, span, 16):
        ax.plot([x0, x0 + 8], [0, 0], color=CENTER, lw=1.5, zorder=4)
        ax.plot([-x0, -x0 - 8], [0, 0], color=CENTER, lw=1.5, zorder=4)
    for y0 in np.arange(R + ring_w / 2 + 6, span, 16):
        ax.plot([0, 0], [y0, y0 + 8], color=CENTER, lw=1.5, zorder=4)
        ax.plot([0, 0], [-y0, -y0 - 8], color=CENTER, lw=1.5, zorder=4)
    for ang_deg in (0, 90, 180, 270):
        ang = math.radians(ang_deg)
        sx = (R + ring_w / 2 + 1) * math.cos(ang)
        sy = (R + ring_w / 2 + 1) * math.sin(ang)
        if ang_deg in (0, 180):
            ax.plot([sx, sx], [-road_w / 2, road_w / 2], color=STOP_LINE, lw=3, zorder=5)
        else:
            ax.plot([-road_w / 2, road_w / 2], [sy, sy], color=STOP_LINE, lw=3, zorder=5)

    arr_R = R - ring_w / 2 - 5
    arrow = FancyArrowPatch((arr_R, 8), (-2, arr_R + 4),
                            connectionstyle="arc3,rad=0.6",
                            arrowstyle="-|>", mutation_scale=18,
                            color="#f6f6f6", lw=2, zorder=5)
    ax.add_patch(arrow)
    ax.text(0, 0, "yield to\nleft (CCW)", color="white", ha="center", va="center",
            fontsize=9, zorder=6)


def car_rect(ax, x, y, orientation, color, w=8, l=14):
    if orientation == "h":
        ax.add_patch(Rectangle((x - l / 2, y - w / 2), l, w,
                               facecolor=color, edgecolor="black", lw=0.8, zorder=6))
    else:
        ax.add_patch(Rectangle((x - w / 2, y - l / 2), w, l,
                               facecolor=color, edgecolor="black", lw=0.8, zorder=6))


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

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.set_xlim(-230, 230)
    ax.set_ylim(-230, 230)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    draw_roundabout(ax, R=sim.radius)

    snap = snapshots[-1]
    for x, y in snap['h_in']:
        car_rect(ax, x, -6, "h", "#1f3a93")
    for x, y in snap['v_in']:
        car_rect(ax, 6, y, "v", "#e67e22")
    for x, y in snap['h_out']:
        car_rect(ax, x, -6, "h", "#1f618d")
    for x, y in snap['v_out']:
        car_rect(ax, 6, y, "v", "#b7950b")
    for rx, ry in zip(snap['ring_x'], snap['ring_y']):
        ax.add_patch(plt.Circle((rx, ry), 5,
                                facecolor="#c0392b", edgecolor="black", lw=0.8, zorder=7))

    ax.set_title(f"Four-arm roundabout (t = {snap_times[-1]:.0f} s, "
                 f"H rate = V rate = 0.4 cars/s)", fontsize=12)
    plt.tight_layout()
    plt.savefig("fig_step4_roundabout.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
