from __future__ import annotations

import numpy as np


def assign_spatial_blocks(
    xs: np.ndarray,
    ys: np.ndarray,
    block_size_m: float = 500.0,
) -> np.ndarray:
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    bx = np.floor(xs / block_size_m).astype(int)
    by = np.floor(ys / block_size_m).astype(int)
    return bx * 100000 + by


def split_blocks(
    block_ids: np.ndarray,
    train_fraction: float = 0.6,
    val_fraction: float = 0.2,
    seed: int = 42,
) -> tuple[set[int], set[int], set[int]]:
    rng = np.random.default_rng(seed)
    unique = np.unique(block_ids)
    rng.shuffle(unique)
    n = len(unique)
    n_train = int(n * train_fraction)
    n_val = int(n * val_fraction)
    train = set(unique[:n_train].tolist())
    val = set(unique[n_train : n_train + n_val].tolist())
    test = set(unique[n_train + n_val :].tolist())
    return train, val, test


def assert_no_future_leakage(feature_times: np.ndarray, label_times: np.ndarray) -> None:
    if np.any(feature_times > label_times):
        raise ValueError("Future observations detected in feature construction")
