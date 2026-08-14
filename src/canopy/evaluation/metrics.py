from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score


@dataclass
class DetectionMetrics:
    precision: float
    recall: float
    f1: float
    false_positive_rate: float
    detection_delays_days: list[float]


def binary_detection_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    stable_mask: np.ndarray | None = None,
) -> DetectionMetrics:
    y_true = np.asarray(y_true, dtype=bool)
    y_pred = np.asarray(y_pred, dtype=bool)
    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    if stable_mask is None:
        stable_mask = ~y_true
    stable_mask = np.asarray(stable_mask, dtype=bool)
    fp = np.sum(y_pred & stable_mask)
    fpr = float(fp / max(np.sum(stable_mask), 1))
    return DetectionMetrics(
        precision=precision,
        recall=recall,
        f1=f1,
        false_positive_rate=fpr,
        detection_delays_days=[],
    )


def forecast_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    if mask.sum() == 0:
        return {"mae": float("nan"), "rmse": float("nan")}
    err = y_true[mask] - y_pred[mask]
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err**2)))
    return {"mae": mae, "rmse": rmse}


def interval_coverage(y_true: float, lower: float, upper: float) -> float:
    return float(lower <= y_true <= upper)


def spatial_block_bootstrap_mean(
    values: np.ndarray,
    block_ids: np.ndarray,
    n_boot: int = 200,
    seed: int = 42,
) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    values = np.asarray(values, dtype=float)
    block_ids = np.asarray(block_ids)
    unique = np.unique(block_ids)
    means = []
    for _ in range(n_boot):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        mask = np.isin(block_ids, sampled)
        if mask.sum() == 0:
            continue
        means.append(np.nanmean(values[mask]))
    if not means:
        m = float(np.nanmean(values))
        return m, m, m
    arr = np.asarray(means)
    return float(np.mean(arr)), float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))
