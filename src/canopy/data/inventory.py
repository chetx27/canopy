from __future__ import annotations

from pathlib import Path
from typing import Any

DATASET_INVENTORY: list[dict[str, Any]] = [
    {
        "name": "Sentinel-2 L2A",
        "provider": "Copernicus",
        "gee_id": "COPERNICUS/S2_SR_HARMONIZED",
        "license": "Copernicus free use",
        "spatial_resolution_m": 10,
        "temporal_resolution": "5-day combined",
        "role": "primary_optical",
    },
    {
        "name": "Sentinel-1 GRD",
        "provider": "Copernicus",
        "gee_id": "COPERNICUS/S1_GRD",
        "license": "Copernicus free use",
        "spatial_resolution_m": 10,
        "temporal_resolution": "6-12 day",
        "role": "sar_gap_fill",
    },
    {
        "name": "HLS",
        "provider": "NASA/USGS",
        "gee_id": "NASA/HLS/HLSL30/v002",
        "license": "Open",
        "spatial_resolution_m": 30,
        "temporal_resolution": "1-4 day",
        "role": "dist_alert_baseline",
    },
    {
        "name": "ERA5-Land",
        "provider": "ECMWF",
        "gee_id": "ECMWF/ERA5_LAND/HOURLY",
        "license": "Copernicus",
        "spatial_resolution_m": 9000,
        "temporal_resolution": "hourly",
        "role": "meteorology",
    },
    {
        "name": "WorldPop 100m",
        "provider": "WorldPop",
        "gee_id": "WorldPop/GP/100m/pop",
        "license": "Open",
        "spatial_resolution_m": 100,
        "temporal_resolution": "annual",
        "role": "population_exposure",
    },
    {
        "name": "OPERA DIST-ALERT",
        "provider": "NASA LP DAAC",
        "url": "https://doi.org/10.5067/SNAS-DAAH1",
        "license": "Open",
        "spatial_resolution_m": 30,
        "temporal_resolution": "near-real-time",
        "role": "operational_baseline",
    },
]


def list_datasets() -> list[dict[str, Any]]:
    return list(DATASET_INVENTORY)


def write_inventory_markdown(path: str | Path) -> None:
    path = Path(path)
    lines = ["# Dataset Inventory", "", "| Name | Provider | Resolution | Role |", "|---|---|---|---|"]
    for item in DATASET_INVENTORY:
        lines.append(
            f"| {item['name']} | {item['provider']} | {item.get('spatial_resolution_m', 'n/a')} m | {item['role']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
