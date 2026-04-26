"""Asymmetric roundabout sweep -- analyses #3.

The horizontal and vertical spawn rates are swept independently. The first
contour shows the joint mean passing time; the second triplet shows the
H-only mean, V-only mean, and the H-V difference (analysis #4 lives here too).
"""

from _setup import FIGURES_DIR, GLOBAL_SEED, quick_mode

import numpy as np
import matplotlib.pyplot as plt

from trafficsim import run_repeated, run_roundabout_sim


def main() -> None:
    quick = quick_mode()
    grid_rates = np.array([0.02, 0.04, 0.06, 0.08, 0.10, 0.12])
    if quick:
        grid_rates = np.array([0.04, 0.08, 0.12])
    repeats = 2 if quick else 3
    tmax = 120.0 if quick else 240.0

    n = len(grid_rates)
    contour_mean = np.full((n, n), np.nan)
    contour_H = np.full_like(contour_mean, np.nan)
    contour_V = np.full_like(contour_mean, np.nan)

    print("Asymmetric roundabout sweep")
    for j, v_rate in enumerate(grid_rates):
        for i, h_rate in enumerate(grid_rates):
            res = run_repeated(
                run_roundabout_sim, repeats=repeats,
                seed0=GLOBAL_SEED + 100 + 17 * i + 31 * j,
                spawn_rate_H=h_rate, spawn_rate_V=v_rate,
                tmax=tmax, warmup=tmax * 0.2,
                radius=15.0,
            )
            contour_mean[j, i] = res["mean_all"]
            contour_H[j, i] = res["mean_H"]
            contour_V[j, i] = res["mean_V"]
        print(f"  V-rate row {v_rate:.2f} done")

    H_grid, V_grid = np.meshgrid(grid_rates, grid_rates)

    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    cs = ax.contourf(H_grid, V_grid, contour_mean, levels=14, cmap="viridis")
    ax.contour(H_grid, V_grid, contour_mean, levels=7, colors="k",
               linewidths=0.5, alpha=0.55)
    plt.colorbar(cs, ax=ax).set_label("mean passing time (s)")
    ax.set_xlabel("H spawn rate (cars/s per arm)")
    ax.set_ylabel("V spawn rate (cars/s per arm)")
    ax.set_title("Figure 5 -- Roundabout asymmetric traffic",
                 fontweight="bold")
    ax.set_aspect("equal")
    plt.tight_layout()
    out1 = FIGURES_DIR / "fig5_roundabout_asymmetric_contour.png"
    plt.savefig(out1, bbox_inches="tight")
    plt.close(fig)
    print("saved", out1)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    panels = [
        (axes[0], contour_H, "H-road passing time", "Blues"),
        (axes[1], contour_V, "V-road passing time", "Greens"),
        (axes[2], contour_H - contour_V, "Bias: H minus V", "coolwarm"),
    ]
    for axis, data, title, cmap in panels:
        im = axis.contourf(H_grid, V_grid, data, levels=14, cmap=cmap)
        plt.colorbar(im, ax=axis)
        axis.set_xlabel("H spawn rate")
        axis.set_ylabel("V spawn rate")
        axis.set_title(title)
        axis.set_aspect("equal")
    axes[2].contour(H_grid, V_grid, contour_H - contour_V, levels=[0],
                    colors="k", linewidths=1.2)
    plt.suptitle("Figure 6 -- Directional bias in the roundabout",
                 fontweight="bold")
    plt.tight_layout()
    out2 = FIGURES_DIR / "fig6_roundabout_directional_bias.png"
    plt.savefig(out2, bbox_inches="tight")
    plt.close(fig)
    print("saved", out2)

    np.savez(FIGURES_DIR / "data_roundabout_asymmetric.npz",
             grid_rates=grid_rates,
             contour_mean=contour_mean,
             contour_H=contour_H,
             contour_V=contour_V)


if __name__ == "__main__":
    main()
