import numpy as np
import pytest

from canopy.detection.baselines import harmonic_persistence_detector, ndvi_threshold_detector
from canopy.evaluation.metrics import binary_detection_metrics, forecast_metrics
from canopy.evaluation.splits import assert_no_future_leakage, assign_spatial_blocks
from canopy.features.indices import ndvi
from canopy.forecasting.baselines import persistence_forecast, seasonal_naive_forecast
from canopy.geospatial.crs import transform_coordinates
from canopy.optimization.engine import CellState, OptimizationConfig, greedy_optimize
from canopy.temporal.harmonic import seasonal_residual_zscore
from canopy.temporal.persistence import persistence_mask


def test_ndvi():
    nir = np.array([100, 200], dtype=float)
    red = np.array([50, 100], dtype=float)
    out = ndvi(nir, red)
    assert np.allclose(out, [1 / 3, 1 / 3])


def test_harmonic_residual():
    t = np.arange(24, dtype=float)
    y = 0.5 + 0.1 * np.sin(2 * np.pi * t / 12.0)
    z, _ = seasonal_residual_zscore(y, t, order=3)
    assert np.all(np.isfinite(z))


def test_persistence_mask():
    flags = np.array([False, True, True, False, True, True, True])
    out = persistence_mask(flags, min_consecutive=2)
    assert out[2]
    assert out[5]


def test_detection_metrics():
    y_true = np.array([True, False, True, False])
    y_pred = np.array([True, False, False, True])
    m = binary_detection_metrics(y_true, y_pred)
    assert 0.0 <= m.f1 <= 1.0


def test_forecast_metrics():
    y = np.array([1.0, 2.0, 3.0])
    p = np.array([1.1, 1.9, 3.2])
    m = forecast_metrics(y, p)
    assert m["mae"] < 0.5


def test_spatial_blocks():
    xs = np.array([0, 100, 600])
    ys = np.array([0, 100, 600])
    blocks = assign_spatial_blocks(xs, ys, block_size_m=500.0)
    assert len(np.unique(blocks)) >= 2


def test_no_future_leakage():
    with pytest.raises(ValueError):
        assert_no_future_leakage(np.array([2, 3]), np.array([1, 2]))


def test_crs_transform():
    x, y = transform_coordinates(np.array([0.0]), np.array([0.0]), "EPSG:4326", "EPSG:32643")
    assert x.size == 1 and y.size == 1


def test_optimizer_budget():
    cells = [
        CellState(
            cell_id=i,
            lst=35.0,
            canopy=0.2,
            population=100.0,
            maturity=0.2,
            water_feasible=True,
            plantable=True,
            preserve_candidate=False,
            exposure=100.0,
        )
        for i in range(10)
    ]
    cfg = OptimizationConfig(budget_units=3, water_budget_m3=1000)
    res = greedy_optimize(cells, cfg, plant_only=True)
    assert res.total_cost <= 3
    assert len(res.selected) <= 3


def test_persistence_detector_on_synthetic_loss():
    t = np.arange(18, dtype=float)
    y = np.full(18, 0.62)
    y[12:] = 0.18
    det = harmonic_persistence_detector(y, t, z_threshold=1.5, persistence_min_months=2, order=2)
    assert det.flags.any()


def test_forecast_baselines():
    series = np.linspace(0.4, 0.6, 24)
    p = persistence_forecast(series, horizon=1)
    s = seasonal_naive_forecast(series, horizon=1)
    assert np.isfinite(p.point)
    assert np.isfinite(s.point)
