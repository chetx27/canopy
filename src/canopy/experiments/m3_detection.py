from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from canopy.config import ensure_dir, load_config, save_json
from canopy.data.labeling import infer_event_month, load_detection_labels
from canopy.data.stack_loader import cell_coordinates, load_monthly_stack, stack_to_cube
from canopy.detection.baselines import detection_index, run_detector
from canopy.evaluation.metrics import binary_detection_metrics, spatial_block_bootstrap_mean
from canopy.evaluation.registry import ExperimentRegistry
from canopy.evaluation.splits import assign_spatial_blocks, split_blocks
from canopy.temporal.persistence import detection_delay_days


def _detector_kwargs(det_cfg: dict[str, Any]) -> dict[str, Any]:
    keys = {
        "ndvi_threshold",
        "delta_threshold",
        "anomaly_z_threshold",
        "persistence_min_months",
        "harmonic_order",
        "history_fraction",
    }
    return {k: v for k, v in det_cfg.items() if k in keys}


def _evaluate_method_on_cells(
    method: str,
    labels_df: pd.DataFrame,
    cube: np.ndarray,
    times: list[str],
    det_cfg: dict[str, Any],
    test_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    y_true = []
    y_pred = []
    stable_mask = []
    delays = []
    block_ids = []
    resolution = det_cfg.get("grid_resolution_m", 30.0)
    block_size = det_cfg.get("spatial_block_size_m", 500.0)
    det_kwargs = _detector_kwargs(det_cfg)

    for pos, (_, row) in enumerate(labels_df.iterrows()):
        if test_mask is not None and not test_mask[pos]:
            continue
        series = cube[:, int(row["row"]), int(row["col"])]
        if not np.isfinite(series).any():
            continue
        t_arr = np.arange(len(times), dtype=float)
        det = run_detector(method, series, t_arr, **det_kwargs)
        predicted = bool(det.flags.any())
        y_true.append(row["label"] == "persistent_loss")
        y_pred.append(predicted)
        stable_mask.append(row["label"] == "stable")
        bx = int(row["row"]) * resolution // block_size
        by = int(row["col"]) * resolution // block_size
        block_ids.append(bx * 100000 + by)

        if row["label"] == "persistent_loss":
            event_idx = None
            if pd.notna(row.get("event_month")) and str(row.get("event_month")) in times:
                event_idx = times.index(str(row["event_month"]))
            else:
                event_idx = infer_event_month(series, times)
            det_idx = detection_index(det)
            if event_idx is not None and det_idx is not None:
                delay = detection_delay_days(det_idx, event_idx, days_per_step=30.0)
                if delay is not None:
                    delays.append(delay)

    if not y_true:
        return {"error": "no_evaluable_cells"}

    metrics = binary_detection_metrics(
        np.array(y_true, dtype=bool),
        np.array(y_pred, dtype=bool),
        stable_mask=np.array(stable_mask, dtype=bool),
    )
    cell_scores = np.array([1.0 if t == p else 0.0 for t, p in zip(y_true, y_pred)], dtype=float)
    f1_boot = spatial_block_bootstrap_mean(
        cell_scores,
        np.array(block_ids),
        n_boot=200,
        seed=42,
    )
    return {
        "persistent_f1": metrics.f1,
        "precision": metrics.precision,
        "recall": metrics.recall,
        "false_positive_rate": metrics.false_positive_rate,
        "median_detection_delay_days": float(np.median(delays)) if delays else None,
        "n_eval_cells": len(y_true),
        "n_delay_samples": len(delays),
        "f1_bootstrap_mean": f1_boot[0],
        "f1_bootstrap_ci_low": f1_boot[1],
        "f1_bootstrap_ci_high": f1_boot[2],
    }


def _write_comparison_figure(method_results: dict[str, Any], out_path: Path) -> str:
    methods = list(method_results.keys())
    f1 = [method_results[m].get("persistent_f1", 0) for m in methods]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(methods, f1, color="teal")
    ax.set_ylabel("Persistent F1")
    ax.set_title("M3 baseline detection comparison (test cells)")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


def run_m3_detection(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    stack_path = Path(cfg["paths"]["processed_stack"])
    nodata = cfg.get("preprocessing", {}).get("nodata", -9999.0)
    ds = load_monthly_stack(stack_path)
    cube, times = stack_to_cube(ds, nodata=nodata)

    labels_df, auto_labeled = load_detection_labels(
        cfg.get("labels", {}).get("path"),
        cube,
        times,
        cfg,
    )

    resolution = float(cfg["study_area"]["grid_resolution_m"])
    block_size = float(cfg["evaluation"]["spatial_block_size_m"])
    rows, cols = cube.shape[1], cube.shape[2]
    xx, yy = cell_coordinates(rows, cols, resolution)
    block_grid = assign_spatial_blocks(xx.ravel(), yy.ravel(), block_size_m=block_size)
    block_grid = block_grid.reshape(rows, cols)

    cell_blocks = labels_df.apply(lambda r: block_grid[int(r["row"]), int(r["col"])], axis=1).values
    train_blocks, val_blocks, test_blocks = split_blocks(
        cell_blocks,
        train_fraction=cfg["evaluation"].get("train_fraction", 0.6),
        val_fraction=cfg["evaluation"].get("val_fraction", 0.2),
        seed=cfg.get("project", {}).get("seed", 42),
    )
    test_mask = np.array([b in test_blocks for b in cell_blocks])

    det_cfg = {**cfg.get("detection", {}), **cfg.get("study_area", {})}
    det_cfg["spatial_block_size_m"] = block_size
    det_cfg["grid_resolution_m"] = resolution

    methods = cfg["detection"]["methods"]
    method_results: dict[str, Any] = {}
    for method in methods:
        method_results[method] = _evaluate_method_on_cells(
            method,
            labels_df,
            cube,
            times,
            det_cfg,
            test_mask=test_mask,
        )

    full_results = {}
    for method in methods:
        full_results[method] = _evaluate_method_on_cells(
            method, labels_df, cube, times, det_cfg, test_mask=None
        )

    baseline = method_results.get("ndvi_threshold", {})
    candidate = method_results.get("harmonic_persistence", {})
    f1_gain = (candidate.get("persistent_f1") or 0) - (baseline.get("persistent_f1") or 0)

    payload: dict[str, Any] = {
        "experiment_id": cfg.get("experiment_id", "m3_detection"),
        "stack_path": str(stack_path),
        "n_time_steps": len(times),
        "times": times,
        "auto_labeled": auto_labeled,
        "n_labels": len(labels_df),
        "n_test_cells": int(test_mask.sum()),
        "spatial_blocks": {
            "train": len(train_blocks),
            "val": len(val_blocks),
            "test": len(test_blocks),
        },
        "test_set_results": method_results,
        "full_set_results": full_results,
        "go_decision": {
            "proceed_to_m4_temporal_model": bool(
                f1_gain >= cfg["evaluation"].get("min_f1_gain_vs_ndvi_threshold", 0.05)
            ),
            "f1_gain_vs_ndvi_threshold": f1_gain,
            "note": "Auto-labels are weak proxies unless manual labels CSV is supplied.",
        },
    }

    out_dir = Path(cfg["paths"]["results"])
    ensure_dir(out_dir)
    fig_path = _write_comparison_figure(method_results, out_dir / "baseline_f1_comparison.png")
    payload["figure_paths"] = [fig_path]
    save_json(out_dir / "detection_baselines.json", payload)
    ExperimentRegistry().register(cfg.get("experiment_id", "m3"), payload)
    return payload
