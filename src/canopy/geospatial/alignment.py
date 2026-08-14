from __future__ import annotations

import numpy as np


def align_to_reference(
    source: np.ndarray,
    source_transform: tuple[float, float, float, float, float, float],
    reference_shape: tuple[int, int],
    reference_transform: tuple[float, float, float, float, float, float],
    fill_value: float = np.nan,
) -> np.ndarray:
    if source.shape == reference_shape and source_transform == reference_transform:
        return source.copy()
    ref_rows, ref_cols = reference_shape
    out = np.full((ref_rows, ref_cols), fill_value, dtype=float)
    a_src, b_src, c_src, d_src, e_src, f_src = source_transform
    a_ref, b_ref, c_ref, d_ref, e_ref, f_ref = reference_transform
    for row in range(ref_rows):
        y = f_ref + row * e_ref + e_ref / 2.0
        for col in range(ref_cols):
            x = c_ref + col * a_ref + a_ref / 2.0
            src_col = int((x - c_src) / a_src)
            src_row = int((y - f_src) / e_src)
            if 0 <= src_row < source.shape[0] and 0 <= src_col < source.shape[1]:
                out[row, col] = source[src_row, src_col]
    return out


def grid_bounds(
    transform: tuple[float, float, float, float, float, float],
    shape: tuple[int, int],
) -> tuple[float, float, float, float]:
    a, b, c, d, e, f = transform
    rows, cols = shape
    minx = c
    maxy = f
    maxx = c + cols * a
    miny = f + rows * e
    return minx, miny, maxx, maxy
