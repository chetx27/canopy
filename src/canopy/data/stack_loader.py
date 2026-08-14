from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr


def load_monthly_stack(path: str | Path) -> xr.Dataset:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Monthly stack not found: {path}. Run M2 first.")
    return xr.open_dataset(path)


def stack_to_cube(ds: xr.Dataset, nodata: float = -9999.0) -> tuple[np.ndarray, list[str]]:
    ndvi = ds["ndvi"].values.astype(float)
    ndvi[ndvi == nodata] = np.nan
    times = [str(t) for t in ds.coords["time"].values.tolist()]
    if len(times) == ndvi.shape[0]:
        return ndvi, times
    times = [str(x)[:7] for x in ds.coords["time"].values.tolist()]
    return ndvi, times


def extract_cell_series(
    cube: np.ndarray,
    row: int,
    col: int,
    min_valid: int = 6,
) -> np.ndarray | None:
    series = cube[:, row, col]
    if np.isfinite(series).sum() < min_valid:
        return None
    return series


def cell_coordinates(rows: int, cols: int, resolution_m: float = 30.0) -> tuple[np.ndarray, np.ndarray]:
    xs = np.arange(cols, dtype=float) * resolution_m + resolution_m / 2.0
    ys = np.arange(rows, dtype=float) * resolution_m + resolution_m / 2.0
    xx, yy = np.meshgrid(xs, ys)
    return xx, yy
