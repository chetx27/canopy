from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from canopy.config import ensure_dir, load_config, save_json
from canopy.data.stack_loader import cell_coordinates, load_monthly_stack, stack_to_cube
from canopy.evaluation.registry import ExperimentRegistry
from canopy.evaluation.splits import assign_spatial_blocks, split_blocks
from canopy.heat.evaluation import (
    compute_exposure_surfaces,
    evaluate_formulation_correlations,
    population_scale_sensitivity,
    summarize_surface,
    top_k_jaccard,
)
from canopy.heat.exposure import total_exposure
from canopy.heat.layers import derive_pilot_heat_layers, mean_canopy_from_stack


def _correlation_figure(corr: dict[str, float], out_path: Path) -> str:
    names = list(corr.keys())
    values = [corr[n] for n in names]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(names, values, color="orangered")
    ax.set_ylim(-1.0, 1.0)
    ax.set_ylabel("Pearson r with held-out LST")
    ax.set_title("M7 exposure formulation correlation (test blocks)")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


def run_m7_heat_exposure(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    stack_path = Path(cfg["paths"]["processed_stack"])
    nodata = cfg.get("preprocessing", {}).get("nodata", -9999.0)
    ds = load_monthly_stack(stack_path)
    cube, times = stack_to_cube(ds, nodata=nodata)

    canopy = mean_canopy_from_stack(cube)
    layers = derive_pilot_heat_layers(canopy, seed=cfg.get("project", {}).get("seed", 42), cfg=cfg)
    lst = layers["lst"]
    population = layers["population"]
    building_density = layers["building_density"]

    heat_cfg = cfg.get("heat", {})
    reference_lst = float(heat_cfg.get("lst_reference_celsius", 24.0))
    coef_canopy = float(heat_cfg.get("downscale_coef_canopy", -2.0))
    coef_build = float(heat_cfg.get("downscale_coef_building", 1.5))
    surfaces = compute_exposure_surfaces(
        lst,
        population,
        canopy,
        building_density,
        reference_lst=reference_lst,
        coef_canopy=coef_canopy,
        coef_build=coef_build,
    )

    resolution = float(cfg["study_area"]["grid_resolution_m"])
    block_size = float(cfg["evaluation"]["spatial_block_size_m"])
    rows, cols = canopy.shape
    xx, yy = cell_coordinates(rows, cols, resolution)
    block_grid = assign_spatial_blocks(xx.ravel(), yy.ravel(), block_size_m=block_size).reshape(rows, cols)
    train_blocks, _, test_blocks = split_blocks(
        block_grid.ravel(),
        train_fraction=cfg["evaluation"].get("train_fraction", 0.6),
        val_fraction=cfg["evaluation"].get("val_fraction", 0.2),
        seed=cfg.get("project", {}).get("seed", 42),
    )
    train_ids = np.array(list(train_blocks), dtype=block_grid.dtype)
    test_ids = np.array(list(test_blocks), dtype=block_grid.dtype)
    test_mask = np.isin(block_grid, test_ids)
    train_mask = np.isin(block_grid, train_ids)

    test_corr = evaluate_formulation_correlations(surfaces, lst, test_mask)
    train_corr = evaluate_formulation_correlations(surfaces, lst, train_mask)

    top_k = int(cfg.get("heat", {}).get("priority_top_k", 100))
    lst_vs_exposure_jaccard = top_k_jaccard(
        surfaces["raw_lst"],
        surfaces["population_weighted_exposure"],
        top_k,
        mask=test_mask,
    )
    lst_vs_downscaled_jaccard = top_k_jaccard(
        surfaces["raw_lst"],
        surfaces["downscaled_lst_proxy"],
        top_k,
        mask=test_mask,
    )

    pop_scales = cfg.get("heat", {}).get("population_sensitivity_scales", [0.5, 1.0, 2.0])
    pop_sensitivity = population_scale_sensitivity(
        lst,
        population,
        canopy,
        building_density,
        pop_scales,
        reference_lst=reference_lst,
        top_k=top_k,
    )

    primary = surfaces["population_weighted_exposure"]
    min_corr = float(cfg.get("evaluation", {}).get("min_lst_correlation", 0.5))
    max_jaccard = float(cfg.get("evaluation", {}).get("max_lst_exposure_topk_jaccard", 0.9))
    primary_corr = test_corr.get("population_weighted_exposure", float("nan"))
    ranking_differs = bool(np.isfinite(lst_vs_exposure_jaccard) and lst_vs_exposure_jaccard < max_jaccard)
    corr_ok = bool(np.isfinite(primary_corr) and primary_corr >= min_corr)

    payload: dict[str, Any] = {
        "experiment_id": cfg.get("experiment_id", "m7"),
        "stack_path": str(stack_path),
        "n_times": len(times),
        "latest_time": times[-1] if times else None,
        "synthetic_layers": layers.get("synthetic", True),
        "reference_lst_celsius": reference_lst,
        "n_train_blocks": len(train_blocks),
        "n_test_blocks": len(test_blocks),
        "surface_summaries_full": {k: summarize_surface(v) for k, v in surfaces.items()},
        "surface_summaries_test": {k: summarize_surface(v, test_mask) for k, v in surfaces.items()},
        "total_population_weighted_exposure": total_exposure(primary),
        "train_correlation_with_lst": train_corr,
        "test_correlation_with_lst": test_corr,
        "priority_overlap": {
            "top_k": top_k,
            "raw_lst_vs_pop_weighted_jaccard": lst_vs_exposure_jaccard,
            "raw_lst_vs_downscaled_jaccard": lst_vs_downscaled_jaccard,
        },
        "population_sensitivity": pop_sensitivity,
        "go_decision": {
            "proceed_to_m8_intervention_simulator": bool(ranking_differs and corr_ok),
            "population_weighting_changes_topk_priorities": ranking_differs,
            "primary_formulation_lst_correlation_ok": corr_ok,
            "primary_formulation_lst_correlation": primary_corr,
            "note": "Pilot layers are derived from NDVI when real LST/population rasters are absent.",
        },
    }

    out_dir = Path(cfg["paths"]["results"])
    ensure_dir(out_dir)
    fig = _correlation_figure(test_corr, out_dir / "exposure_lst_correlation.png")
    payload["figure_paths"] = [fig]
    save_json(out_dir / "heat_exposure_eval.json", payload)
    ExperimentRegistry().register(cfg.get("experiment_id", "m7"), payload)
    return payload
