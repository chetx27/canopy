from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from canopy.config import ensure_dir, load_config, save_json
from canopy.data.labeling import load_detection_labels
from canopy.data.stack_loader import cell_coordinates, load_monthly_stack, stack_to_cube
from canopy.detection.temporal_ml import fit_temporal_models
from canopy.evaluation.detection_eval import evaluate_method_on_cells
from canopy.evaluation.registry import ExperimentRegistry
from canopy.evaluation.splits import assign_spatial_blocks, split_blocks
from canopy.temporal.features import feature_names


def _comparison_figure(results: dict[str, Any], out_path: Path, title: str) -> str:
    methods = list(results.keys())
    f1 = [results[m].get("persistent_f1", 0) for m in methods]
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(methods, f1, color="darkgreen")
    ax.set_ylabel("Persistent F1")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


def _ablation_configs(base_cfg: dict[str, Any]) -> dict[str, dict[str, Any]]:
    all_names = feature_names(max_lags=base_cfg.get("temporal_model", {}).get("max_lags", 3))
    ndvi_only = ["ndvi_mean", "ndvi_std", "ndvi_min", "ndvi_max", "ndvi_range", "trend", "recent_delta"]
    no_seasonal = [n for n in all_names if "seasonal" not in n and "harmonic" not in n]
    return {
        "full_features": {"feature_subset": None},
        "ndvi_only": {"feature_subset": ndvi_only},
        "no_seasonal": {"feature_subset": no_seasonal},
    }


def run_m4_detection(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    stack_path = Path(cfg["paths"]["processed_stack"])
    nodata = cfg.get("preprocessing", {}).get("nodata", -9999.0)
    ds = load_monthly_stack(stack_path)
    cube, times = stack_to_cube(ds, nodata=nodata)

    label_path = cfg.get("labels", {}).get("path")
    merged = cfg.get("labels", {}).get("merged_path")
    if merged and Path(merged).exists():
        labels_df = pd.read_csv(merged)
        auto_labeled = False
    else:
        labels_df, auto_labeled = load_detection_labels(label_path, cube, times, cfg)

    resolution = float(cfg["study_area"]["grid_resolution_m"])
    block_size = float(cfg["evaluation"]["spatial_block_size_m"])
    rows, cols = cube.shape[1], cube.shape[2]
    xx, yy = cell_coordinates(rows, cols, resolution)
    block_grid = assign_spatial_blocks(xx.ravel(), yy.ravel(), block_size_m=block_size).reshape(rows, cols)
    cell_blocks = labels_df.apply(lambda r: block_grid[int(r["row"]), int(r["col"])], axis=1).values

    train_blocks, val_blocks, test_blocks = split_blocks(
        cell_blocks,
        train_fraction=cfg["evaluation"].get("train_fraction", 0.6),
        val_fraction=cfg["evaluation"].get("val_fraction", 0.2),
        seed=cfg.get("project", {}).get("seed", 42),
    )
    train_mask = np.array([b in train_blocks for b in cell_blocks])
    val_mask = np.array([b in val_blocks for b in cell_blocks])
    test_mask = np.array([b in test_blocks for b in cell_blocks])

    det_cfg = {**cfg.get("detection", {}), **cfg.get("study_area", {}), **cfg.get("temporal_model", {})}
    det_cfg["spatial_block_size_m"] = block_size
    det_cfg["grid_resolution_m"] = resolution
    det_cfg["seed"] = cfg.get("project", {}).get("seed", 42)

    baseline_methods = cfg["detection"].get("baseline_methods", [])
    test_results: dict[str, Any] = {}
    for method in baseline_methods:
        test_results[method] = evaluate_method_on_cells(
            method, labels_df, cube, times, det_cfg, test_mask=test_mask
        )

    tm_cfg = {
        **cfg.get("temporal_model", {}),
        "seed": cfg.get("project", {}).get("seed", 42),
        "persistence_min_months": cfg["detection"].get("persistence_min_months", 2),
    }
    model = fit_temporal_models(cube, labels_df, times, train_mask, tm_cfg)
    test_results["temporal_gbm"] = evaluate_method_on_cells(
        "temporal_gbm",
        labels_df,
        cube,
        times,
        det_cfg,
        test_mask=test_mask,
        ml_model=model,
    )

    ablation_results: dict[str, Any] = {}
    for ab_name, ab_override in _ablation_configs(cfg).items():
        ab_cfg = {**tm_cfg, **ab_override}
        ab_model = fit_temporal_models(cube, labels_df, times, train_mask, ab_cfg)
        ablation_results[ab_name] = evaluate_method_on_cells(
            "temporal_gbm",
            labels_df,
            cube,
            times,
            det_cfg,
            test_mask=test_mask,
            ml_model=ab_model,
        )

    val_results = evaluate_method_on_cells(
        "temporal_gbm",
        labels_df,
        cube,
        times,
        det_cfg,
        test_mask=val_mask,
        ml_model=model,
    )

    best_baseline = max(
        baseline_methods,
        key=lambda m: test_results.get(m, {}).get("persistent_f1", 0),
    )
    baseline_f1 = test_results.get(best_baseline, {}).get("persistent_f1", 0)
    model_f1 = test_results.get("temporal_gbm", {}).get("persistent_f1", 0)
    f1_gain = model_f1 - baseline_f1

    payload: dict[str, Any] = {
        "experiment_id": cfg.get("experiment_id", "m4"),
        "stack_path": str(stack_path),
        "labels_path": str(merged or label_path),
        "auto_labeled": auto_labeled,
        "n_labels": len(labels_df),
        "n_train_cells": int(train_mask.sum()),
        "n_val_cells": int(val_mask.sum()),
        "n_test_cells": int(test_mask.sum()),
        "feature_names": model.feature_names,
        "test_set_results": test_results,
        "validation_temporal_gbm": val_results,
        "ablation_results": ablation_results,
        "go_decision": {
            "proceed_to_m6_forecasting": bool(
                f1_gain >= cfg["evaluation"].get("min_f1_gain_vs_best_baseline", 0.03)
            ),
            "best_baseline": best_baseline,
            "f1_gain_vs_best_baseline": f1_gain,
            "note": "Train on spatial train blocks; evaluate on held-out test blocks.",
        },
    }

    out_dir = Path(cfg["paths"]["results"])
    ensure_dir(out_dir)
    fig1 = _comparison_figure(test_results, out_dir / "m4_method_comparison.png", "M4 test-set detection comparison")
    fig2 = _comparison_figure(ablation_results, out_dir / "m4_ablation_comparison.png", "M4 temporal GBM ablation")
    payload["figure_paths"] = [fig1, fig2]
    save_json(out_dir / "temporal_model_eval.json", payload)
    ExperimentRegistry().register(cfg.get("experiment_id", "m4"), payload)
    return payload
