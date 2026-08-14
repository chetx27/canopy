from __future__ import annotations

import numpy as np


def ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    denom = nir + red
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (nir - red) / denom
    out = np.where(denom == 0, np.nan, out)
    return out.astype(float)


def evi(nir: np.ndarray, red: np.ndarray, blue: np.ndarray) -> np.ndarray:
    denom = nir + 6.0 * red - 7.5 * blue + 1.0
    with np.errstate(divide="ignore", invalid="ignore"):
        out = 2.5 * (nir - red) / denom
    out = np.where(denom == 0, np.nan, out)
    return out.astype(float)


def ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
    denom = green + nir
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (green - nir) / denom
    out = np.where(denom == 0, np.nan, out)
    return out.astype(float)


def ndbi(swir: np.ndarray, nir: np.ndarray) -> np.ndarray:
    denom = swir + nir
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (swir - nir) / denom
    out = np.where(denom == 0, np.nan, out)
    return out.astype(float)


def savi(nir: np.ndarray, red: np.ndarray, l: float = 0.5) -> np.ndarray:
    denom = nir + red + l
    with np.errstate(divide="ignore", invalid="ignore"):
        out = ((nir - red) / denom) * (1.0 + l)
    out = np.where(denom == 0, np.nan, out)
    return out.astype(float)
