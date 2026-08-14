from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from canopy.temporal.harmonic import fit_harmonic_coefficients, predict_harmonic, seasonal_residual_zscore
from canopy.temporal.persistence import first_detection_index, persistence_mask


@dataclass
class DetectionResult:
    flags: np.ndarray
    scores: np.ndarray
    method: str


def ndvi_threshold_detector(
    ndvi_series: np.ndarray,
    threshold: float = 0.25,
) -> DetectionResult:
    y = np.asarray(ndvi_series, dtype=float)
    flags = y < threshold
    flags = flags & np.isfinite(y)
    scores = threshold - y
    return DetectionResult(flags=flags, scores=scores, method="ndvi_threshold")


def bi_temporal_delta_detector(
    ndvi_series: np.ndarray,
    delta_threshold: float = -0.15,
) -> DetectionResult:
    y = np.asarray(ndvi_series, dtype=float)
    flags = np.zeros_like(y, dtype=bool)
    scores = np.zeros_like(y, dtype=float)
    for i in range(1, len(y)):
        if np.isfinite(y[i]) and np.isfinite(y[i - 1]):
            delta = y[i] - y[i - 1]
            scores[i] = -delta
            flags[i] = delta <= delta_threshold
    return DetectionResult(flags=flags, scores=scores, method="bi_temporal_delta")


def harmonic_persistence_detector(
    ndvi_series: np.ndarray,
    times: np.ndarray,
    z_threshold: float = 2.0,
    persistence_min_months: int = 2,
    order: int = 3,
    history_fraction: float = 0.6,
) -> DetectionResult:
    y = np.asarray(ndvi_series, dtype=float)
    t = np.asarray(times, dtype=float)
    split = max(order * 2 + 2, int(len(y) * history_fraction))
    history_y = y[:split]
    history_t = t[:split]
    z = np.full_like(y, np.nan)
    coef = fit_harmonic_coefficients(history_y, history_t, order=order)
    if np.all(np.isfinite(coef)):
        pred_hist = predict_harmonic(coef, history_t, history_t.min(), history_t.max(), order=order)
        resid_hist = history_y - pred_hist
        std = np.nanstd(resid_hist)
        if std == 0 or np.isnan(std):
            std = 1.0
        for i in range(split, len(y)):
            pred_i = predict_harmonic(coef, np.array([t[i]]), history_t.min(), history_t.max(), order=order)[0]
            if np.isfinite(y[i]):
                z[i] = (y[i] - pred_i) / std
    else:
        z, _ = seasonal_residual_zscore(y, t, order=order)
    anomaly = (z <= -z_threshold) & np.isfinite(z)
    persistent = persistence_mask(anomaly, min_consecutive=persistence_min_months)
    scores = np.where(np.isfinite(z), -z, np.nan)
    return DetectionResult(flags=persistent, scores=scores, method="harmonic_persistence")


def bfast_monitor_style_detector(
    ndvi_series: np.ndarray,
    history_fraction: float = 0.6,
    z_threshold: float = 2.0,
) -> DetectionResult:
    y = np.asarray(ndvi_series, dtype=float)
    split = max(2, int(len(y) * history_fraction))
    history = y[:split]
    monitor = y[split:]
    mu = np.nanmean(history)
    sigma = np.nanstd(history)
    flags = np.zeros_like(y, dtype=bool)
    scores = np.zeros_like(y, dtype=float)
    if sigma == 0 or np.isnan(sigma):
        return DetectionResult(flags=flags, scores=scores, method="bfast_monitor_style")
    for i, val in enumerate(monitor, start=split):
        if np.isfinite(val):
            z = (val - mu) / sigma
            scores[i] = -z
            flags[i] = z <= -z_threshold
    return DetectionResult(flags=flags, scores=scores, method="bfast_monitor_style")


def run_detector(method: str, ndvi_series: np.ndarray, times: np.ndarray, **kwargs) -> DetectionResult:
    if method == "ndvi_threshold":
        return ndvi_threshold_detector(ndvi_series, threshold=kwargs.get("ndvi_threshold", 0.25))
    if method == "bi_temporal_delta":
        return bi_temporal_delta_detector(ndvi_series, delta_threshold=kwargs.get("delta_threshold", -0.15))
    if method == "harmonic_persistence":
        return harmonic_persistence_detector(
            ndvi_series,
            times,
            z_threshold=kwargs.get("anomaly_z_threshold", 2.0),
            persistence_min_months=kwargs.get("persistence_min_months", 2),
            order=kwargs.get("harmonic_order", 3),
        )
    if method == "bfast_monitor_style":
        return bfast_monitor_style_detector(
            ndvi_series,
            history_fraction=kwargs.get("history_fraction", 0.6),
            z_threshold=kwargs.get("anomaly_z_threshold", 2.0),
        )
    raise ValueError(f"Unknown detector method: {method}")


def detection_index(result: DetectionResult) -> int | None:
    return first_detection_index(result.flags)
