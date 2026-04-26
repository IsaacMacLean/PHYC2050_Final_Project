"""Roundabout radius sensitivity -- analysis #9.

The radius changes both the path length around the circle and the storage
capacity (number of cars that fit on the ring). Larger circles take longer to
traverse but can absorb more entering traffic before locking up.
"""

from _setup import FIGURES_DIR, GLOBAL_SEED, quick_mode

import numpy as np
import matplotlib.pyplot as plt

from trafficsim import run_repeated, run_roundabout_sim


def main() -> None:
    quick = quick_mode()
    radii = [10.0, 15.0, 20.0, 25.0]
    if quick:
        radii = [10.0, 20.0]
    spawn_rates = np.array([0.02, 0.04, 0.06, 0.08, 0.10, 0.12])
    repeats = 2 if quick else 3
    tmax = 120.0 if quick else 240.0

    results = {}
    for rad in radii:
        means = np.full_like(spawn_rates, np.nan, dtype=float)
        flows = np.full_like(spawn_rates, np.nan, dtype=float)
        for i, rate in enumerate(spawn_rates):
            res = run_repeated(
                run_roundabout_sim, repeats=repeats,
                seed0=GLOBAL_SEED + 900 + int(rad) * 10 + i,
                spawn_rate_H=rate, spawn_rate_V=rate,
                tmax=tmax, warmup=tmax * 0.2,
                radius=rad,
            )
            means[i] = res["mean_all"]
            flows[i] = res["flow"]
        results[rad] = (means, flows)
        print(f"  radius={rad:.0f} m done")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    for rad, (means, flows) in results.items():
        axes[0].plot(spawn_rates, means, "o-", lw=1.8, label=f"R={rad:.0f} m")
        axes[1].plot(spawn_rates, flows, "o-", lw=1.8, label=f"R={rad:.0f} m")

    axes[0].set_xlabel("spawn rate (cars/s per arm)")
    axes[0].set_ylabel("mean passing time (s)")
    axes[0].set_title("Passing time")
    axes[0].legend()

    axes[1].set_xlabel("spawn rate (cars/s per arm)")
    axes[1].set_ylabel("throughput (cars/s)")
    axes[1].set_title("Completed flow")
    axes[1].legend()

    plt.suptitle("Figure 11 -- Sensitivity to roundabout radius",
                 fontweight="bold")
    plt.tight_layout()
    out = FIGURES_DIR / "fig11_radius_sensitivity.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("saved", out)

    np.savez(FIGURES_DIR / "data_radius_sensitivity.npz",
             radii=np.array(radii), spawn_rates=spawn_rates,
             means=np.array([results[r][0] for r in radii]),
             flows=np.array([results[r][1] for r in radii]))


if __name__ == "__main__":
    main()
