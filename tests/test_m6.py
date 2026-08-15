import numpy as np
import pytest

from canopy.forecasting.baselines import run_forecast
from canopy.forecasting.evaluation import aggregate_forecast_results, evaluate_series_forecast


def test_evaluate_series_forecast():
    series = np.linspace(0.4, 0.7, 18)
    out = evaluate_series_forecast(series, horizon=3, method="persistence")
    assert out is not None
    assert out["abs_error"] >= 0


def test_aggregate_forecast_results():
    rows = [{"abs_error": 0.1, "squared_error": 0.01, "coverage_80": 1.0}] * 5
    agg = aggregate_forecast_results(rows)
    assert agg["n"] == 5
    assert agg["mae"] == pytest.approx(0.1)


def test_run_forecast_methods():
    series = np.linspace(0.4, 0.6, 24)
    for method in ["persistence", "seasonal_naive", "linear_trend", "gbdt"]:
        result = run_forecast(method, series, horizon=2)
        assert np.isfinite(result.point)
