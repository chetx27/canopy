import numpy as np
import pandas as pd
import pytest

from canopy.data.annotation import (
    cohen_kappa,
    generate_annotation_batch,
    inter_rater_report,
    merge_rater_labels,
    simulate_rater_b_from_reference,
)
from canopy.temporal.features import series_features, series_to_vector


def _cube(months=12, rows=30, cols=30):
    rng = np.random.default_rng(1)
    cube = rng.uniform(0.3, 0.7, size=(months, rows, cols))
    times = [f"2023-{m:02d}" for m in range(1, months + 1)]
    return cube, times


def test_series_features():
    y = np.array([0.5, 0.55, 0.52, 0.48, 0.45, 0.42], dtype=float)
    feats = series_features(y)
    assert "trend" in feats
    assert feats["ndvi_mean"] > 0


def test_series_to_vector():
    y = np.linspace(0.4, 0.6, 10)
    vec = series_to_vector(y)
    assert vec.ndim == 1
    assert vec.size > 5


def test_annotation_batch_size():
    cube, times = _cube()
    batch = generate_annotation_batch(cube, times, n_total=120, seed=0)
    assert len(batch) <= 120
    assert "label" in batch.columns


def test_cohen_kappa_perfect():
    a = pd.Series(["stable", "seasonal", "persistent_loss"])
    b = pd.Series(["stable", "seasonal", "persistent_loss"])
    assert cohen_kappa(a, b) == pytest.approx(1.0)


def test_inter_rater_report():
    df = pd.DataFrame(
        {
            "cell_id": ["a", "b", "c"],
            "row": [1, 2, 3],
            "col": [1, 2, 3],
            "label": ["stable", "seasonal", "persistent_loss"],
        }
    )
    sim = simulate_rater_b_from_reference(df, agreement_rate=1.0, seed=0)
    sim_a = sim[["cell_id", "row", "col", "label_a"]].rename(columns={"label_a": "label"})
    sim_b = sim[["cell_id", "row", "col", "label_b"]].rename(columns={"label_b": "label"})
    report = inter_rater_report(sim_a, sim_b)
    assert report["overall_kappa"] == pytest.approx(1.0)


def test_merge_rater_labels():
    df_a = pd.DataFrame(
        {
            "cell_id": ["a", "b"],
            "row": [1, 2],
            "col": [1, 2],
            "label": ["stable", "persistent_loss"],
            "event_month": ["", "2023-08"],
        }
    )
    df_b = pd.DataFrame(
        {
            "cell_id": ["a", "b"],
            "row": [1, 2],
            "col": [1, 2],
            "label": ["stable", "persistent_loss"],
            "event_month": ["", "2023-08"],
        }
    )
    merged, meta = merge_rater_labels(df_a, df_b)
    assert len(merged) == 2
    assert meta["n_merged_labels"] == 2


def test_temporal_gbm_train_smoke():
    from canopy.detection.temporal_ml import build_cell_training_data, train_temporal_gbm

    cube, times = _cube()
    labels = pd.DataFrame(
        {
            "cell_id": [f"c{i}" for i in range(6)],
            "label": ["stable", "stable", "seasonal", "seasonal", "persistent_loss", "persistent_loss"],
            "row": [1, 2, 3, 4, 5, 6],
            "col": [1, 2, 3, 4, 5, 6],
        }
    )
    train_mask = np.array([True] * 6)
    x, y = build_cell_training_data(cube, labels, times, train_mask)
    model = train_temporal_gbm(x, y, seed=0)
    assert hasattr(model, "predict_proba")
