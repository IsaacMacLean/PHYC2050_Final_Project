"""Repeated-run helper used by the analysis scripts.

Each analysis runs every operating point with multiple random seeds so that the
plotted curves include an estimate of the standard error.
"""

from __future__ import annotations

import warnings
from typing import Callable

import numpy as np

from .vehicle import finite_mean

SUMMARY_METRICS = [
    "mean_all", "std_all", "mean_wait", "mean_H", "mean_V",
    "bias_H_minus_V", "flow", "density",
]


def run_repeated(sim_func: Callable, repeats: int = 3, seed0: int = 0, **kwargs) -> dict:
    """Run ``sim_func`` ``repeats`` times with seeds ``seed0, seed0+1009, ...``.

    Returns a single dict that mirrors the per-run result but with averaged
    metrics and a ``<metric>_stderr`` column for every entry in
    ``SUMMARY_METRICS``.
    """
    results = [sim_func(seed=seed0 + 1009 * rep, **kwargs) for rep in range(repeats)]

    combined = {k: v for k, v in results[0].items()
                if k not in ("cars", "frames", "total_times", "wait_times")}
    combined["repeats"] = repeats
    combined["replicate_results"] = results
    combined["n_spawned"] = int(sum(r["n_spawned"] for r in results))
    combined["n_finished"] = int(sum(r["n_finished"] for r in results))
    combined["n_measured"] = int(sum(r["n_measured"] for r in results))

    for metric in SUMMARY_METRICS:
        values = np.array([r.get(metric, np.nan) for r in results], dtype=float)
        combined[metric] = finite_mean(values)
        if np.any(np.isfinite(values)):
            combined[metric + "_stderr"] = float(
                np.nanstd(values) / np.sqrt(np.sum(np.isfinite(values)))
            )
        else:
            combined[metric + "_stderr"] = float("nan")

    with warnings.catch_warnings():
        # A NaN-only column (an arm with no measured cars in any replicate at
        # very low spawn rates) is expected; nanmean's "empty slice" warning
        # is just noise here.
        warnings.simplefilter("ignore", RuntimeWarning)
        combined["mean_by_arm"] = np.nanmean(
            np.array([r["mean_by_arm"] for r in results], dtype=float), axis=0
        )
    return combined
