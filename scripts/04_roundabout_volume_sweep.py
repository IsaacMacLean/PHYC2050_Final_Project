"""Symmetric traffic-volume sweep for the roundabout (analyses #1 and #2).

Sweeps the spawn rate equally on every arm and reports the mean passing time,
mean wait at the yield line, and completed flow rate as a function of volume.
"""

from _setup import FIGURES_DIR, GLOBAL_SEED, quick_mode

import numpy as np
import matplotlib.pyplot as plt

from trafficsim import run_repeated, run_roundabout_sim


def main() -> None:
    quick = quick_mode()
    spawn_rates = np.array([0.02, 0.04, 0.06, 0.08, 0.10, 0.12])
    repeats = 2 if quick else 3
    tmax = 120.0 if quick else 240.0

    means = np.full_like(spawn_rates, np.nan, dtype=float)
    waits = np.full_like(spawn_rates, np.nan, dtype=float)
    flows = np.full_like(spawn_rates, np.nan, dtype=float)
    mean_err = np.full_like(spawn_rates, np.nan, dtype=float)
    flow_err = np.full_like(spawn_rates, np.nan, dtype=float)

    print("Symmetric roundabout sweep")
    for i, rate in enumerate(spawn_rates):
        res = run_repeated(
            run_roundabout_sim, repeats=repeats, seed0=GLOBAL_SEED + i,
            spawn_rate_H=rate, spawn_rate_V=rate,
            tmax=tmax, warmup=tmax * 0.2,
            radius=15.0,
        )
        means[i] = res["mean_all"]
        waits[i] = res["mean_wait"]
        flows[i] = res["flow"]
        mean_err[i] = res["mean_all_stderr"]
        flow_err[i] = res["flow_stderr"]
        print(f"  rate={rate:.2f}: mean={means[i]:.1f}s wait={waits[i]:.1f}s"
              f" flow={flows[i]:.3f} cars/s")

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    axes[0].errorbar(spawn_rates, means, yerr=mean_err, fmt="o-", lw=2,
                     color="tab:blue", capsize=3)
    axes[0].set_xlabel("spawn rate (cars/s per arm)")
    axes[0].set_ylabel("mean passing time (s)")
    axes[0].set_title("Passing time")

    axes[1].plot(spawn_rates, waits, "s-", lw=2, color="tab:orange")
    axes[1].set_xlabel("spawn rate (cars/s per arm)")
    axes[1].set_ylabel("mean wait before entry (s)")
    axes[1].set_title("Entry delay")

    axes[2].errorbar(spawn_rates, flows, yerr=flow_err, fmt="^-", lw=2,
                     color="tab:green", capsize=3)
    axes[2].set_xlabel("spawn rate (cars/s per arm)")
    axes[2].set_ylabel("throughput (cars/s)")
    axes[2].set_title("Completed flow")

    plt.suptitle("Figure 4 -- Roundabout performance vs traffic volume",
                 fontweight="bold")
    plt.tight_layout()
    out = FIGURES_DIR / "fig4_roundabout_volume_sweep.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("saved", out)

    np.savez(FIGURES_DIR / "data_roundabout_volume_sweep.npz",
             spawn_rates=spawn_rates, means=means, waits=waits, flows=flows,
             mean_err=mean_err, flow_err=flow_err)


if __name__ == "__main__":
    main()
