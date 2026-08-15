from __future__ import annotations

from typing import Any

import numpy as np

from canopy.heat.evaluation import compute_exposure_surfaces
from canopy.intervention.simulator import InterventionCell, InterventionParams


def estimate_maturity(canopy_series: np.ndarray, canopy_mean: float) -> float:
    series = np.asarray(canopy_series, dtype=float)
    valid = series[np.isfinite(series)]
    if valid.size < 3:
        return float(np.clip(canopy_mean, 0.0, 1.0))
    trend = float(valid[-1] - valid[0])
    stability = 1.0 - min(float(np.nanstd(valid)) * 2.0, 1.0)
    maturity = 0.5 * stability + 0.3 * float(canopy_mean) + 0.2 * float(max(-trend, 0.0))
    return float(np.clip(maturity, 0.0, 1.0))


def build_intervention_grid(
    cube: np.ndarray,
    canopy: np.ndarray,
    lst: np.ndarray,
    population: np.ndarray,
    building_density: np.ndarray,
    exposure_surface: np.ndarray,
    cfg: dict[str, Any],
    seed: int = 42,
) -> list[InterventionCell]:
    params = InterventionParams.from_config(cfg)
    rng = np.random.default_rng(seed)
    iv_cfg = cfg.get("intervention", {})
    rows, cols = canopy.shape
    max_cells = int(iv_cfg.get("max_eval_cells", 500))
    min_exposure = float(iv_cfg.get("min_exposure", 0.0))
    preserve_quota = int(iv_cfg.get("preserve_sample", 100))
    plant_quota = int(iv_cfg.get("plant_sample", 200))
    restore_quota = int(iv_cfg.get("restore_sample", 100))

    flat_exposure = exposure_surface.ravel()
    valid = np.isfinite(flat_exposure) & (flat_exposure >= min_exposure)
    candidate_idx = np.flatnonzero(valid)

    preserve_pool: list[int] = []
    plant_pool: list[int] = []
    restore_pool: list[int] = []
    meta: dict[int, dict[str, Any]] = {}
    for flat_idx in candidate_idx:
        row, col = divmod(int(flat_idx), cols)
        canopy_val = float(canopy[row, col])
        maturity = estimate_maturity(cube[:, row, col], canopy_val)
        water_feasible = bool(rng.random() > float(iv_cfg.get("water_infeasible_fraction", 0.15)))
        plantable = canopy_val <= params.plantable_canopy_max and building_density[row, col] < 0.85
        preserve_candidate = (
            maturity >= params.preserve_maturity_threshold
            and canopy_val >= params.preserve_canopy_threshold
        )
        restorable = (
            params.plantable_canopy_max < canopy_val <= params.restorable_canopy_max
            and building_density[row, col] < 0.9
        )
        meta[int(flat_idx)] = {
            "row": row,
            "col": col,
            "canopy_val": canopy_val,
            "maturity": maturity,
            "water_feasible": water_feasible,
            "plantable": plantable,
            "preserve_candidate": preserve_candidate,
            "restorable": restorable,
        }
        if preserve_candidate:
            preserve_pool.append(int(flat_idx))
        if plantable:
            plant_pool.append(int(flat_idx))
        if restorable:
            restore_pool.append(int(flat_idx))

    def _top_by_exposure(pool: list[int], quota: int) -> list[int]:
        if quota <= 0 or not pool:
            return []
        order = sorted(pool, key=lambda i: flat_exposure[i], reverse=True)
        return order[:quota]

    selected: list[int] = []
    seen: set[int] = set()
    for pool, quota in (
        (preserve_pool, preserve_quota),
        (restore_pool, restore_quota),
        (plant_pool, plant_quota),
    ):
        for flat_idx in _top_by_exposure(pool, quota):
            if len(selected) >= max_cells:
                break
            if flat_idx not in seen:
                selected.append(flat_idx)
                seen.add(flat_idx)
        if len(selected) >= max_cells:
            break
    if len(selected) < max_cells:
        remaining = [i for i in candidate_idx if int(i) not in seen]
        order = sorted(remaining, key=lambda i: flat_exposure[i], reverse=True)
        for flat_idx in order[: max_cells - len(selected)]:
            selected.append(int(flat_idx))
            seen.add(int(flat_idx))

    cells: list[InterventionCell] = []
    for cell_id, flat_idx in enumerate(selected):
        info = meta[flat_idx]
        row, col = info["row"], info["col"]
        cells.append(
            InterventionCell(
                cell_id=cell_id,
                row=row,
                col=col,
                lst=float(lst[row, col]),
                canopy=float(info["canopy_val"]),
                population=float(population[row, col]),
                building_density=float(building_density[row, col]),
                maturity=float(info["maturity"]),
                exposure=float(exposure_surface[row, col]),
                water_feasible=bool(info["water_feasible"]),
                plantable=bool(info["plantable"]),
                preserve_candidate=bool(info["preserve_candidate"]),
                restorable=bool(info["restorable"]),
            )
        )
    return cells


def load_heat_surfaces_for_intervention(
    canopy: np.ndarray,
    lst: np.ndarray,
    population: np.ndarray,
    building_density: np.ndarray,
    cfg: dict[str, Any],
) -> np.ndarray:
    heat_cfg = cfg.get("heat", {})
    surfaces = compute_exposure_surfaces(
        lst,
        population,
        canopy,
        building_density,
        reference_lst=float(heat_cfg.get("lst_reference_celsius", 24.0)),
        coef_canopy=float(heat_cfg.get("downscale_coef_canopy", -2.0)),
        coef_build=float(heat_cfg.get("downscale_coef_building", 1.5)),
    )
    return surfaces["population_weighted_exposure"]
