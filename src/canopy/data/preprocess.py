from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import calculate_default_transform, reproject


SCL_CLOUD = {3, 8, 9, 10, 11}


def month_list(start: str, end: str) -> list[str]:
    import pandas as pd

    periods = pd.period_range(start=start, end=end, freq="M")
    return [p.strftime("%Y-%m") for p in periods]


def apply_scl_cloud_mask(
    ndvi: np.ndarray,
    scl: np.ndarray | None,
    cloud_classes: set[int] | None = None,
    nodata: float = -9999.0,
) -> np.ndarray:
    out = np.asarray(ndvi, dtype=float).copy()
    if scl is None:
        return out
    classes = cloud_classes or SCL_CLOUD
    cloud = np.isin(scl.astype(int), list(classes))
    out[cloud] = nodata
    return out


def reproject_to_crs(
    array: np.ndarray,
    src_transform,
    src_crs: str,
    dst_crs: str,
    dst_shape: tuple[int, int] | None = None,
    resolution: float | None = None,
    resampling: Resampling = Resampling.bilinear,
    nodata: float = -9999.0,
) -> tuple[np.ndarray, Any]:
    if dst_shape is None and resolution is not None:
        left, bottom, right, top = rasterio.transform.array_bounds(array.shape[0], array.shape[1], src_transform)
        width = max(1, int((right - left) / resolution))
        height = max(1, int((top - bottom) / resolution))
        dst_shape = (height, width)
    transform, width, height = calculate_default_transform(
        src_crs,
        dst_crs,
        array.shape[1],
        array.shape[0],
        *rasterio.transform.array_bounds(array.shape[0], array.shape[1], src_transform),
        dst_width=dst_shape[1] if dst_shape else None,
        dst_height=dst_shape[0] if dst_shape else None,
    )
    dst = np.full((height, width), nodata, dtype=float)
    reproject(
        source=array,
        destination=dst,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=transform,
        dst_crs=dst_crs,
        src_nodata=nodata,
        dst_nodata=nodata,
        resampling=resampling,
    )
    return dst, transform


def load_monthly_tifs(raw_dir: Path) -> tuple[dict[str, np.ndarray], dict[str, int], dict[str, Any]]:
    monthly: dict[str, np.ndarray] = {}
    counts: dict[str, int] = {}
    meta: dict[str, Any] = {}
    tifs = sorted(raw_dir.glob("*.tif")) + sorted(raw_dir.glob("**/*.tif"))
    seen: set[str] = set()
    for path in tifs:
        if path.name in seen:
            continue
        seen.add(path.name)
        stem = path.stem
        month = stem.split("_")[-1] if "_" in stem else stem
        if len(month) != 7 or month[4] != "-":
            continue
        with rasterio.open(path) as src:
            data = src.read(1).astype(float)
            nodata = src.nodata if src.nodata is not None else -9999.0
            data[data == nodata] = np.nan
            monthly[month] = data
            meta_json = path.with_suffix(".json")
            if meta_json.exists():
                import json

                meta_sidecar = json.loads(meta_json.read_text())
                counts[month] = int(meta_sidecar.get("obs_count", 1))
            else:
                counts[month] = 1
            if "crs" not in meta:
                meta = {"crs": str(src.crs), "transform": src.transform}
    return monthly, counts, meta


def write_monthly_stack(
    monthly_ndvi: dict[str, np.ndarray],
    output_path: Path,
    crs: str,
    transform,
    nodata: float = -9999.0,
) -> Path:
    import xarray as xr

    months = sorted(monthly_ndvi.keys())
    arrays = []
    for m in months:
        arr = np.asarray(monthly_ndvi[m], dtype=float)
        arr = np.where(np.isfinite(arr), arr, nodata)
        arrays.append(arr)
    stack = np.stack(arrays, axis=0)
    height, width = stack.shape[1], stack.shape[2]
    if transform is None:
        transform = from_origin(0, height * 30, 30, 30)
    ds = xr.Dataset(
        data_vars={
            "ndvi": (("time", "y", "x"), stack),
        },
        coords={"time": months},
        attrs={
            "crs": crs,
            "transform": list(transform)[:6] if transform is not None else [],
            "nodata": nodata,
        },
    )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ds.to_netcdf(output_path)
    return output_path


def harmonize_monthly_stack(
    monthly: dict[str, np.ndarray],
    reference_shape: tuple[int, int] | None = None,
) -> dict[str, np.ndarray]:
    if not monthly:
        return {}
    if reference_shape is None:
        reference_shape = monthly[sorted(monthly.keys())[0]].shape
    out = {}
    for month, arr in monthly.items():
        if arr.shape == reference_shape:
            out[month] = arr
            continue
        padded = np.full(reference_shape, np.nan, dtype=float)
        rows = min(reference_shape[0], arr.shape[0])
        cols = min(reference_shape[1], arr.shape[1])
        padded[:rows, :cols] = arr[:rows, :cols]
        out[month] = padded
    return out
