"""Traffic-light cycle-length sweep at fixed traffic volume (analysis #5).

Holds the spawn rate constant and varies the traffic-light cycle. The mean
passing time goes through a minimum: short cycles waste time switching, long
cycles let queues grow on the red road. The minimum locates the "best" cycle
for that volume.
"""

from _setup import FIGURES_DIR, GLOBAL_SEED, quick_mode

import numpy as np
import matplotlib.pyplot as plt

from trafficsim import run_repeated, run_traffic_light_sim


def main() -> None:
    quick = quick_mode()
    cycles = [10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 60.0, 80.0]
    if quick:
        cycles = [15.0, 30.0, 60.0]
    repeats = 2 if quick else 3
    tmax = 120.0 if quick else 240.0
    spawn_rate = 0.08

    means = np.full(len(cycles), np.nan)
    flows = np.full(len(cycles), np.nan)
    mean_err = np.full(len(cycles), np.nan)

    print(f"Cycle-length sweep at spawn rate {spawn_rate:.2f} cars/s/arm")
    for i, cyc in enumerate(cycles):
        res = run_repeated(
            run_traffic_light_sim, repeats=repeats,
            seed0=GLOBAL_SEED + 600 + i,
            spawn_rate_H=spawn_rate, spawn_rate_V=spawn_rate,
            tmax=tmax, warmup=tmax * 0.2,
            cycle=cyc, radius=15.0,
        )
        means[i] = res["mean_all"]
        flows[i] = res["flow"]
        mean_err[i] = res["mean_all_stderr"]
        print(f"  cycle={cyc:5.1f}s -> mean={means[i]:.2f}s flow={flows[i]:.3f}")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    axes[0].errorbar(cycles, means, yerr=mean_err, fmt="o-", lw=2,
                     color="tab:blue", capsize=3)
    axes[0].set_xlabel("cycle length (s)")
    axes[0].set_ylabel("mean passing time (s)")
    axes[0].set_title("Passing time vs cycle length")

    axes[1].plot(cycles, flows, "s-", lw=2, color="tab:green")
    axes[1].set_xlabel("cycle length (s)")
    axes[1].set_ylabel("throughput (cars/s)")
    axes[1].set_title("Throughput vs cycle length")

    plt.suptitle(f"Figure 9 -- Cycle-length sweep (spawn = {spawn_rate:.2f} cars/s)",
                 fontweight="bold")
    plt.tight_layout()
    out = FIGURES_DIR / "fig9_cycle_length_sweep.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("saved", out)

    np.savez(FIGURES_DIR / "data_cycle_length_sweep.npz",
             cycles=np.array(cycles), means=means, flows=flows, mean_err=mean_err,
             spawn_rate=spawn_rate)


if __name__ == "__main__":
    main()
