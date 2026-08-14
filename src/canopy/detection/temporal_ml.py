from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier

from canopy.detection.baselines import DetectionResult
from canopy.temporal.features import feature_names, series_to_vector, window_features
from canopy.temporal.persistence import persistence_mask


@dataclass
class TemporalGBMModel:
    cell_classifier: GradientBoostingClassifier
    sequence_classifier: GradientBoostingClassifier | None
    feature_names: list[str]
    probability_threshold: float = 0.5
    persistence_min_months: int = 2


def train_temporal_gbm(
    x_train: np.ndarray,
    y_train: np.ndarray,
    seed: int = 42,
) -> GradientBoostingClassifier:
    model = GradientBoostingClassifier(
        random_state=seed,
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
    )
    model.fit(x_train, y_train)
    return model


def train_sequence_gbm(
    x_seq: np.ndarray,
    y_seq: np.ndarray,
    seed: int = 42,
) -> GradientBoostingClassifier:
    model = GradientBoostingClassifier(
        random_state=seed,
        n_estimators=150,
        max_depth=3,
        learning_rate=0.05,
    )
    model.fit(x_seq, y_seq)
    return model


def build_cell_training_data(
    cube: np.ndarray,
    labels_df: Any,
    times: list[str],
    train_mask: np.ndarray,
    max_lags: int = 3,
    feature_subset: list[str] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    names = feature_subset or feature_names(max_lags=max_lags)
    rows = []
    targets = []
    t_arr = np.arange(len(times), dtype=float)
    for pos, (_, row) in enumerate(labels_df.iterrows()):
        if not train_mask[pos]:
            continue
        series = cube[:, int(row["row"]), int(row["col"])]
        if np.isfinite(series).sum() < 6:
            continue
        rows.append(series_to_vector(series, t_arr, max_lags=max_lags, feature_subset=names))
        targets.append(1 if row["label"] == "persistent_loss" else 0)
    if not rows:
        raise ValueError("No training rows available for temporal GBM")
    return np.vstack(rows), np.array(targets, dtype=int)


def build_sequence_training_data(
    cube: np.ndarray,
    labels_df: Any,
    times: list[str],
    train_mask: np.ndarray,
    window: int = 6,
) -> tuple[np.ndarray, np.ndarray]:
    rows = []
    targets = []
    for pos, (_, row) in enumerate(labels_df.iterrows()):
        if not train_mask[pos]:
            continue
        series = cube[:, int(row["row"]), int(row["col"])]
        if not np.isfinite(series).any():
            continue
        positive_months = set()
        if row["label"] == "persistent_loss":
            if pd_notna(row.get("event_month")) and str(row.get("event_month")) in times:
                start = times.index(str(row["event_month"]))
                positive_months = set(range(start, len(times)))
            else:
                positive_months = set(range(len(times) // 2, len(times)))
        for t_idx in range(len(times)):
            if not np.isfinite(series[t_idx]):
                continue
            rows.append(window_features(series, t_idx, window=window))
            targets.append(1 if t_idx in positive_months else 0)
    if not rows:
        raise ValueError("No sequence training rows available")
    return np.vstack(rows), np.array(targets, dtype=int)


def pd_notna(val: Any) -> bool:
    if val is None:
        return False
    try:
        import pandas as pd

        return bool(pd.notna(val) and str(val).strip() != "")
    except Exception:
        return bool(val)


def fit_temporal_models(
    cube: np.ndarray,
    labels_df: Any,
    times: list[str],
    train_mask: np.ndarray,
    cfg: dict[str, Any],
) -> TemporalGBMModel:
    max_lags = cfg.get("max_lags", 3)
    feature_subset = cfg.get("feature_subset")
    seed = cfg.get("seed", 42)
    x_train, y_train = build_cell_training_data(
        cube, labels_df, times, train_mask, max_lags=max_lags, feature_subset=feature_subset
    )
    cell_model = train_temporal_gbm(x_train, y_train, seed=seed)
    seq_model = None
    if cfg.get("train_sequence_model", True):
        x_seq, y_seq = build_sequence_training_data(
            cube, labels_df, times, train_mask, window=cfg.get("sequence_window", 6)
        )
        seq_model = train_sequence_gbm(x_seq, y_seq, seed=seed)
    names = feature_subset or feature_names(max_lags=max_lags)
    return TemporalGBMModel(
        cell_classifier=cell_model,
        sequence_classifier=seq_model,
        feature_names=names,
        probability_threshold=cfg.get("probability_threshold", 0.5),
        persistence_min_months=cfg.get("persistence_min_months", 2),
    )


def predict_cell(model: TemporalGBMModel, series: np.ndarray, times: np.ndarray) -> tuple[bool, float]:
    x = series_to_vector(series, times, max_lags=3, feature_subset=model.feature_names).reshape(1, -1)
    proba = float(model.cell_classifier.predict_proba(x)[0, 1])
    return proba >= model.probability_threshold, proba


def predict_sequence_flags(model: TemporalGBMModel, series: np.ndarray, window: int = 6) -> DetectionResult:
    flags = np.zeros(len(series), dtype=bool)
    scores = np.zeros(len(series), dtype=float)
    if model.sequence_classifier is None:
        return DetectionResult(flags=flags, scores=scores, method="temporal_sequence_gbm")
    for t_idx in range(len(series)):
        if not np.isfinite(series[t_idx]):
            continue
        x = window_features(series, t_idx, window=window).reshape(1, -1)
        proba = float(model.sequence_classifier.predict_proba(x)[0, 1])
        scores[t_idx] = proba
        flags[t_idx] = proba >= model.probability_threshold
    persistent = persistence_mask(flags, min_consecutive=model.persistence_min_months)
    return DetectionResult(flags=persistent, scores=scores, method="temporal_sequence_gbm")


def temporal_gbm_detector(
    series: np.ndarray,
    times: np.ndarray,
    model: TemporalGBMModel,
    window: int = 6,
) -> DetectionResult:
    cell_flag, cell_score = predict_cell(model, series, times)
    if model.sequence_classifier is not None:
        seq_result = predict_sequence_flags(model, series, window=window)
        flags = seq_result.flags if seq_result.flags.any() else np.array([cell_flag] * len(series))
        scores = seq_result.scores if seq_result.scores.any() else np.full(len(series), cell_score)
    else:
        flags = np.array([cell_flag] * len(series), dtype=bool)
        scores = np.full(len(series), cell_score)
    return DetectionResult(flags=flags, scores=scores, method="temporal_gbm")
