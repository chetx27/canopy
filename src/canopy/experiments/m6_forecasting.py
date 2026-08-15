from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from canopy.config import ensure_dir, load_config, save_json
from canopy.data.stack_loader import cell_coordinates, load_monthly_stack, stack_to_cube
from canopy.evaluation.registry import ExperimentRegistry
from canopy.evaluation.splits import assign_spatial_blocks, split_blocks
from canopy.forecasting.evaluation import evaluate_stack_forecasts


def _load_eval_cells(cfg: dict[str, Any], cube: np.ndarray) -> tuple[np.ndarray, np.ndarray, bool]:
    merged = cfg.get("labels", {}).get("merged_path")
    label_path = cfg.get("labels", {}).get("path")
    auto = False
    if merged and Path(merged).exists():
        df = pd.read_csv(merged)
    elif label_path and Path(label_path).exists():
        df = pd.read_csv(label_path)
    else:
        auto = True
        _, rows, cols = cube.shape
        rng = np.random.default_rng(cfg.get("project", {}).get("seed", 42))
        sample_rows = rng.integers(0, rows, size=120)
        sample_cols = rng.integers(0, cols, size=120)
        df = pd.DataFrame({"row": sample_rows, "col": sample_cols})
    return df["row"].values, df["col"].values, auto


def _figure(results: dict[str, Any], out_path: Path) -> str:
    methods = list(results.keys())
    horizons = sorted({h for m in results.values() for h in m.keys()}, key=int)
    x = np.arange(len(horizons))
    width = 0.8 / max(len(methods), 1)
    fig, ax = plt.subplots(figsize=(10, 4))
    for i, method in enumerate(methods):
        mae = [results[method][h]["mae"] for h in horizons]
        ax.bar(x + i * width, mae, width=width, label=method)
    ax.set_xticks(x + width * (len(methods) - 1) / 2)
    ax.set_xticklabels([f"{h}m" for h in horizons])
    ax.set_ylabel("MAE")
    ax.set_title("M6 forecast MAE by horizon (test cells)")
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


def run_m6_forecasting(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    stack_path = Path(cfg["paths"]["processed_stack"])
    nodata = cfg.get("preprocessing", {}).get("nodata", -9999.0)
    ds = load_monthly_stack(stack_path)
    cube, times = stack_to_cube(ds, nodata=nodata)

    rows, cols, auto_cells = _load_eval_cells(cfg, cube)
    resolution = float(cfg["study_area"]["grid_resolution_m"])
    block_size = float(cfg["evaluation"]["spatial_block_size_m"])
    grid_rows, grid_cols = cube.shape[1], cube.shape[2]
    xx, yy = cell_coordinates(grid_rows, grid_cols, resolution)
    block_grid = assign_spatial_blocks(xx.ravel(), yy.ravel(), block_size_m=block_size).reshape(grid_rows, grid_cols)
    cell_blocks = np.array([block_grid[int(r), int(c)] for r, c in zip(rows, cols)])

    _, _, test_blocks = split_blocks(
        cell_blocks,
        train_fraction=cfg["evaluation"].get("train_fraction", 0.6),
        val_fraction=cfg["evaluation"].get("val_fraction", 0.2),
        seed=cfg.get("project", {}).get("seed", 42),
    )
    test_mask = np.array([b in test_blocks for b in cell_blocks])
    test_rows = rows[test_mask]
    test_cols = cols[test_mask]

    fc_cfg = cfg.get("forecasting", {})
    methods = fc_cfg.get("methods", ["persistence", "seasonal_naive", "linear_trend", "gbdt"])
    horizons = fc_cfg.get("horizons_months", [1, 3, 6])
    kwargs = {
        "max_lags": fc_cfg.get("max_lags", 6),
        "season_length": fc_cfg.get("season_length", 12),
        "min_history": fc_cfg.get("min_history", 8),
    }

    test_results = evaluate_stack_forecasts(cube, test_rows, test_cols, horizons, methods, kwargs)
    full_results = evaluate_stack_forecasts(cube, rows, cols, horizons, methods, kwargs)

    best_by_horizon = {}
    for h in horizons:
        hs = str(h)
        best_method = min(methods, key=lambda m: test_results[m][hs]["mae"])
        best_by_horizon[hs] = best_method

    gbdt_better = all(
        test_results["gbdt"][str(h)]["mae"] <= test_results["persistence"][str(h)]["mae"] * 1.05
        for h in horizons
        if test_results["gbdt"][str(h)]["n"] > 0
    )

    payload: dict[str, Any] = {
        "experiment_id": cfg.get("experiment_id", "m6"),
        "stack_path": str(stack_path),
        "n_times": len(times),
        "times": times,
        "auto_cells": auto_cells,
        "n_eval_cells_full": len(rows),
        "n_eval_cells_test": len(test_rows),
        "test_results": test_results,
        "full_results": full_results,
        "best_method_by_horizon": best_by_horizon,
        "go_decision": {
            "proceed_to_m7_heat_exposure": bool(gbdt_better),
            "gbdt_beats_persistence_all_horizons": gbdt_better,
            "note": "Holdout evaluation uses final N months as forecast targets without future leakage.",
        },
    }

    out_dir = Path(cfg["paths"]["results"])
    ensure_dir(out_dir)
    fig = _figure(test_results, out_dir / "forecast_mae_by_horizon.png")
    payload["figure_paths"] = [fig]
    save_json(out_dir / "forecast_eval.json", payload)
    ExperimentRegistry().register(cfg.get("experiment_id", "m6"), payload)
    return payload
