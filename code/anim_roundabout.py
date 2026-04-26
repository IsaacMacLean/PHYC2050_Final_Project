import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, FFMpegWriter

from round_core import run_roundabout_sim, ARM_COLORS
from step4_roundabout_demo import draw_base_roads


def main():
    out = run_roundabout_sim(
        rate_h=0.10, rate_v=0.10, opposite=True,
        T=180.0, dt=0.1, seed=3,
        record=True, record_stride=2,
    )
    radius = out["radius"]
    extent = out["road_length"] + 8.0
    frames = out["frames"]

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.set_aspect("equal")
    ax.set_xlim(-extent, extent)
    ax.set_ylim(-extent, extent)
    ax.set_xticks([]); ax.set_yticks([])
    draw_base_roads(ax, radius=radius, extent=extent)

    handles = []
    for arm in range(4):
        h = ax.scatter([], [], s=70, c=ARM_COLORS[arm], edgecolor="black", lw=0.6,
                       label=f"arm {arm} ({['E', 'N', 'W', 'S'][arm]})")
        handles.append(h)
    ax.legend(handles=handles, loc="upper right", fontsize=9, framealpha=0.85)

    scat = ax.scatter([], [], s=70, edgecolor="black", lw=0.6, zorder=10)
    title = ax.set_title("", fontsize=12)

    lane_offset = 2.5

    def update(idx):
        snap = frames[idx]
        xs, ys, cs = [], [], []
        for c in snap["cars"]:
            x, y = c["x"], c["y"]
            theta = c.get("theta", math.atan2(y, x))
            nx, ny = -math.sin(theta), math.cos(theta)
            if c["state"] == "approach":
                x += lane_offset * nx; y += lane_offset * ny
            elif c["state"] == "exit":
                x -= lane_offset * nx; y -= lane_offset * ny
            xs.append(x); ys.append(y); cs.append(c["color"])
        if xs:
            scat.set_offsets(np.column_stack([xs, ys]))
            scat.set_facecolors(cs)
        else:
            scat.set_offsets(np.empty((0, 2)))
        title.set_text(f"Four-arm roundabout (t = {snap['time']:.0f} s)")
        return scat, title

    anim = FuncAnimation(fig, update, frames=len(frames), interval=40, blit=False)
    writer = FFMpegWriter(
        fps=25, bitrate=2400,
        extra_args=["-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-pix_fmt", "yuv420p"],
    )
    anim.save("../animations/roundabout.mp4", writer=writer, dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
