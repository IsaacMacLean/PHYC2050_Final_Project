"""Roundabout vs traffic-light comparison -- analyses #5 and #6.

Reuses the symmetric volume sweep on the roundabout, then runs the same volume
sweep against three traffic-light cycle times (20s, 40s, 60s). Plots passing
time and throughput side-by-side and computes the time-difference curve so
the "when is each better?" question has a direct answer.
"""

from _setup import FIGURES_DIR, GLOBAL_SEED, quick_mode

import numpy as np
import matplotlib.pyplot as plt

from trafficsim import (
    run_repeated,
    run_roundabout_sim,
    run_traffic_light_sim,
)


def sweep(sim_func, spawn_rates, repeats, tmax, seed0, **kwargs):
    means = np.full_like(spawn_rates, np.nan, dtype=float)
    waits = np.full_like(spawn_rates, np.nan, dtype=float)
    flows = np.full_like(spawn_rates, np.nan, dtype=float)
    mean_err = np.full_like(spawn_rates, np.nan, dtype=float)
    flow_err = np.full_like(spawn_rates, np.nan, dtype=float)
    for i, rate in enumerate(spawn_rates):
        res = run_repeated(
            sim_func, repeats=repeats, seed0=seed0 + i,
            spawn_rate_H=rate, spawn_rate_V=rate,
            tmax=tmax, warmup=tmax * 0.2,
            radius=15.0,
            **kwargs,
        )
        means[i] = res["mean_all"]
        waits[i] = res["mean_wait"]
        flows[i] = res["flow"]
        mean_err[i] = res["mean_all_stderr"]
        flow_err[i] = res["flow_stderr"]
    return means, waits, flows, mean_err, flow_err


def main() -> None:
    quick = quick_mode()
    spawn_rates = np.array([0.02, 0.04, 0.06, 0.08, 0.10, 0.12])
    repeats = 2 if quick else 3
    tmax = 120.0 if quick else 240.0

    print("Roundabout sweep (baseline)")
    rdb_mean, rdb_wait, rdb_flow, rdb_mean_err, rdb_flow_err = sweep(
        run_roundabout_sim, spawn_rates, repeats, tmax, GLOBAL_SEED + 200
    )

    cycle_periods = [20.0, 40.0, 60.0]
    tl_results = {}
    for cyc in cycle_periods:
        print(f"Traffic-light sweep, cycle={cyc:.0f} s")
        means, waits, flows, mean_err, flow_err = sweep(
            run_traffic_light_sim, spawn_rates, repeats, tmax,
            GLOBAL_SEED + 300 + int(cyc) * 10, cycle=cyc,
        )
        tl_results[cyc] = {
            "mean": means, "wait": waits, "flow": flows,
            "mean_err": mean_err, "flow_err": flow_err,
        }

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].errorbar(spawn_rates, rdb_mean, yerr=rdb_mean_err, fmt="o-",
                     color="k", lw=2.2, capsize=3, label="Roundabout")
    axes[1].errorbar(spawn_rates, rdb_flow, yerr=rdb_flow_err, fmt="o-",
                     color="k", lw=2.2, capsize=3, label="Roundabout")

    cycle_colors = ["tab:blue", "tab:orange", "tab:green"]
    for color, cyc in zip(cycle_colors, cycle_periods):
        d = tl_results[cyc]
        axes[0].errorbar(spawn_rates, d["mean"], yerr=d["mean_err"],
                         fmt="s--", color=color, lw=1.8, capsize=3,
                         label=f"Light {cyc:.0f}s")
        axes[1].errorbar(spawn_rates, d["flow"], yerr=d["flow_err"],
                         fmt="s--", color=color, lw=1.8, capsize=3,
                         label=f"Light {cyc:.0f}s")

    axes[0].set_xlabel("spawn rate (cars/s per arm)")
    axes[0].set_ylabel("mean passing time (s)")
    axes[0].set_title("Passing time")
    axes[0].legend()

    axes[1].set_xlabel("spawn rate (cars/s per arm)")
    axes[1].set_ylabel("throughput (cars/s)")
    axes[1].set_title("Completed flow")
    axes[1].legend()

    plt.suptitle("Figure 7 -- Roundabout vs traffic-light intersection",
                 fontweight="bold")
    plt.tight_layout()
    out1 = FIGURES_DIR / "fig7_roundabout_vs_lights.png"
    plt.savefig(out1, bbox_inches="tight")
    plt.close(fig)
    print("saved", out1)

    fig, ax = plt.subplots(figsize=(7.6, 4.7))
    for color, cyc in zip(cycle_colors, cycle_periods):
        diff = tl_results[cyc]["mean"] - rdb_mean
        ax.plot(spawn_rates, diff, "o-", color=color, lw=1.9,
                label=f"cycle={cyc:.0f}s")
    ax.axhline(0.0, color="k", ls="--", lw=1.0)
    ax.set_xlabel("spawn rate (cars/s per arm)")
    ax.set_ylabel("light mean time - roundabout mean time (s)")
    ax.set_title("Figure 8 -- Performance difference (positive = roundabout faster)",
                 fontweight="bold")
    ax.legend()
    plt.tight_layout()
    out2 = FIGURES_DIR / "fig8_performance_difference.png"
    plt.savefig(out2, bbox_inches="tight")
    plt.close(fig)
    print("saved", out2)

    print("\nSummary table")
    header = ["rate", "rdb_t", "rdb_flow"] + [f"L{int(c)}_t" for c in cycle_periods]
    print(" ".join(f"{h:>9}" for h in header))
    for i, rate in enumerate(spawn_rates):
        row = [rate, rdb_mean[i], rdb_flow[i]] + [tl_results[c]["mean"][i] for c in cycle_periods]
        print(" ".join(f"{v:9.3f}" for v in row))

    np.savez(FIGURES_DIR / "data_roundabout_vs_lights.npz",
             spawn_rates=spawn_rates,
             rdb_mean=rdb_mean, rdb_flow=rdb_flow,
             rdb_mean_err=rdb_mean_err, rdb_flow_err=rdb_flow_err,
             tl_means=np.array([tl_results[c]["mean"] for c in cycle_periods]),
             tl_flows=np.array([tl_results[c]["flow"] for c in cycle_periods]),
             cycle_periods=np.array(cycle_periods))


if __name__ == "__main__":
    main()
