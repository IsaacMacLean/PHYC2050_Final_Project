"""Drawing and animation helpers shared by the scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Rectangle


def draw_base_roads(ax, radius: float = 15.0, extent: float = 105.0,
                    road_width: float = 10.0, kind: str = "roundabout",
                    phase: Optional[str] = None) -> None:
    ax.add_patch(Rectangle((-extent, -road_width / 2), 2 * extent, road_width,
                           facecolor="lightgray", edgecolor="none", alpha=0.6, zorder=0))
    ax.add_patch(Rectangle((-road_width / 2, -extent), road_width, 2 * extent,
                           facecolor="lightgray", edgecolor="none", alpha=0.6, zorder=0))

    ring_half_width = road_width / 4.0
    gap = radius + ring_half_width

    ax.plot([-extent, -gap], [0, 0], linestyle="--", color="dimgray", lw=1.5,
            dashes=(6, 6), zorder=1)
    ax.plot([gap, extent], [0, 0], linestyle="--", color="dimgray", lw=1.5,
            dashes=(6, 6), zorder=1)
    ax.plot([0, 0], [-extent, -gap], linestyle="--", color="dimgray", lw=1.5,
            dashes=(6, 6), zorder=1)
    ax.plot([0, 0], [gap, extent], linestyle="--", color="dimgray", lw=1.5,
            dashes=(6, 6), zorder=1)

    if kind == "roundabout":
        ax.add_patch(Circle((0, 0), radius + ring_half_width, facecolor="gray",
                            edgecolor="none", alpha=0.9, zorder=2))
        ax.add_patch(Circle((0, 0), max(radius - ring_half_width, 0.5),
                            facecolor="silver", edgecolor="none", alpha=1.0, zorder=3))
        ax.add_patch(Circle((0, 0), radius, fill=False, edgecolor="dimgray",
                            lw=2, zorder=4))
    else:
        ax.add_patch(Rectangle((-radius, -radius), 2 * radius, 2 * radius,
                               facecolor="gray", edgecolor="dimgray",
                               alpha=0.55, lw=1.0, zorder=2))
        h_color = "green" if phase == "H" else "red"
        v_color = "green" if phase == "V" else "red"
        ax.scatter([radius + 7, -radius - 7], [radius + 7, -radius - 7], s=90,
                   c=[h_color, h_color], edgecolors="k", zorder=5)
        ax.scatter([-radius - 7, radius + 7], [radius + 7, -radius - 7], s=90,
                   c=[v_color, v_color], edgecolors="k", zorder=5)

    ax.set_aspect("equal")
    ax.set_xlim(-extent, extent)
    ax.set_ylim(-extent, extent)
    ax.grid(False)


def plot_frame(result: dict, frame_index: int = -1, title: Optional[str] = None):
    frames = result.get("frames", [])
    if not frames:
        raise ValueError("result does not contain recorded frames; run with record=True")
    frame = frames[frame_index]
    radius = result["radius"]
    extent = result["road_length"] + 8.0
    fig, ax = plt.subplots(figsize=(7, 7))
    draw_base_roads(ax, radius=radius, extent=extent, kind=result["kind"],
                    phase=frame.get("phase"))
    for item in frame["cars"]:
        ax.plot(item["x"], item["y"], "o", ms=6.8, color=item["color"], zorder=10)
    ax.set_title(title or f"{result['kind']} frame at t={frame['time']:.1f} s")
    plt.tight_layout()
    return fig, ax


def animate_roundabout(result: dict, interval: int = 30, max_frames: int = 320):
    frames = result.get("frames", [])
    if not frames:
        raise ValueError("result does not contain recorded frames; run with record=True")

    if len(frames) > max_frames:
        keep = np.linspace(0, len(frames) - 1, max_frames).astype(int)
        frames = [frames[i] for i in keep]

    radius = result["radius"]
    extent = result["road_length"] + 8.0
    fig, ax = plt.subplots(figsize=(8, 8))
    draw_base_roads(ax, radius=radius, extent=extent, kind="roundabout")

    max_cars = max((len(frame["cars"]) for frame in frames), default=0)
    car_dots = [ax.plot([], [], "o", ms=8, zorder=10)[0] for _ in range(max_cars)]

    def init():
        for dot in car_dots:
            dot.set_data([], [])
            dot.set_alpha(0.0)
        return car_dots

    def update(i):
        frame = frames[i]
        for dot in car_dots:
            dot.set_data([], [])
            dot.set_alpha(0.0)
        for dot, item in zip(car_dots, frame["cars"]):
            dot.set_data([item["x"]], [item["y"]])
            dot.set_color(item["color"])
            dot.set_alpha(1.0)
        ax.set_title(f"Animated Roundabout Simulation, t = {frame['time']:.1f} s")
        return car_dots

    ani = FuncAnimation(fig, update, frames=len(frames), init_func=init,
                        interval=interval, blit=True)
    plt.close(fig)
    return ani


def animate_result(result: dict, interval: int = 35, max_frames: int = 300,
                   save_name: Optional[str] = None,
                   output_dir: Optional[Path] = None):
    frames = result.get("frames", [])
    if not frames:
        raise ValueError("result does not contain recorded frames; run with record=True")

    if result["kind"] == "roundabout":
        ani = animate_roundabout(result, interval=interval, max_frames=max_frames)
    else:
        if len(frames) > max_frames:
            keep = np.linspace(0, len(frames) - 1, max_frames).astype(int)
            frames = [frames[i] for i in keep]
        radius = result["radius"]
        extent = result["road_length"] + 8.0
        fig, ax = plt.subplots(figsize=(8, 8))

        def update(i):
            frame = frames[i]
            ax.clear()
            draw_base_roads(ax, radius=radius, extent=extent, kind=result["kind"],
                            phase=frame.get("phase"))
            for item in frame["cars"]:
                ax.plot(item["x"], item["y"], "o", ms=7, color=item["color"], zorder=10)
            phase_text = (f", phase = {frame.get('phase')}"
                          if frame.get("phase") is not None else "")
            ax.set_title(f"{result['kind']} t = {frame['time']:.1f} s{phase_text}")
            return []

        ani = FuncAnimation(fig, update, frames=len(frames), interval=interval, blit=False)
        plt.close(fig)

    if save_name is not None:
        output_dir = Path(output_dir) if output_dir is not None else Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / save_name
        ani.save(path, fps=max(1, int(1000 / interval)), dpi=150)
        print("saved", path.resolve())

    return ani
