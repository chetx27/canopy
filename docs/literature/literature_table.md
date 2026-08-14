# CANOPY Literature Table (Living Document)

**Last updated:** 2026-08-14  
**Target size before Milestone 3:** 50+ entries  
**Current size:** 28 seed entries (expand via citation chaining)

Legend: **GT** = ground truth quality noted; **CANOPY gap** = what this work does not address that CANOPY investigates.

| Paper | Year | Problem | Dataset | Method | Spatial res. | Temporal res. | Evaluation | Main result | Limitation | Relevance to CANOPY | Potential research gap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Zhu et al. CCDC | 2014 | Continuous land-cover change | Landsat New England | Harmonic model + RF classification | 30 m | All acquisitions | User/producer accuracy, temporal accuracy 80% | Robust change detection with seasonality | Not urban-focused; needs dense series | Core Baseline D | Urban sub-pixel loss |
| Verbesselt et al. BFAST | 2010 | Trend/season breaks in NDVI | Simulated + MODIS Australia | BFAST decomposition | 250 m–30 m | 16-day | Break detection accuracy | Separates phenology from disturbance | Weak on seasonal amplitude changes alone | Baseline C foundation | Monsoon urban phenology |
| Bullock et al. DIST-ALERT | 2025 | Global vegetation loss alerts | HLS global | Rolling 3-yr baseline anomaly | 30 m | 1–4 day revisit | Detection lag, precision/recall vs reference | Mean lag 6–20 days by event size | No intervention modeling; urban scattered trees | Baseline E; latency benchmark | Decision loop after alert |
| Hansen et al. GFC | 2013 | Annual forest loss | Landsat global | Classification tree | 30 m | Annual | Global accuracy assessment | Standard forest loss product | Annual, not early warning; urban trees | Reference product | Early urban loss |
| Potapov et al. GFC updates | 2019+ | Forest loss dynamics | Landsat | Deep learning variants | 30 m | Annual | Regional validation | Improved tropical loss mapping | Same limitations in cities | Weak label source only | — |
| Smith et al. EWMACD comparison | 2019 | Compare change detectors | Simulated time series | BFAST, CCDC, EWMACD | 30 m | Dense | Change date correctness | EWMACD best overall; CCDC best class change | Simulated, not urban | Method selection guide | Real urban benchmark |
| Li et al. Shenzhen vegetation dynamics | 2021 | Urban greenness process change | Landsat Shenzhen | CCDC + trend/process integration | 30 m | 2000–2020 | Area statistics | 35% pixels changed at least once | Single Chinese city | Urban temporal framing | Indian monsoon city |
| Nölke Bengaluru tree cover | 2021 | Continuous urban tree cover | Landsat + WorldView-3 Bengaluru | Fully connected NN | 30 m | Snapshot (2016) | MAE 13.04% | Better than GTC v4 in urban AOI | Small northern AOI; not temporal | Canopy prior for Bengaluru | City-wide temporal canopy |
| SAM Bengaluru LULC | 2023 | 11-class land cover | S2+S1+OSM+DEM Bengaluru | OBIA + ML (GEE) | 10 m | Multi-date composites | Thematic accuracy | Handles monsoon with multi-sensor | Training data not always public | LULC weak labels | Pixel-level change events |
| Shahfahad et al. Bengaluru thermal comfort | 2025 | LST vs land cover 1993–2023 | Landsat Bengaluru | GIS + regression | 30 m | Multi-decadal | LST trends, comfort indices | +15.13°C mean LST; NDVI negative corr. | LST not air temp; not forecasting | Heat motivation for Bengaluru | Population exposure |
| Govind & Ramesh Bengaluru LST | 2020 | LST concentric rings | Landsat Bengaluru | Ring-based analysis | 30 m | Multi-year | Correlation structure | Core vs fringe UHI patterns | No intervention layer | Spatial UHI structure | — |
| Kim et al. Seoul phenology | 2024 | Urban phenology drivers | MODIS + VIIRS Seoul | Regression partitioning | 500 m–1 km | 2012–2021 | Variance partitioning | Day/night warming differential | Coarse resolution | Seasonality modeling | Finer urban scale |
| Zhao et al. Hangzhou forest phenology | 2024 | Urban forest phenology | MODIS Hangzhou | Double logistic fit | 1 km | 2001–2020 | Trend analysis | Extended growing season with urbanization | MODIS scale | Phenology baseline | Sentinel-2 scale |
| Nowak et al. Baltimore planting | 2010s | Where to plant trees | Baltimore i-Tree | Gradient-based placement scenarios | Block group / grid | Snapshot | Pollution, heat metrics | P-EHI prioritization differs from heat-only | Planting only; no preservation | Optimization Baseline 6 | Preserve vs plant |
| Locke et al. Joliette | 2021 | Street tree prioritization | Joliette GIS | Weighted multi-indicator index | Street segment | Snapshot | Municipal planning use | Heat-focused weighting practical | Heuristic weights | Baseline 5 analog | Uncertainty |
| Sun et al. Boston heat optimization | 2025 | Tree vs cool roof allocation | Boston Daymet + land cover | Downscaling regression + scenario optimization | 200 m | Seasonal (JJA) | Vulnerability-weighted exposure reduction | Integrated interventions beat single-strategy | Boston-specific; deterministic costs | Closest integrated precedent | Vegetation loss forecast input |
| Dortmund TPP | 2025 | Tree planting potential | Urban Atlas Dortmund | Weighted hex overlay | 50 m | Snapshot | Composite suitability | Multi-criteria planting map | No temporal loss detection | Baseline overlay | Dynamic priorities |
| Chen et al. tree cooling efficacy | 2024 | Context-dependent cooling | Multi-city global | Meta-analysis + modeling | City-scale | Seasonal | Cooling variance by morphology | Young trees limited; morphology matters | Not optimization | Intervention effect priors | Bengaluru parameters |
| Nature Comm. urban forestry hurdles | 2026 | Maturity for cooling | Modeled growth curves | Simulation | Tree-level | Decades | Canopy area growth | Mature trees critical | Not geospatial AI | Supports H5 | Spatial preserve ranking |
| Roloff et al. urban tree stock | 2021 | Age structure ecosystem services | Generic urban stock model | Demographic tree model | Stand-level | Decades | Service provisioning by age | Old trees dominate cooling services | Parameter calibration needed | Preservation benefit function | Empirical Bengaluru calibration |
| Lou et al. GeoCP | 2025 | Spatial prediction uncertainty | Housing + synthetic | Conformal prediction | Point / raster | Snapshot | Coverage probability | 93.67% coverage vs 81% bootstrap | Needs calibration set design | Uncertainty layer | Decision ranking stability |
| Vargas et al. Peru alerts | 2019 | Tropical early warning | Landsat Peru | Alert algorithm | 30 m | Near-real-time | Alert latency | Early warning feasible | Forest context | Method precedent | Urban |
| Frantz et al. BFAST Monitor GEE | 2021 | Large-area NRT monitoring | GEE implementation | BFAST Monitor | 30 m | Sub-annual | Case studies | Scalable NRT on GEE | Forest-focused demos | Baseline C implementation | Bengaluru scale run |
| Universal NRT framework review | 2025 | NRT vegetation anomalies | Landsat global survey | Parametric NRT methods | 30 m | Per acquisition | Framework comparison | COLD/S-CCD improvements | Review, not new data | Method map | — |
| Lang et al. ETH canopy height | 2023 | Canopy height from S2+GEDI | Global | Deep learning | 10 m | 2020 snapshot | RMSE vs LiDAR | Global 10 m height | 2020 single year | Maturity proxy | Temporal height change |
| Weng et al. LCZ phenology Austin | 2022 | LCZ phenology | Landsat Austin | LCZ stratification | 30 m | Multi-year | LCZ comparisons | LCZ controls phenology response | US city | Stratification feature | Bengaluru LCZ |
| Ramachandra & Kumar IISc Bengaluru | 2009+ | Urban sprawl environmental impact | Multi-source Bengaluru | GIS analysis | City-scale | Multi-decadal | Land cover fractions | Extreme vegetation/water loss trends | Not ML; coarse for pixel labels | Context setting | — |
| Integrated GFW alerts blog/docs | 2022–25 | Multi-sensor alert fusion | GLAD+RADD+DIST | Alert integration | 10–30 m | Days | Confidence by agreement | Multi-alert increases confidence | Not urban decision support | External baseline | — |

## Topic coverage checklist

- [x] Satellite vegetation change detection
- [x] Urban tree-canopy mapping
- [x] Urban heat exposure
- [x] Urban greening optimization
- [x] Tree-placement optimization
- [x] Deforestation early warning
- [x] Temporal anomaly detection
- [x] Urban climate intervention modeling
- [x] Uncertainty-aware geospatial AI

## Next literature actions

1. Add BEAST (Zhao et al.), COLD, S-CCD primary papers.
2. Add Lai & Kontokosta (2019) urban tree benefits review.
3. Add peer-reviewed downscaling papers cited by Sun 2025.
4. Add Karnataka/BDA statutory tree preservation documents (non-peer, context only).
5. Systematic Scopus export for `"urban vegetation" AND "change detection" AND "Sentinel-2"` (2018–2026).
