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


def draw_intersection(ax, road_w=24.0, span=230.0, turn_len=70.0):
    half = road_w / 2
    ax.add_patch(Rectangle((-span, -span), 2 * span, 2 * span,
                           facecolor=GRASS, edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((-span, -half), 2 * span, road_w,
                           facecolor=ASPHALT, edgecolor="none", zorder=1))
    ax.add_patch(Rectangle((-half, -span), road_w, 2 * span,
                           facecolor=ASPHALT, edgecolor="none", zorder=1))

    ax.plot([-span, span], [half, half], color=EDGE, lw=1.0, zorder=2)
    ax.plot([-span, span], [-half, -half], color=EDGE, lw=1.0, zorder=2)
    ax.plot([half, half], [-span, span], color=EDGE, lw=1.0, zorder=2)
    ax.plot([-half, -half], [-span, span], color=EDGE, lw=1.0, zorder=2)

    for x0 in np.arange(-span, -half - turn_len, 16):
        ax.plot([x0, x0 + 8], [0, 0], color=CENTER, lw=1.5, zorder=2)
    for x0 in np.arange(half + turn_len, span, 16):
        ax.plot([x0, x0 + 8], [0, 0], color=CENTER, lw=1.5, zorder=2)
    for y0 in np.arange(-span, -half - turn_len, 16):
        ax.plot([0, 0], [y0, y0 + 8], color=CENTER, lw=1.5, zorder=2)
    for y0 in np.arange(half + turn_len, span, 16):
        ax.plot([0, 0], [y0, y0 + 8], color=CENTER, lw=1.5, zorder=2)

    ax.plot([-half - turn_len, -half], [0, 0], color=CENTER, lw=2.0, zorder=2)
    ax.plot([half, half + turn_len], [0, 0], color=CENTER, lw=2.0, zorder=2)
    ax.plot([0, 0], [-half - turn_len, -half], color=CENTER, lw=2.0, zorder=2)
    ax.plot([0, 0], [half, half + turn_len], color=CENTER, lw=2.0, zorder=2)

    ax.plot([-half - turn_len, -half], [-half / 2, -half / 2],
            color=STOP_LINE, lw=1.6, zorder=2)
    ax.plot([half, half + turn_len], [half / 2, half / 2],
            color=STOP_LINE, lw=1.6, zorder=2)
    ax.plot([half / 2, half / 2], [-half - turn_len, -half],
            color=STOP_LINE, lw=1.6, zorder=2)
    ax.plot([-half / 2, -half / 2], [half, half + turn_len],
            color=STOP_LINE, lw=1.6, zorder=2)

    arrow_kw = dict(width=1.4, head_width=4.0, head_length=4.0,
                    facecolor=STOP_LINE, edgecolor="none",
                    zorder=3, length_includes_head=True)
    ax.add_patch(FancyArrow(-half - turn_len / 2, -3.5, 0, 7, **arrow_kw))
    ax.add_patch(FancyArrow(half + turn_len / 2, 3.5, 0, -7, **arrow_kw))
    ax.add_patch(FancyArrow(3.5, -half - turn_len / 2, -7, 0, **arrow_kw))
    ax.add_patch(FancyArrow(-3.5, half + turn_len / 2, 7, 0, **arrow_kw))

    ax.plot([-half, half], [-half, -half], color=STOP_LINE, lw=3, zorder=3)
    ax.plot([-half, half], [half, half], color=STOP_LINE, lw=3, zorder=3)
    ax.plot([-half, -half], [-half, half], color=STOP_LINE, lw=3, zorder=3)
    ax.plot([half, half], [-half, half], color=STOP_LINE, lw=3, zorder=3)


def car_rect(ax, x, y, orientation, color, w=5, l=10):
    if orientation == "h":
        ax.add_patch(Rectangle((x - l / 2, y - w / 2), l, w,
                               facecolor=color, edgecolor="black", lw=0.7, zorder=4))
    else:
        ax.add_patch(Rectangle((x - w / 2, y - l / 2), w, l,
                               facecolor=color, edgecolor="black", lw=0.7, zorder=4))


def draw_signal(ax, h_red, v_red):
    ax.add_patch(Rectangle((-15, -10), 30, 20, facecolor="#1c1c1c",
                           edgecolor="black", lw=1.4, zorder=5))
    ax.add_patch(plt.Circle((-7.5, 1.5), 4.2,
                            facecolor=("#e74c3c" if h_red else "#2ecc71"),
                            edgecolor="black", lw=0.8, zorder=6))
    ax.add_patch(plt.Circle((7.5, 1.5), 4.2,
                            facecolor=("#e74c3c" if v_red else "#2ecc71"),
                            edgecolor="black", lw=0.8, zorder=6))
    ax.text(-7.5, -6.5, "H", color="white", ha="center",
            fontsize=11, fontweight="bold", zorder=6)
    ax.text(7.5, -6.5, "V", color="white", ha="center",
            fontsize=11, fontweight="bold", zorder=6)


def main():
    random.seed(7)
    dt = 0.01
    T = 160.0
    period = 40.0
    n = int(T / dt)
    lane_off = 8.0

    sig_h = Signal(loc=-12.0, period=period, offset=0.0)
    sig_v = Signal(loc=-12.0, period=period, offset=period / 2)
    lane_e = Lane(signal=sig_h, entry_s=-200.0, exit_s=200.0)
    lane_w = Lane(signal=sig_h, entry_s=-200.0, exit_s=200.0)
    lane_n = Lane(signal=sig_v, entry_s=-200.0, exit_s=200.0)
    lane_s = Lane(signal=sig_v, entry_s=-200.0, exit_s=200.0)

    snaps_e, snaps_w, snaps_n, snaps_s, ts = [], [], [], [], []
    for i in range(n):
        t = i * dt
        for ln in (lane_e, lane_w, lane_n, lane_s):
            ln.try_spawn(t, dt, rate=0.25)
            ln.step(t, dt)
        if i % 30 == 0:
            ts.append(t)
            snaps_e.append(lane_e.positions)
            snaps_w.append(lane_w.positions)
            snaps_n.append(lane_n.positions)
            snaps_s.append(lane_s.positions)

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.set_xlim(-230, 230)
    ax.set_ylim(-230, 230)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    draw_intersection(ax)

    snap_idx = -1
    t_show = ts[snap_idx]
    for s in snaps_e[snap_idx]:
        car_rect(ax, s, -lane_off, "h", "#1f3a93")
    for s in snaps_w[snap_idx]:
        car_rect(ax, -s, lane_off, "h", "#2e86c1")
    for s in snaps_n[snap_idx]:
        car_rect(ax, lane_off, s, "v", "#e67e22")
    for s in snaps_s[snap_idx]:
        car_rect(ax, -lane_off, -s, "v", "#d35400")

    h_red = sig_h.red(t_show)
    v_red = sig_v.red(t_show)
    draw_signal(ax, h_red, v_red)

    ax.annotate("", xy=(-160, -34), xytext=(-200, -34),
                arrowprops=dict(arrowstyle="-|>", color="white", lw=2))
    ax.annotate("", xy=(34, -160), xytext=(34, -200),
                arrowprops=dict(arrowstyle="-|>", color="white", lw=2))
    ax.text(-180, -44, "H flow", color="white", fontsize=10)
    ax.text(42, -180, "V flow", color="white", fontsize=10, rotation=90)

    ax.set_title(f"Crossroads with opposing-phase traffic lights "
                 f"(t = {t_show:.0f} s, H={'R' if h_red else 'G'}, V={'R' if v_red else 'G'})",
                 fontsize=12)
    plt.tight_layout()
    plt.savefig("../figures/fig_step3_intersection_lights.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
