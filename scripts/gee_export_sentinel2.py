#!/usr/bin/env python3
"""Google Earth Engine export template for Sentinel-2 monthly composites.

Requires: pip install earthengine-api geemap
Authentication: earthengine authenticate
"""
from __future__ import annotations

import argparse
from pathlib import Path


def build_export(aoi_path: str, start: str, end: str, out_prefix: str) -> None:
    try:
        import ee
    except ImportError as exc:
        raise SystemExit("Install GEE dependencies: pip install canopy[gee]") from exc

    ee.Initialize()
    import geopandas as gpd

    aoi = gpd.read_file(aoi_path).to_crs(4326)
    geom = ee.Geometry.Mapping(aoi.union_all().__geo_interface__)

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(geom)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
        .map(lambda img: img.normalizedDifference(["B8", "B4"]).rename("NDVI"))
    )

    months = ee.List.sequence(0, ee.Date(end).difference(ee.Date(start), "month"))
    print(f"Prepared export template for {out_prefix}")
    print(f"AOI: {aoi_path}, period: {start} to {end}, images: {collection.size().getInfo()}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aoi", default="data/external/bengaluru_pilot_aoi.geojson")
    parser.add_argument("--start", default="2023-01-01")
    parser.add_argument("--end", default="2024-06-30")
    parser.add_argument("--out", default="data/raw/s2_pilot")
    args = parser.parse_args()
    if not Path(args.aoi).exists():
        raise SystemExit(f"AOI not found: {args.aoi}. Create GeoJSON before export.")
    build_export(args.aoi, args.start, args.end, args.out)


if __name__ == "__main__":
    main()
