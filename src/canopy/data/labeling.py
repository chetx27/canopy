from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def infer_event_month(series: np.ndarray, times: list[str]) -> int | None:
    y = np.asarray(series, dtype=float)
    valid = np.isfinite(y)
    if valid.sum() < 4:
        return None
    baseline = np.nanmean(y[: max(3, len(y) // 3)])
    for i, val in enumerate(y):
        if np.isfinite(val) and val < baseline - 0.12:
            return i
    return None


def auto_label_cells_from_stack(
    cube: np.ndarray,
    times: list[str],
    n_per_class: int = 50,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    _, rows, cols = cube.shape
    candidates: list[dict[str, Any]] = []
    for row in range(rows):
        for col in range(cols):
            series = cube[:, row, col]
            if np.isfinite(series).sum() < 8:
                continue
            trend = np.polyfit(np.arange(len(series))[np.isfinite(series)], series[np.isfinite(series)], 1)[0]
            seasonal = np.nanstd(series)
            candidates.append({"row": row, "col": col, "trend": trend, "seasonal": seasonal})

    if not candidates:
        raise ValueError("No valid cells in stack for auto-labeling")

    df = pd.DataFrame(candidates)
    stable_pool = df[(df["trend"].abs() < 0.005) & (df["seasonal"] < 0.12)]
    seasonal_pool = df[(df["trend"].abs() < 0.008) & (df["seasonal"] >= 0.12)]
    loss_pool = df[df["trend"] <= -0.008]

    def sample(pool: pd.DataFrame, label: str, n: int) -> list[dict[str, Any]]:
        if pool.empty:
            pool = df.sample(min(n, len(df)), random_state=seed)
        pick = pool.sample(min(n, len(pool)), random_state=int(rng.integers(0, 1_000_000)))
        rows_out = []
        for i, row in pick.iterrows():
            series = cube[:, int(row["row"]), int(row["col"])]
            event_idx = infer_event_month(series, times)
            rows_out.append(
                {
                    "cell_id": f"{label}_{int(row['row'])}_{int(row['col'])}",
                    "label": label,
                    "row": int(row["row"]),
                    "col": int(row["col"]),
                    "event_month": times[event_idx] if event_idx is not None else "",
                }
            )
        return rows_out

    labeled = (
        sample(stable_pool, "stable", n_per_class)
        + sample(seasonal_pool, "seasonal", n_per_class)
        + sample(loss_pool, "persistent_loss", n_per_class)
    )
    return pd.DataFrame(labeled)


def load_detection_labels(
    path: str | None,
    cube: np.ndarray,
    times: list[str],
    cfg: dict[str, Any],
) -> tuple[pd.DataFrame, bool]:
    from pathlib import Path

    n_per = cfg.get("labels", {}).get("n_per_class", 50)
    seed = cfg.get("project", {}).get("seed", 42)
    if path and Path(path).exists():
        df = pd.read_csv(path)
        required = {"cell_id", "label", "row", "col"}
        if not required.issubset(df.columns):
            raise ValueError(f"Labels CSV must contain columns: {required}")
        return df, False
    df = auto_label_cells_from_stack(cube, times, n_per_class=n_per, seed=seed)
    return df, True
