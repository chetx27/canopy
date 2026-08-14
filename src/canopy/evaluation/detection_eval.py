from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from canopy.data.labeling import infer_event_month
from canopy.detection.baselines import detection_index, run_detector
from canopy.detection.temporal_ml import TemporalGBMModel, temporal_gbm_detector
from canopy.evaluation.metrics import binary_detection_metrics, spatial_block_bootstrap_mean
from canopy.temporal.persistence import detection_delay_days


def detector_kwargs(det_cfg: dict[str, Any]) -> dict[str, Any]:
    keys = {
        "ndvi_threshold",
        "delta_threshold",
        "anomaly_z_threshold",
        "persistence_min_months",
        "harmonic_order",
        "history_fraction",
    }
    return {k: v for k, v in det_cfg.items() if k in keys}


def evaluate_method_on_cells(
    method: str,
    labels_df: pd.DataFrame,
    cube: np.ndarray,
    times: list[str],
    det_cfg: dict[str, Any],
    test_mask: np.ndarray | None = None,
    ml_model: TemporalGBMModel | None = None,
) -> dict[str, Any]:
    y_true = []
    y_pred = []
    stable_mask = []
    delays = []
    block_ids = []
    resolution = det_cfg.get("grid_resolution_m", 30.0)
    block_size = det_cfg.get("spatial_block_size_m", 500.0)
    det_kwargs_local = detector_kwargs(det_cfg)

    for pos, (_, row) in enumerate(labels_df.iterrows()):
        if test_mask is not None and not test_mask[pos]:
            continue
        series = cube[:, int(row["row"]), int(row["col"])]
        if not np.isfinite(series).any():
            continue
        t_arr = np.arange(len(times), dtype=float)
        if method in {"temporal_gbm", "temporal_sequence_gbm"}:
            if ml_model is None:
                continue
            det = temporal_gbm_detector(
                series,
                t_arr,
                ml_model,
                window=det_cfg.get("sequence_window", 6),
            )
        else:
            det = run_detector(method, series, t_arr, **det_kwargs_local)
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
    f1_boot = spatial_block_bootstrap_mean(cell_scores, np.array(block_ids), n_boot=200, seed=42)
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
