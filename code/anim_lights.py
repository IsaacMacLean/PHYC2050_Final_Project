import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, FFMpegWriter

from sim_core import Lane, Signal
from step3_intersection_lights import draw_intersection, draw_signal, car_rect


def main():
    random.seed(7)
    dt = 0.05
    T = 90.0
    period = 20.0
    n = int(T / dt)
    lane_off = 6.0
    record_every = 4

    sig_h = Signal(loc=0.0, period=period, offset=0.0)
    sig_v = Signal(loc=0.0, period=period, offset=period / 2)
    lane_e = Lane(signal=sig_h, entry_s=-200.0, exit_s=200.0)
    lane_w = Lane(signal=sig_h, entry_s=-200.0, exit_s=200.0)
    lane_n = Lane(signal=sig_v, entry_s=-200.0, exit_s=200.0)
    lane_s = Lane(signal=sig_v, entry_s=-200.0, exit_s=200.0)

    snaps = []
    for i in range(n):
        t = i * dt
        for ln in (lane_e, lane_w, lane_n, lane_s):
            ln.try_spawn(t, dt, rate=0.4)
            ln.step(t, dt)
        if i % record_every == 0:
            snaps.append({
                "t": t,
                "e": list(lane_e.positions),
                "w": list(lane_w.positions),
                "n": list(lane_n.positions),
                "s": list(lane_s.positions),
                "h_red": sig_h.red(t),
                "v_red": sig_v.red(t),
            })

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.set_xlim(-230, 230); ax.set_ylim(-230, 230)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    draw_intersection(ax)
    title = ax.set_title("", fontsize=12)

    def update(idx):
        for p in list(ax.patches):
            if p.get_zorder() in (4, 5, 6):
                p.remove()
        for txt in [t for t in ax.texts if t.get_zorder() == 6]:
            txt.remove()
        snap = snaps[idx]
        for s in snap["e"]:
            car_rect(ax, s, -lane_off, "h", "#1f3a93")
        for s in snap["w"]:
            car_rect(ax, -s, lane_off, "h", "#2e86c1")
        for s in snap["n"]:
            car_rect(ax, lane_off, s, "v", "#e67e22")
        for s in snap["s"]:
            car_rect(ax, -lane_off, -s, "v", "#d35400")
        draw_signal(ax, snap["h_red"], snap["v_red"])
        title.set_text(f"Crossroads with traffic lights "
                       f"(t = {snap['t']:.0f} s, "
                       f"H={'R' if snap['h_red'] else 'G'}, "
                       f"V={'R' if snap['v_red'] else 'G'})")
        return []

    anim = FuncAnimation(fig, update, frames=len(snaps), interval=50, blit=False)
    writer = FFMpegWriter(
        fps=20, bitrate=2400,
        extra_args=["-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-pix_fmt", "yuv420p"],
    )
    anim.save("../animations/lights.mp4", writer=writer, dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
