from __future__ import annotations

import numpy as np


def persistence_mask(
    anomaly_flags: np.ndarray,
    min_consecutive: int = 2,
) -> np.ndarray:
    arr = np.asarray(anomaly_flags, dtype=bool)
    if arr.ndim != 1:
        raise ValueError("anomaly_flags must be 1D time series")
    out = np.zeros_like(arr, dtype=bool)
    run = 0
    for i, flag in enumerate(arr):
        run = run + 1 if flag else 0
        if run >= min_consecutive:
            out[i - min_consecutive + 1 : i + 1] = True
    return out


def first_detection_index(flags: np.ndarray) -> int | None:
    idx = np.where(np.asarray(flags, dtype=bool))[0]
    return int(idx[0]) if idx.size else None


def detection_delay_days(
    detection_index: int | None,
    event_index: int,
    days_per_step: float = 30.0,
) -> float | None:
    if detection_index is None:
        return None
    return float(max(0, detection_index - event_index) * days_per_step)
