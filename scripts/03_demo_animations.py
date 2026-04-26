"""Side-by-side roundabout vs traffic-light demo, plus saved .mp4 movies.

Records a moderate-traffic run for each intersection type, exports a snapshot
figure, and saves both animations. Pass ``--quick`` to skip the .mp4 export
when you just want the snapshot figure.
"""

from _setup import FIGURES_DIR, GLOBAL_SEED, quick_mode

import matplotlib.pyplot as plt

from trafficsim import (
    animate_result,
    draw_base_roads,
    run_roundabout_sim,
    run_traffic_light_sim,
)


def main() -> None:
    quick = quick_mode()
    tmax = 60.0 if quick else 140.0

    rdb = run_roundabout_sim(
        spawn_rate_H=0.12, spawn_rate_V=0.08,
        tmax=tmax, warmup=20.0, seed=GLOBAL_SEED,
        radius=15.0, record=True, record_stride=3,
    )
    light = run_traffic_light_sim(
        spawn_rate_H=0.12, spawn_rate_V=0.08,
        tmax=tmax, warmup=20.0, seed=GLOBAL_SEED,
        radius=15.0, cycle=40.0, record=True, record_stride=3,
    )

    print("Roundabout demo")
    print(f"  spawned={rdb['n_spawned']} finished={rdb['n_finished']}"
          f" measured={rdb['n_measured']}")
    print(f"  mean total={rdb['mean_all']:.2f} s, mean wait={rdb['mean_wait']:.2f} s,"
          f" flow={rdb['flow']:.3f} cars/s")

    print("Traffic-light demo")
    print(f"  spawned={light['n_spawned']} finished={light['n_finished']}"
          f" measured={light['n_measured']}")
    print(f"  mean total={light['mean_all']:.2f} s, mean wait={light['mean_wait']:.2f} s,"
          f" flow={light['flow']:.3f} cars/s")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    for ax, result, label in zip(axes, [rdb, light],
                                 ["Roundabout", "Traffic Light"]):
        frame = result["frames"][len(result["frames"]) // 2]
        draw_base_roads(ax, radius=result["radius"],
                        extent=result["road_length"] + 8,
                        kind=result["kind"], phase=frame.get("phase"))
        for item in frame["cars"]:
            ax.plot(item["x"], item["y"], "o", ms=6.8,
                    color=item["color"], zorder=10)
        ax.set_title(label)

    plt.suptitle("Figure 3 -- Example traffic states", fontweight="bold")
    plt.tight_layout()
    snap = FIGURES_DIR / "fig3_example_states.png"
    plt.savefig(snap, bbox_inches="tight")
    plt.close(fig)
    print("saved", snap)

    if not quick:
        animate_result(rdb, save_name="movie_roundabout.mp4",
                       output_dir=FIGURES_DIR)
        animate_result(light, save_name="movie_traffic_light.mp4",
                       output_dir=FIGURES_DIR)


if __name__ == "__main__":
    main()
