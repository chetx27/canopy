from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor


@dataclass
class ForecastResult:
    horizon: int
    point: float
    lower: float
    upper: float
    method: str


def persistence_forecast(series: np.ndarray, horizon: int) -> ForecastResult:
    y = np.asarray(series, dtype=float)
    last = y[np.isfinite(y)][-1]
    return ForecastResult(horizon=horizon, point=last, lower=last, upper=last, method="persistence")


def seasonal_naive_forecast(series: np.ndarray, horizon: int, season_length: int = 12) -> ForecastResult:
    y = np.asarray(series, dtype=float)
    if len(y) <= season_length:
        return persistence_forecast(y, horizon)
    ref = y[-season_length + horizon - 1]
    return ForecastResult(horizon=horizon, point=ref, lower=ref, upper=ref, method="seasonal_naive")


def linear_trend_forecast(series: np.ndarray, horizon: int) -> ForecastResult:
    y = np.asarray(series, dtype=float)
    t = np.arange(len(y), dtype=float)
    mask = np.isfinite(y)
    if mask.sum() < 2:
        return persistence_forecast(y, horizon)
    coef = np.polyfit(t[mask], y[mask], 1)
    pred = np.polyval(coef, len(y) - 1 + horizon)
    resid = y[mask] - np.polyval(coef, t[mask])
    std = np.nanstd(resid)
    return ForecastResult(
        horizon=horizon,
        point=float(pred),
        lower=float(pred - 1.96 * std),
        upper=float(pred + 1.96 * std),
        method="linear_trend",
    )


def gbdt_forecast(
    series: np.ndarray,
    horizon: int,
    max_lags: int = 6,
    quantile_alpha: float = 0.1,
) -> ForecastResult:
    y = np.asarray(series, dtype=float)
    rows = []
    targets = []
    for i in range(max_lags, len(y)):
        window = y[i - max_lags : i]
        if not np.all(np.isfinite(window)) or not np.isfinite(y[i]):
            continue
        rows.append(window)
        targets.append(y[i])
    if len(rows) < 5:
        return linear_trend_forecast(y, horizon)
    x = np.vstack(rows)
    t = np.asarray(targets, dtype=float)
    model = GradientBoostingRegressor(random_state=42, n_estimators=100, max_depth=3)
    model.fit(x, t)
    context = y[-max_lags:].copy()
    context = np.where(np.isfinite(context), context, np.nanmean(y[np.isfinite(y)]))
    for _ in range(horizon):
        pred = model.predict(context.reshape(1, -1))[0]
        context = np.roll(context, -1)
        context[-1] = pred
    resid = t - model.predict(x)
    q = np.quantile(np.abs(resid), 1 - quantile_alpha)
    point = float(context[-1])
    return ForecastResult(
        horizon=horizon,
        point=point,
        lower=point - q,
        upper=point + q,
        method="gbdt",
    )


def run_forecast(method: str, series: np.ndarray, horizon: int, **kwargs) -> ForecastResult:
    if method == "persistence":
        return persistence_forecast(series, horizon)
    if method == "seasonal_naive":
        return seasonal_naive_forecast(series, horizon, season_length=kwargs.get("season_length", 12))
    if method == "linear_trend":
        return linear_trend_forecast(series, horizon)
    if method == "gbdt":
        return gbdt_forecast(series, horizon, max_lags=kwargs.get("max_lags", 6))
    raise ValueError(f"Unknown forecast method: {method}")
