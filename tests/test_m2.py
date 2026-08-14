import numpy as np

from canopy.data.qc import build_qc_report, compute_month_qc
from canopy.data.preprocess import harmonize_monthly_stack, month_list
from canopy.data.synthetic import generate_synthetic_pilot_stack


def test_month_list():
    months = month_list("2023-01-01", "2023-03-31")
    assert months == ["2023-01", "2023-02", "2023-03"]


def test_compute_month_qc():
    ndvi = np.full((10, 10), 0.5)
    ndvi[0:3, :] = np.nan
    qc = compute_month_qc(ndvi, "2023-07", n_observations=2, monsoon_months={7})
    assert qc.valid_pixel_fraction == 0.7
    assert qc.cloud_gap is False


def test_synthetic_stack_has_monsoon_gaps():
    cfg = {
        "project": {"seed": 42},
        "temporal": {"start_date": "2023-01-01", "end_date": "2023-12-31"},
    }
    monthly, counts = generate_synthetic_pilot_stack(cfg)
    assert len(monthly) == 12
    july = monthly["2023-07"]
    valid_frac = np.isfinite(july).mean()
    assert valid_frac < 0.8
    assert counts["2023-07"] < counts["2023-01"]


def test_build_qc_report_go():
    cfg = {
        "study_area": {"aoi_path": "data/external/bengaluru_pilot_aoi.geojson", "grid_resolution_m": 30},
        "project": {"crs": "EPSG:32643", "seed": 42},
        "temporal": {"start_date": "2023-01-01", "end_date": "2023-06-30"},
        "preprocessing": {"nodata": -9999},
        "qc": {"monsoon_months": [6, 7, 8, 9, 10], "min_months_required": 4, "max_missing_fraction": 0.6},
    }
    monthly, counts = generate_synthetic_pilot_stack(cfg)
    monthly = harmonize_monthly_stack(monthly)
    report = build_qc_report(monthly, counts, cfg, synthetic=True)
    assert report.n_months == 6
    assert report.alignment_ok
    assert "proceed_to_m3_detection" in report.go_decision


def test_harmonize_mismatched_shapes():
    monthly = {"2023-01": np.ones((5, 5)), "2023-02": np.ones((4, 4))}
    out = harmonize_monthly_stack(monthly)
    assert out["2023-01"].shape == out["2023-02"].shape
