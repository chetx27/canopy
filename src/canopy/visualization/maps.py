from __future__ import annotations

from pathlib import Path

import folium
import numpy as np


def export_point_map(
    latitudes: np.ndarray,
    longitudes: np.ndarray,
    values: np.ndarray,
    output_html: str | Path,
    zoom: int = 11,
) -> Path:
    latitudes = np.asarray(latitudes, dtype=float)
    longitudes = np.asarray(longitudes, dtype=float)
    values = np.asarray(values, dtype=float)
    center = [float(np.nanmean(latitudes)), float(np.nanmean(longitudes))]
    fmap = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
    for lat, lon, val in zip(latitudes, longitudes, values):
        if not np.isfinite(val):
            continue
        color = "red" if val > 0.5 else "green"
        folium.CircleMarker(
            location=[float(lat), float(lon)],
            radius=4,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=f"score={val:.3f}",
        ).add_to(fmap)
    output_html = Path(output_html)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    fmap.save(str(output_html))
    return output_html
