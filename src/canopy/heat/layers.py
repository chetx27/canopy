from __future__ import annotations

from typing import Any

import numpy as np


def mean_canopy_from_stack(cube: np.ndarray) -> np.ndarray:
    arr = np.asarray(cube, dtype=float)
    return np.nanmean(arr, axis=0)


def derive_pilot_heat_layers(
    canopy: np.ndarray,
    seed: int = 42,
    cfg: dict[str, Any] | None = None,
) -> dict[str, np.ndarray]:
    """Build deterministic pilot LST/population/building layers from canopy proxy."""
    cfg = cfg or {}
    heat_cfg = cfg.get("heat", {})
    rng = np.random.default_rng(seed)
    canopy = np.asarray(canopy, dtype=float)
    canopy = np.clip(np.nan_to_num(canopy, nan=0.2), 0.0, 1.0)
    rows, cols = canopy.shape

    building_density = np.clip(1.0 - canopy * 1.15, 0.0, 1.0)
    yy, xx = np.mgrid[0:rows, 0:cols]
    center_r, center_c = rows / 2.0, cols / 2.0
    dist = np.sqrt((yy - center_r) ** 2 + (xx - center_c) ** 2)
    dist_norm = dist / max(dist.max(), 1.0)
    urban_core = np.exp(-3.0 * dist_norm) * (0.4 + 0.6 * building_density)
    population = 50.0 + 250.0 * urban_core + rng.normal(0, 8, size=(rows, cols))
    population = np.clip(population, 0.0, None)

    lst_base = float(heat_cfg.get("lst_base_celsius", 30.0))
    lst_amp = float(heat_cfg.get("lst_canopy_sensitivity", 12.0))
    lst = lst_base + lst_amp * (1.0 - canopy) + 2.0 * building_density + rng.normal(0, 0.6, size=(rows, cols))
    lst = np.clip(lst, 20.0, 48.0)

    return {
        "canopy": canopy,
        "building_density": building_density,
        "population": population,
        "lst": lst,
        "synthetic": True,
    }
