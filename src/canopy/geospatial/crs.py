from __future__ import annotations

import numpy as np
from pyproj import Transformer


def transform_coordinates(
    xs: np.ndarray,
    ys: np.ndarray,
    src_crs: str,
    dst_crs: str,
) -> tuple[np.ndarray, np.ndarray]:
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    x_out, y_out = transformer.transform(xs, ys)
    return np.asarray(x_out), np.asarray(y_out)


def assert_same_crs(crs_a: str, crs_b: str) -> None:
    if crs_a != crs_b:
        raise ValueError(f"CRS mismatch: {crs_a} vs {crs_b}")
