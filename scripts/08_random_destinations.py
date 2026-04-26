"""Random-destination roundabout sweep -- analyses #7 and #8.

Re-runs the symmetric volume sweep with each car assigned a uniformly random
exit arm (left/right/straight) instead of always going straight, so we can see
how much extra time the random turns cost.
"""

from _setup import FIGURES_DIR, GLOBAL_SEED, quick_mode

import numpy as np
import matplotlib.pyplot as plt

from trafficsim import run_repeated, run_roundabout_sim


def sweep(spawn_rates, repeats, tmax, seed0, random_dest):
    means = np.full_like(spawn_rates, np.nan, dtype=float)
    flows = np.full_like(spawn_rates, np.nan, dtype=float)
    mean_err = np.full_like(spawn_rates, np.nan, dtype=float)
    for i, rate in enumerate(spawn_rates):
        res = run_repeated(
            run_roundabout_sim, repeats=repeats, seed0=seed0 + i,
            spawn_rate_H=rate, spawn_rate_V=rate,
            tmax=tmax, warmup=tmax * 0.2,
            random_dest=random_dest, radius=15.0,
        )
        means[i] = res["mean_all"]
        flows[i] = res["flow"]
        mean_err[i] = res["mean_all_stderr"]
    return means, flows, mean_err


def main() -> None:
    quick = quick_mode()
    spawn_rates = np.array([0.02, 0.04, 0.06, 0.08, 0.10, 0.12])
    repeats = 2 if quick else 3
    tmax = 120.0 if quick else 240.0

    print("Straight-only baseline")
    base_mean, base_flow, base_err = sweep(
        spawn_rates, repeats, tmax, GLOBAL_SEED + 700, random_dest=False
    )
    print("Random-destination sweep")
    rand_mean, rand_flow, rand_err = sweep(
        spawn_rates, repeats, tmax, GLOBAL_SEED + 800, random_dest=True
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    axes[0].errorbar(spawn_rates, base_mean, yerr=base_err, fmt="o-",
                     color="k", lw=2, label="straight through")
    axes[0].errorbar(spawn_rates, rand_mean, yerr=rand_err, fmt="s--",
                     color="tab:purple", lw=2, label="random exits")
    axes[0].set_xlabel("spawn rate (cars/s per arm)")
    axes[0].set_ylabel("mean passing time (s)")
    axes[0].set_title("Passing time")
    axes[0].legend()

    axes[1].plot(spawn_rates, base_flow, "o-", color="k", lw=2,
                 label="straight through")
    axes[1].plot(spawn_rates, rand_flow, "s--", color="tab:purple", lw=2,
                 label="random exits")
    axes[1].set_xlabel("spawn rate (cars/s per arm)")
    axes[1].set_ylabel("throughput (cars/s)")
    axes[1].set_title("Completed flow")
    axes[1].legend()

    plt.suptitle("Figure 10 -- Effect of random destinations",
                 fontweight="bold")
    plt.tight_layout()
    out = FIGURES_DIR / "fig10_random_destinations.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("saved", out)

    np.savez(FIGURES_DIR / "data_random_destinations.npz",
             spawn_rates=spawn_rates,
             base_mean=base_mean, rand_mean=rand_mean,
             base_flow=base_flow, rand_flow=rand_flow)


if __name__ == "__main__":
    main()
