from __future__ import annotations

import numpy as np


def fit_harmonic_coefficients(
    values: np.ndarray,
    times: np.ndarray,
    order: int = 3,
) -> np.ndarray:
    t = np.asarray(times, dtype=float)
    y = np.asarray(values, dtype=float)
    mask = np.isfinite(y)
    if mask.sum() < (2 * order + 2):
        return np.full(2 * order + 1, np.nan)
    t = t[mask]
    y = y[mask]
    t_norm = (t - t.min()) / max(t.max() - t.min(), 1.0)
    design = [np.ones_like(t_norm)]
    for k in range(1, order + 1):
        design.append(np.sin(2 * np.pi * k * t_norm))
        design.append(np.cos(2 * np.pi * k * t_norm))
    x = np.column_stack(design)
    coef, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    return coef


def predict_harmonic(
    coefficients: np.ndarray,
    times: np.ndarray,
    t_min: float,
    t_max: float,
    order: int = 3,
) -> np.ndarray:
    t = np.asarray(times, dtype=float)
    t_norm = (t - t_min) / max(t_max - t_min, 1.0)
    pred = np.full_like(t_norm, coefficients[0], dtype=float)
    idx = 1
    for k in range(1, order + 1):
        pred += coefficients[idx] * np.sin(2 * np.pi * k * t_norm)
        pred += coefficients[idx + 1] * np.cos(2 * np.pi * k * t_norm)
        idx += 2
    return pred


def seasonal_residual_zscore(
    values: np.ndarray,
    times: np.ndarray,
    order: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
    y = np.asarray(values, dtype=float)
    t = np.asarray(times, dtype=float)
    coef = fit_harmonic_coefficients(y, t, order=order)
    if not np.all(np.isfinite(coef)):
        z = np.full_like(y, np.nan)
        return z, coef
    pred = predict_harmonic(coef, t, t.min(), t.max(), order=order)
    resid = y - pred
    std = np.nanstd(resid)
    if std == 0 or np.isnan(std):
        z = np.zeros_like(resid)
    else:
        z = resid / std
    return z, coef
