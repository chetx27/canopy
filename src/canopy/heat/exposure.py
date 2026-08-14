from __future__ import annotations

import numpy as np


def population_weighted_exposure(
    lst: np.ndarray,
    population: np.ndarray,
    reference_lst: float = 24.0,
) -> np.ndarray:
    lst = np.asarray(lst, dtype=float)
    pop = np.asarray(population, dtype=float)
    excess = np.maximum(lst - reference_lst, 0.0)
    return excess * np.maximum(pop, 0.0)


def total_exposure(exposure_surface: np.ndarray) -> float:
    arr = np.asarray(exposure_surface, dtype=float)
    return float(np.nansum(arr))


def downscale_lst_proxy(
    lst: np.ndarray,
    canopy: np.ndarray,
    building_density: np.ndarray,
    coef_canopy: float = -2.0,
    coef_build: float = 1.5,
) -> np.ndarray:
    lst = np.asarray(lst, dtype=float)
    canopy = np.asarray(canopy, dtype=float)
    build = np.asarray(building_density, dtype=float)
    adjustment = coef_canopy * canopy + coef_build * build
    return lst + adjustment


def exposure_reduction_from_canopy_gain(
    current_canopy: np.ndarray,
    canopy_gain: np.ndarray,
    lst: np.ndarray,
    population: np.ndarray,
    cooling_per_canopy_unit: float = 2.0,
    reference_lst: float = 24.0,
) -> np.ndarray:
    current = np.asarray(current_canopy, dtype=float)
    gain = np.asarray(canopy_gain, dtype=float)
    lst = np.asarray(lst, dtype=float)
    pop = np.asarray(population, dtype=float)
    cooling = cooling_per_canopy_unit * gain
    new_lst = np.maximum(lst - cooling, 0.0)
    before = population_weighted_exposure(lst, pop, reference_lst)
    after = population_weighted_exposure(new_lst, pop, reference_lst)
    return before - after
