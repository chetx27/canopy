from __future__ import annotations

import numpy as np


def spatial_conformal_interval(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    coords: np.ndarray,
    test_coord: np.ndarray,
    alpha: float = 0.1,
    bandwidth_m: float = 1000.0,
) -> tuple[float, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    coords = np.asarray(coords, dtype=float)
    test_coord = np.asarray(test_coord, dtype=float)
    residuals = np.abs(y_true - y_pred)
    dist = np.linalg.norm(coords - test_coord, axis=1)
    weights = np.exp(-(dist**2) / (2 * bandwidth_m**2))
    if weights.sum() == 0:
        q = np.quantile(residuals, 1 - alpha)
    else:
        order = np.argsort(residuals)
        residuals_sorted = residuals[order]
        weights_sorted = weights[order]
        weights_sorted = weights_sorted / weights_sorted.sum()
        cdf = np.cumsum(weights_sorted)
        idx = np.searchsorted(cdf, 1 - alpha)
        idx = min(idx, len(residuals_sorted) - 1)
        q = residuals_sorted[idx]
    pred = float(y_pred[np.argmin(dist)])
    return pred - q, pred + q


def ranking_stability_kendall(
    base_ranking: list[int],
    perturbed_ranking: list[int],
) -> float:
    from scipy.stats import kendalltau

    common = sorted(set(base_ranking) & set(perturbed_ranking))
    if len(common) < 2:
        return 1.0
    a = [base_ranking.index(x) for x in common]
    b = [perturbed_ranking.index(x) for x in common]
    tau, _ = kendalltau(a, b)
    return float(tau if not np.isnan(tau) else 0.0)
