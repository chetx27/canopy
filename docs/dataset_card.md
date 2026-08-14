# CANOPY Dataset Card — Bengaluru Pilot

**Version:** 0.1 (planning)  
**Status:** Inventory only. No data downloaded into repository yet.

## Study area

- **City:** Bengaluru (Bengaluru Urban / BBMP jurisdiction)
- **Pilot AOI (MVRE):** ~25 km² contiguous subset (northern metro transect candidate, aligned with prior urban tree cover research)
- **Full study area (later):** BBMP + peri-urban buffer (~800–1,100 km² depending on definition)
- **CRS:** EPSG:32643 (UTM zone 43N) for analysis; WGS84 for ingestion

## Dataset inventory

### Earth observation

| Name | Provider | URL / GEE ID | License | Spatial | Temporal | Variables | Missingness / limits | Preprocessing | CANOPY role |
|---|---|---|---|---|---|---|---|---|---|
| Sentinel-2 L2A | ESA/Copernicus | `COPERNICUS/S2_SR_HARMONIZED` | Copernicus free | 10–20 m | 2017–present | SR bands, SCL | Monsoon clouds Jun–Oct | Cloud mask (SCL), harmonize 10 m, monthly composite | Primary optical series |
| Sentinel-1 GRD | ESA | `COPERNICUS/S1_GRD` | Copernicus free | 10 m | 2017–present | VH, VV | Terrain edge noise | Speckle filter, align to S2 grid | Gap filling, structure |
| HLS L30/S30 | NASA/USGS | HLS v2 | Open | 30 m | 2013–present | SR multi-sensor | Sensor merge artifacts | Use OPERA spec | DIST-ALERT baseline input |
| Landsat C2 L2 | USGS | `LANDSAT/LC08/C02/T1_L2` etc. | Open | 30 m | 1984–present | SR, ST (LST) | SLC-off gaps L7 | Fmask, temporal composite | Long baseline, LST |
| OPERA DIST-ALERT | NASA | LP DAAC OPERA | Open | 30 m | 2023–present | Alert flags, confidence | New product; urban validation limited | Direct download | Operational baseline |
| MODIS LST MOD11A1 | NASA | `MODIS/061/MOD11A1` | Open | 1 km | Daily | LST, QC | Coarse | Reproject to study grid | Coarse validation |
| Dynamic World | Google/WRI | `GOOGLE/DYNAMICWORLD/V1` | CC-BY 4.0 | 10 m | 2016–present | Class probabilities | Model uncertainty | Monthly mode | Weak LULC prior only |
| ESA WorldCover 2021 | ESA | 10 m | 2021 snapshot | Single epoch | — | Stratification |
| ETH Canopy Height 2020 | ETH | 10 m global | 2020 | Static | — | Maturity proxy |

### Climate and environment

| Name | Provider | URL / GEE ID | License | Spatial | Temporal | Variables | Limits | Role |
|---|---|---|---|---|---|---|---|---|
| ERA5-Land hourly | ECMWF | `ECMWF/ERA5_LAND/HOURLY` | Copernicus | ~9 km | Hourly | T2m, dewpoint, precip, soil moisture | Not microscale | Meteorology covariates |
| CHIRPS (optional) | UCSB | 5 km | Daily precip | Backup rainfall | Water feasibility |

### Human and built environment

| Name | Provider | URL / GEE ID | License | Spatial | Temporal | Variables | Limits | Role |
|---|---|---|---|---|---|---|---|---|
| WorldPop 100 m | WorldPop | `WorldPop/GP/100m/pop` | Open | 100 m | 2015–2030 | Population | Dasymetric uncertainty | Exposure weighting |
| GHSL built-up | EC JRC | 10 m | Multi-date | Built-up intensity | Morphology |
| MS Building Footprints | Microsoft | GitHub release | ODbL | Vector | Snapshot | Footprint area | Incomplete fringe | Density feature |
| OSM | Contributors | Overpass/GEE | ODbL | Vector | Continuous | Roads, water, landuse | Completeness varies | Constraints |

### Terrain

| Name | Provider | Resolution | Role |
|---|---|---|---|
| Copernicus DEM GLO-30 | ESA | 30 m | Slope, aspect |
| CartoSat DEM (India) | ISRO | 30 m | Local alternative if accessed |

### Reference / label sources (not for training if used as evaluation)

| Source | Type | Notes |
|---|---|---|
| Manual HV imagery interpretation | Strong GT (sample) | Tier 1 |
| OSM change history | Medium GT | Tier 2 |
| Hansen/GFC, Dynamic World transitions | Weak / pseudo | Tier 3 only |
| Peer-reviewed Bengaluru LULC maps | Medium if geometries available | Tier 2 |

## Derived feature candidates (justified)

| Feature | Justification |
|---|---|
| NDVI, EVI | Standard vegetation vigor |
| NDWI | Moisture / irrigation signal (important in Bengaluru) |
| NDBI | Built-up expansion proxy |
| SAR VH/VV ratio | Cloud-free structure; monsoon continuity |
| Seasonal harmonic amplitude/phase | Phenology baseline |
| Texture (GLCM on NIR) | Scattered tree patterns |
| Building density, distance to water | Morphology and feasibility |
| Rolling 3-month NDVI anomaly | Persistence detection input |

Features added only with ablation justification.

## Data acquisition plan

1. Define AOI GeoJSON (`data/external/bengaluru_aoi.geojson`) from BBMP boundary.
2. GEE export scripts (future): monthly composites 2019–2025 for pilot.
3. Store raw exports outside git; checksum sidecar files in repo.
4. Record preprocessing parameters in experiment configs.

## Known Bengaluru-specific issues

- **Monsoon cloud persistence:** Expect 40–70% monthly missing optical pixels in peak monsoon (validate empirically in MVRE).
- **Sub-pixel trees:** At 30 m, isolated roadside trees often invisible; prefer 100 m aggregation for optimization grid.
- **Contradictory greenness trends:** Some wards show recent greening (street planting) while metro net loss continues; spatial heterogeneity is real, not noise.

## Licensing and ethics

- No PII in population layers; aggregate grid cells only.
- Respect Copernicus, WorldPop, and OSM attribution in outputs.
- High-resolution imagery for annotation must comply with provider ToS.

## Data availability risks summary

See `docs/research_discovery.md` Section 9.
