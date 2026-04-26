import math
import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyArrow

from sim_core import Lane, Signal


GRASS = "#9bc78a"
ASPHALT = "#3b3b3b"
EDGE = "#d9d9d9"
CENTER = "#f1c40f"
STOP_LINE = "#ffffff"


def draw_intersection(ax, road_w=24.0, span=230.0):
    ax.add_patch(Rectangle((-span, -span), 2 * span, 2 * span,
                           facecolor=GRASS, edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((-span, -road_w / 2), 2 * span, road_w,
                           facecolor=ASPHALT, edgecolor="none", zorder=1))
    ax.add_patch(Rectangle((-road_w / 2, -span), road_w, 2 * span,
                           facecolor=ASPHALT, edgecolor="none", zorder=1))
    ax.plot([-span, span], [road_w / 2, road_w / 2], color=EDGE, lw=1.0, zorder=2)
    ax.plot([-span, span], [-road_w / 2, -road_w / 2], color=EDGE, lw=1.0, zorder=2)
    ax.plot([road_w / 2, road_w / 2], [-span, span], color=EDGE, lw=1.0, zorder=2)
    ax.plot([-road_w / 2, -road_w / 2], [-span, span], color=EDGE, lw=1.0, zorder=2)
    for x0 in np.arange(-span, span, 16):
        if abs(x0 + 8) > road_w / 2:
            ax.plot([x0, x0 + 8], [0, 0], color=CENTER, lw=1.5, zorder=2)
    for y0 in np.arange(-span, span, 16):
        if abs(y0 + 8) > road_w / 2:
            ax.plot([0, 0], [y0, y0 + 8], color=CENTER, lw=1.5, zorder=2)
    ax.plot([-road_w / 2, road_w / 2], [-road_w / 2, -road_w / 2],
            color=STOP_LINE, lw=3, zorder=3)
    ax.plot([-road_w / 2, road_w / 2], [road_w / 2, road_w / 2],
            color=STOP_LINE, lw=3, zorder=3)
    ax.plot([-road_w / 2, -road_w / 2], [-road_w / 2, road_w / 2],
            color=STOP_LINE, lw=3, zorder=3)
    ax.plot([road_w / 2, road_w / 2], [-road_w / 2, road_w / 2],
            color=STOP_LINE, lw=3, zorder=3)


def car_rect(ax, x, y, orientation, color, w=8, l=14):
    if orientation == "h":
        ax.add_patch(Rectangle((x - l / 2, y - w / 2), l, w,
                               facecolor=color, edgecolor="black", lw=0.8, zorder=4))
    else:
        ax.add_patch(Rectangle((x - w / 2, y - l / 2), w, l,
                               facecolor=color, edgecolor="black", lw=0.8, zorder=4))


def draw_signal(ax, h_red, v_red):
    ax.add_patch(Rectangle((-22, -22), 44, 44, facecolor="#222",
                           edgecolor="black", lw=1.2, zorder=5))
    ax.add_patch(plt.Circle((-10, 0), 6,
                            facecolor=("#e74c3c" if h_red else "#2ecc71"),
                            edgecolor="black", lw=0.8, zorder=6))
    ax.add_patch(plt.Circle((10, 0), 6,
                            facecolor=("#e74c3c" if v_red else "#2ecc71"),
                            edgecolor="black", lw=0.8, zorder=6))
    ax.text(-10, -16, "H", color="white", ha="center", fontsize=8, zorder=6)
    ax.text(10, -16, "V", color="white", ha="center", fontsize=8, zorder=6)


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

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.set_xlim(-230, 230)
    ax.set_ylim(-230, 230)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    draw_intersection(ax)

    snap_idx = -1
    t_show = ts[snap_idx]
    for x in snaps_h[snap_idx]:
        car_rect(ax, x, -6, "h", "#1f3a93")
    for y in snaps_v[snap_idx]:
        car_rect(ax, 6, y, "v", "#e67e22")

    h_red = sig_h.red(t_show)
    v_red = sig_v.red(t_show)
    draw_signal(ax, h_red, v_red)

    ax.annotate("", xy=(-160, -32), xytext=(-200, -32),
                arrowprops=dict(arrowstyle="-|>", color="white", lw=2))
    ax.annotate("", xy=(32, -160), xytext=(32, -200),
                arrowprops=dict(arrowstyle="-|>", color="white", lw=2))
    ax.text(-180, -42, "H flow", color="white", fontsize=10)
    ax.text(40, -180, "V flow", color="white", fontsize=10, rotation=90)

    ax.set_title(f"Crossroads with opposing-phase traffic lights "
                 f"(t = {t_show:.0f} s, H={'R' if h_red else 'G'}, V={'R' if v_red else 'G'})",
                 fontsize=12)
    plt.tight_layout()
    plt.savefig("../figures/fig_step3_intersection_lights.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
