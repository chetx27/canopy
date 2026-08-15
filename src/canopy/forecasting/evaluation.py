from __future__ import annotations

from typing import Any

import numpy as np

from canopy.evaluation.metrics import forecast_metrics, interval_coverage
from canopy.forecasting.baselines import run_forecast


def holdout_indices(n_timesteps: int, horizon: int, min_history: int = 8) -> int | None:
    train_end = n_timesteps - horizon
    if train_end < min_history:
        return None
    return train_end


def evaluate_series_forecast(
    series: np.ndarray,
    horizon: int,
    method: str,
    kwargs: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    kwargs = kwargs or {}
    idx = holdout_indices(len(series), horizon, min_history=kwargs.get("min_history", 8))
    if idx is None:
        return None
    history = series[:idx]
    target = series[idx + horizon - 1]
    if not np.isfinite(target):
        return None
    result = run_forecast(method, history, horizon, **kwargs)
    err = abs(result.point - target)
    return {
        "horizon": horizon,
        "method": method,
        "target": float(target),
        "point": float(result.point),
        "lower": float(result.lower),
        "upper": float(result.upper),
        "abs_error": float(err),
        "squared_error": float(err**2),
        "coverage_80": interval_coverage(float(target), result.lower, result.upper)
        if np.isfinite(result.lower) and np.isfinite(result.upper)
        else 0.0,
    }


def aggregate_forecast_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n": 0, "mae": float("nan"), "rmse": float("nan"), "coverage_80": float("nan")}
    errors = np.array([r["abs_error"] for r in rows], dtype=float)
    sq = np.array([r["squared_error"] for r in rows], dtype=float)
    cov = np.array([r["coverage_80"] for r in rows], dtype=float)
    return {
        "n": len(rows),
        "mae": float(np.mean(errors)),
        "rmse": float(np.sqrt(np.mean(sq))),
        "coverage_80": float(np.mean(cov)),
    }


def evaluate_stack_forecasts(
    cube: np.ndarray,
    cell_rows: np.ndarray,
    cell_cols: np.ndarray,
    horizons: list[int],
    methods: list[str],
    forecast_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    forecast_kwargs = forecast_kwargs or {}
    out: dict[str, Any] = {}
    for method in methods:
        out[method] = {}
        for horizon in horizons:
            rows = []
            for row, col in zip(cell_rows, cell_cols):
                series = cube[:, int(row), int(col)]
                row_result = evaluate_series_forecast(series, horizon, method, forecast_kwargs)
                if row_result is not None:
                    rows.append(row_result)
            out[method][str(horizon)] = aggregate_forecast_results(rows)
    return out
