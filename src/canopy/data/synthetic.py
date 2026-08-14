from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np

from canopy.data.preprocess import month_list


def generate_synthetic_pilot_stack(
    cfg: dict[str, Any],
    seed: int | None = None,
) -> tuple[dict[str, np.ndarray], dict[str, int]]:
    rng = np.random.default_rng(seed or cfg.get("project", {}).get("seed", 42))
    months = month_list(cfg["temporal"]["start_date"], cfg["temporal"]["end_date"])
    rows, cols = 120, 120
    base_ndvi = rng.uniform(0.25, 0.75, size=(rows, cols))
    built = rng.random((rows, cols)) < 0.35
    base_ndvi[built] *= 0.4
    monthly: dict[str, np.ndarray] = {}
    counts: dict[str, int] = {}
    for month in months:
        month_num = datetime.strptime(month, "%Y-%m").month
        seasonal = 0.08 * np.sin(2 * np.pi * (month_num - 1) / 12.0)
        noise = rng.normal(0, 0.03, size=(rows, cols))
        arr = np.clip(base_ndvi + seasonal + noise, 0.05, 0.95)
        if month_num in {6, 7, 8, 9, 10}:
            cloud_frac = rng.uniform(0.35, 0.75)
            n_obs = int(rng.integers(1, 4))
        else:
            cloud_frac = rng.uniform(0.05, 0.25)
            n_obs = int(rng.integers(3, 12))
        cloud_mask = rng.random((rows, cols)) < cloud_frac
        arr = arr.astype(float)
        arr[cloud_mask] = np.nan
        monthly[month] = arr
        counts[month] = n_obs
    loss_cells = rng.random((rows, cols)) < 0.02
    for month in months:
        if month >= "2023-09":
            degraded = monthly[month][loss_cells] * 0.3 + 0.05
            monthly[month][loss_cells] = np.clip(degraded, 0.05, 0.95)
    return monthly, counts
