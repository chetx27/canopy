from __future__ import annotations

import numpy as np

from canopy.temporal.harmonic import fit_harmonic_coefficients, predict_harmonic


def series_features(
    series: np.ndarray,
    times: np.ndarray | None = None,
    max_lags: int = 3,
    harmonic_order: int = 3,
) -> dict[str, float]:
    y = np.asarray(series, dtype=float)
    t = np.arange(len(y), dtype=float) if times is None else np.asarray(times, dtype=float)
    valid = np.isfinite(y)
    feats: dict[str, float] = {
        "valid_fraction": float(valid.mean()) if y.size else 0.0,
        "ndvi_mean": float(np.nanmean(y)) if valid.any() else 0.0,
        "ndvi_std": float(np.nanstd(y)) if valid.sum() > 1 else 0.0,
        "ndvi_min": float(np.nanmin(y)) if valid.any() else 0.0,
        "ndvi_max": float(np.nanmax(y)) if valid.any() else 0.0,
        "ndvi_range": 0.0,
        "trend": 0.0,
        "recent_delta": 0.0,
        "harmonic_residual_std": 0.0,
    }
    if valid.any():
        feats["ndvi_range"] = float(np.nanmax(y) - np.nanmin(y))
    if valid.sum() >= 2:
        feats["trend"] = float(np.polyfit(t[valid], y[valid], 1)[0])
    if valid.sum() >= max_lags + 1:
        feats["recent_delta"] = float(y[valid][-1] - y[valid][-1 - max_lags])
    for lag in range(1, max_lags + 1):
        delta = np.nanmean(y[lag:] - y[:-lag]) if len(y) > lag else 0.0
        feats[f"lag_delta_{lag}"] = float(delta) if np.isfinite(delta) else 0.0
    coef = fit_harmonic_coefficients(y, t, order=harmonic_order)
    if np.all(np.isfinite(coef)):
        pred = predict_harmonic(coef, t, t.min(), t.max(), order=harmonic_order)
        resid = y - pred
        feats["harmonic_residual_std"] = float(np.nanstd(resid[valid]))
    month_sin = np.sin(2 * np.pi * t / 12.0)
    month_cos = np.cos(2 * np.pi * t / 12.0)
    if valid.sum() >= 3:
        feats["seasonal_sin_corr"] = float(np.corrcoef(y[valid], month_sin[valid])[0, 1])
        feats["seasonal_cos_corr"] = float(np.corrcoef(y[valid], month_cos[valid])[0, 1])
    else:
        feats["seasonal_sin_corr"] = 0.0
        feats["seasonal_cos_corr"] = 0.0
    return feats


def feature_names(max_lags: int = 3) -> list[str]:
    base = [
        "valid_fraction",
        "ndvi_mean",
        "ndvi_std",
        "ndvi_min",
        "ndvi_max",
        "ndvi_range",
        "trend",
        "recent_delta",
        "harmonic_residual_std",
        "seasonal_sin_corr",
        "seasonal_cos_corr",
    ]
    base += [f"lag_delta_{lag}" for lag in range(1, max_lags + 1)]
    return base


def series_to_vector(
    series: np.ndarray,
    times: np.ndarray | None = None,
    max_lags: int = 3,
    feature_subset: list[str] | None = None,
) -> np.ndarray:
    feats = series_features(series, times, max_lags=max_lags)
    names = feature_subset or feature_names(max_lags=max_lags)
    vec = np.array([feats.get(n, 0.0) for n in names], dtype=float)
    return np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0)


def window_features(series: np.ndarray, end_idx: int, window: int = 6, max_lags: int = 3) -> np.ndarray:
    start = max(0, end_idx - window + 1)
    window_series = series[start : end_idx + 1]
    t = np.arange(len(window_series), dtype=float)
    return series_to_vector(window_series, t, max_lags=max_lags)
