from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def mask_s2_clouds(image: Any, cloud_classes: list[int] | None = None) -> Any:
    import ee

    classes = cloud_classes or [3, 8, 9, 10, 11]
    scl = image.select("SCL")
    mask = scl.eq(classes[0])
    for c in classes[1:]:
        mask = mask.or(scl.eq(c))
    return image.updateMask(mask.Not())


def add_ndvi(image: Any) -> Any:
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    return image.addBands(ndvi)


def monthly_ndvi_composite(
    collection: Any,
    month_start: str,
    month_end: str,
    composite_method: str = "median",
) -> Any:
    import ee

    filtered = collection.filterDate(month_start, month_end)
    ndvi = filtered.select("NDVI")
    if composite_method == "mean":
        comp = ndvi.mean()
    else:
        comp = ndvi.median()
    count = ndvi.size().rename("obs_count")
    return comp.addBands(count).set({"month_start": month_start, "month_end": month_end})


def build_s2_collection(
    geometry: Any,
    start: str,
    end: str,
    max_cloud_fraction: float = 60.0,
    cloud_classes: list[int] | None = None,
) -> Any:
    import ee

    col = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(geometry)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud_fraction * 100 if max_cloud_fraction <= 1 else max_cloud_fraction))
        .map(lambda img: mask_s2_clouds(img, cloud_classes))
        .map(add_ndvi)
    )
    return col


def export_monthly_composites(
    aoi_path: str | Path,
    start: str,
    end: str,
    out_dir: str | Path,
    cfg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    import ee
    import geopandas as gpd
    import pandas as pd

    ee.Initialize()
    cfg = cfg or {}
    prep = cfg.get("preprocessing", {})
    gee_cfg = cfg.get("gee", {})
    cloud_classes = prep.get("cloud_mask_scl", [3, 8, 9, 10, 11])
    scale = int(gee_cfg.get("scale_m", 30))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    aoi = gpd.read_file(aoi_path).to_crs(4326)
    geom = ee.Geometry(aoi.union_all().__geo_interface__)
    collection = build_s2_collection(
        geom,
        start,
        end,
        max_cloud_fraction=prep.get("max_cloud_fraction", 0.6),
        cloud_classes=cloud_classes,
    )
    periods = pd.period_range(start=start, end=end, freq="M")
    manifest: dict[str, Any] = {
        "aoi_path": str(aoi_path),
        "start": start,
        "end": end,
        "months": [],
        "collection_size": collection.size().getInfo(),
    }

    try:
        import geemap
    except ImportError:
        geemap = None

    for period in periods:
        month = period.strftime("%Y-%m")
        month_start = period.start_time.strftime("%Y-%m-%d")
        month_end = (period.start_time + pd.offsets.MonthEnd(0) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        composite = monthly_ndvi_composite(collection, month_start, month_end, prep.get("composite_method", "median"))
        obs_count = composite.select("obs_count").reduceRegion(ee.Reducer.first(), geom, scale).getInfo().get("obs_count", 0)
        ndvi_img = composite.select("NDVI")
        out_tif = out_dir / f"s2_ndvi_{month}.tif"
        meta_path = out_dir / f"s2_ndvi_{month}.json"

        if geemap is not None:
            geemap.ee_export_image(
                ndvi_img,
                filename=str(out_tif),
                scale=scale,
                region=geom,
                file_per_band=False,
            )
            status = "exported_local"
        elif gee_cfg.get("export_to_drive", True):
            task = ee.batch.Export.image.toDrive(
                image=ndvi_img,
                description=f"canopy_s2_ndvi_{month}",
                folder=gee_cfg.get("drive_folder", "canopy_bengaluru_pilot"),
                fileNamePrefix=f"s2_ndvi_{month}",
                region=geom,
                scale=scale,
                maxPixels=int(gee_cfg.get("max_pixels", 1e9)),
            )
            task.start()
            status = f"drive_task_{task.id}"
        else:
            status = "skipped_no_geemap"

        meta = {"month": month, "obs_count": obs_count, "status": status, "path": str(out_tif)}
        meta_path.write_text(json.dumps(meta, indent=2))
        manifest["months"].append(meta)

    manifest_path = out_dir / "export_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str))
    return manifest


def check_gee_auth() -> bool:
    try:
        import ee

        ee.Initialize()
        ee.Number(1).getInfo()
        return True
    except Exception:
        return False
