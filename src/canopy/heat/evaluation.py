from __future__ import annotations

from typing import Any

import numpy as np

from canopy.heat.exposure import downscale_lst_proxy, population_weighted_exposure, total_exposure


def spatial_pearson(a: np.ndarray, b: np.ndarray, mask: np.ndarray | None = None) -> float:
    x = np.asarray(a, dtype=float).ravel()
    y = np.asarray(b, dtype=float).ravel()
    if mask is not None:
        m = np.asarray(mask, dtype=bool).ravel()
        x = x[m]
        y = y[m]
    valid = np.isfinite(x) & np.isfinite(y)
    if valid.sum() < 3:
        return float("nan")
    x = x[valid]
    y = y[valid]
    if np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def rank_spearman(a: np.ndarray, b: np.ndarray, mask: np.ndarray | None = None) -> float:
    x = np.asarray(a, dtype=float).ravel()
    y = np.asarray(b, dtype=float).ravel()
    if mask is not None:
        m = np.asarray(mask, dtype=bool).ravel()
        x = x[m]
        y = y[m]
    valid = np.isfinite(x) & np.isfinite(y)
    if valid.sum() < 3:
        return float("nan")
    x = x[valid]
    y = y[valid]
    rx = np.argsort(np.argsort(x))
    ry = np.argsort(np.argsort(y))
    return spatial_pearson(rx, ry)


def top_k_indices(surface: np.ndarray, k: int, mask: np.ndarray | None = None) -> np.ndarray:
    arr = np.asarray(surface, dtype=float).ravel()
    if mask is not None:
        valid_idx = np.flatnonzero(np.asarray(mask, dtype=bool).ravel() & np.isfinite(arr))
    else:
        valid_idx = np.flatnonzero(np.isfinite(arr))
    if valid_idx.size == 0:
        return np.array([], dtype=int)
    order = valid_idx[np.argsort(arr[valid_idx])[::-1]]
    return order[: min(k, order.size)]


def top_k_jaccard(
    a: np.ndarray,
    b: np.ndarray,
    k: int,
    mask: np.ndarray | None = None,
) -> float:
    ia = set(top_k_indices(a, k, mask).tolist())
    ib = set(top_k_indices(b, k, mask).tolist())
    if not ia and not ib:
        return float("nan")
    if not ia or not ib:
        return 0.0
    return float(len(ia & ib) / len(ia | ib))


def compute_exposure_surfaces(
    lst: np.ndarray,
    population: np.ndarray,
    canopy: np.ndarray,
    building_density: np.ndarray,
    reference_lst: float = 24.0,
    coef_canopy: float = -2.0,
    coef_build: float = 1.5,
) -> dict[str, np.ndarray]:
    lst = np.asarray(lst, dtype=float)
    pop = np.asarray(population, dtype=float)
    canopy = np.asarray(canopy, dtype=float)
    building = np.asarray(building_density, dtype=float)
    downscaled = downscale_lst_proxy(lst, canopy, building, coef_canopy=coef_canopy, coef_build=coef_build)
    return {
        "raw_lst": lst,
        "lst_x_population": lst * np.maximum(pop, 0.0),
        "downscaled_lst_proxy": downscaled,
        "population_weighted_exposure": population_weighted_exposure(downscaled, pop, reference_lst),
    }


def summarize_surface(surface: np.ndarray, mask: np.ndarray | None = None) -> dict[str, float]:
    arr = np.asarray(surface, dtype=float)
    if mask is not None:
        arr = arr[np.asarray(mask, dtype=bool)]
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {"mean": float("nan"), "p90": float("nan"), "total": float("nan")}
    return {
        "mean": float(np.mean(arr)),
        "p90": float(np.quantile(arr, 0.9)),
        "total": float(np.nansum(arr)),
    }


def evaluate_formulation_correlations(
    surfaces: dict[str, np.ndarray],
    lst: np.ndarray,
    test_mask: np.ndarray,
) -> dict[str, float]:
    return {name: spatial_pearson(surface, lst, test_mask) for name, surface in surfaces.items()}


def population_scale_sensitivity(
    lst: np.ndarray,
    population: np.ndarray,
    canopy: np.ndarray,
    building_density: np.ndarray,
    scales: list[float],
    reference_lst: float = 24.0,
    top_k: int = 50,
) -> dict[str, Any]:
    base = compute_exposure_surfaces(lst, population, canopy, building_density, reference_lst=reference_lst)
    base_surface = base["population_weighted_exposure"]
    rows = []
    for scale in scales:
        scaled_pop = population * scale
        surface = population_weighted_exposure(
            base["downscaled_lst_proxy"],
            scaled_pop,
            reference_lst,
        )
        rows.append(
            {
                "scale": float(scale),
                "total_exposure": total_exposure(surface),
                "rank_spearman_vs_base": rank_spearman(base_surface, surface),
                "top_k_jaccard_vs_base": top_k_jaccard(base_surface, surface, top_k),
            }
        )
    return {"scales": rows, "top_k": top_k}
