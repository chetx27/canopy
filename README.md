# CANOPY

**Temporal Geospatial AI for Urban Vegetation-Loss Detection, Climate-Risk Forecasting, and Intervention Optimization**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Research Status](https://img.shields.io/badge/Research-Active-orange.svg)
![Domain](https://img.shields.io/badge/Domain-Geospatial%20AI-2f6f8f.svg)
![Remote Sensing](https://img.shields.io/badge/Remote%20Sensing-Satellite%20%2B%20Temporal%20Analysis-4c8bf5.svg)

CANOPY is an end-to-end geospatial intelligence framework that detects abnormal urban vegetation loss, forecasts future vegetation and heat-exposure risk, quantifies intervention impact, and optimizes where limited urban-greening resources should be deployed.

It connects remote sensing, temporal modeling, geospatial analysis, uncertainty quantification, and constrained optimization into a single reproducible research pipeline. The initial study area is **Bengaluru, India**, with an architecture designed to transfer to other cities.

> **Core question:** Given where vegetation is changing, how fast, what risk may emerge, who is exposed, and what interventions are feasible — where should a city act first?

---

## Table of Contents

- [Motivation](#motivation)
- [Pipeline Overview](#pipeline-overview)
- [Architecture](#architecture)
- [Core Modules](#core-modules)
- [Research Methodology](#research-methodology)
- [Evaluation](#evaluation)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [Limitations](#limitations)
- [Ethics](#ethics)
- [Future Research](#future-research)
- [Citation](#citation)
- [License](#license)

---

## Motivation

Urban vegetation changes continuously due to construction, drought, heat stress, disease, and development pressure — often invisibly until the damage is visible. Most urban-greening workflows react after the fact.

CANOPY investigates a proactive pipeline:

```
detect change early → understand persistence → estimate future risk
→ quantify exposure → identify feasible interventions → optimize resources
```

**Hypothesis:** Temporal and uncertainty-aware geospatial modeling can identify persistent vegetation degradation earlier, and produce more useful intervention priorities, than static thresholds or purely heuristic ranking. This is tested via explicit baselines, spatial/temporal validation, ablations, and robustness experiments — not assumed.

---

## Pipeline Overview

| Stage | Question | Output |
|---|---|---|
| Data Acquisition | What observations exist? | Harmonized observations |
| Quality Control | Which are trustworthy? | Clean temporal data |
| Feature Engineering | What signals are informative? | Spectral/spatial indices |
| Temporal Modeling | What is persistent change? | Temporal representations |
| Detection | Where is loss occurring? | Anomaly maps |
| Forecasting | What happens next? | Risk trajectories |
| Heat Modeling | What's the exposure impact? | Exposure surfaces |
| Intervention | What actions are feasible? | Candidate interventions |
| Optimization | Where to allocate resources? | Priority ranking |
| Uncertainty | How stable are predictions? | Confidence intervals |
| Evaluation | Does it actually work? | Metrics & experiment registry |

Output is not just "plant a tree here" — it's *why here, how urgent, what happens if nothing is done, what's feasible, who benefits, at what cost, and how confident are we.*

---

## Architecture

```
Satellite + Auxiliary Data
        │
        ▼
Data Acquisition → Quality Control → CRS/Resampling
        │
        ▼
Spectral Features → Temporal Representation
        │
        ▼
Vegetation Change Detection
        │
        ▼
Risk Forecasting → Heat/Exposure Modeling
        │
        ▼
Intervention Simulation → Constrained Optimization
        │
        ▼
Uncertainty Quantification
        │
        ▼
Evaluation + Experiment Registry
        │
        ▼
Decision-Support Outputs
```

---

## Core Modules

1. **Data Acquisition & Harmonization** — ingestion, CRS alignment, resampling, quality filtering, AOI clipping.
2. **Spectral Feature Engineering** — NDVI, EVI, NDWI, NDBI, SAVI as complementary vegetation/urban signals.
3. **Temporal Representation** — harmonic seasonality, persistence filtering, trend/residual analysis to separate real decline from noise.
4. **Vegetation-Loss Detection** — multiple baselines (single-date threshold, bi-temporal Δ-NDVI, BFAST-style structural change, harmonic + persistence) plus stronger research baselines (DIST-ALERT, gradient-boosted/temporal deep models).
5. **Future Risk Forecasting** — persistence, seasonal-naive, linear trend, tree-based, and probabilistic models across multiple horizons (30/60/90-day+).
6. **Heat Exposure Modeling** — links vegetation, LST, built-up intensity, and population into a population-weighted exposure metric.
7. **Intervention Modeling** — preserve / restore / plant scenarios evaluated against real-world constraints (budget, water, land, access).
8. **Spatial Optimization** — constrained greedy optimization maximizing expected benefit subject to cost, water, and land constraints; configurable multi-term objective.
9. **Uncertainty Quantification** — conformal methods, prediction intervals, and ranking-stability analysis (e.g., Kendall's τ under perturbation).
10. **Evaluation & Experiment Registry** — every experiment has a config ID, seed, documented splits, and metrics.

---

## Research Methodology

Staged phases: Discovery → Pilot Data Validation → Baseline Detection → Temporal Modeling → Ground-Truth Validation → Forecasting → Heat Exposure → Intervention Modeling → Optimization.

**Key protocol rules:**
- No test leakage — held-out regions never inform tuning/preprocessing.
- No future information leakage in forecasting features.
- External disturbance products are reference data, not automatic ground truth.
- Negative results are documented, not discarded.
- Every experiment is registered (config, seed, splits, metrics).

**Leakage safeguards:** spatial block splits with buffer zones (not random pixel splits), strict temporal train/val/test ordering, and preprocessing statistics computed only on training regions.

---

## Evaluation

| Category | Key Metrics |
|---|---|
| Detection | Precision, Recall, F1, Persistent-class F1, FPR, Detection Delay, IoU |
| Forecasting | MAE, RMSE, horizon-specific error, interval coverage, CRPS |
| Heat/Exposure | RMSE, MAE, spatial correlation, population-weighted error |
| Optimization | Exposure reduction, benefit/tree, benefit/cost, equity (Gini, quintile share), ranking stability |

Optimization strategies are benchmarked against random allocation, max-LST, min-canopy, max-population, and greedy-exposure baselines to confirm the full system adds real value.

---

## Repository Structure

```
canopy/
├── app/research_interface.py
├── configs/              # YAML experiment configs (m2–m9, mvre)
├── data/external/        # Bengaluru AOIs, label templates
├── docs/                 # architecture, protocol, ethics, experiments
├── results/
├── scripts/               # run_mvre.py, run_optimization_eval.py, gee_export_sentinel2.py
├── src/canopy/
│   ├── data/ detection/ evaluation/ experiments/ features/
│   ├── forecasting/ geospatial/ heat/ intervention/
│   └── optimization/ temporal/ uncertainty/ visualization/
├── tests/
├── CITATION.cff
├── LICENSE
└── pyproject.toml
```

---

## Installation

```bash
git clone https://github.com/chetx27/canopy.git
cd canopy

python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -e .                # base install
pip install -e ".[dev]"         # + dev dependencies
pip install -e ".[gee]"         # + Google Earth Engine support
pip install -e ".[mlflow]"      # + MLflow tracking
pip install -e ".[all]"         # everything
```

**Requirements:** Python 3.9+, pip, Git, a GDAL-compatible geospatial environment, and optional Earth Engine access.

---

## Usage

```bash
canopy                                   # CLI entry point
python scripts/run_mvre.py               # Minimum Viable Research Experiment
python scripts/run_optimization_eval.py  # Intervention/optimization evaluation
python scripts/gee_export_sentinel2.py   # Sentinel-2 export via GEE
```

The MVRE answers the first go/no-go question: *is there enough signal in the pilot data to justify building the full system?*

**Pilot experiment parameters:** ~25 km² Bengaluru AOI, ~18-month period, 30 m grid, 150 manually labeled cells; primary metrics are persistent F1, detection delay, and FPR.

---

## Data Sources

- **Sentinel-2** — multispectral imagery (NDVI/EVI/NDWI/NDBI/SAVI)
- **Sentinel-1** — SAR, fills gaps where optical data is cloud-affected
- **Harmonized Landsat/Sentinel** — extended temporal coverage
- **DIST-ALERT** — disturbance reference product
- **Auxiliary data** — population, land use, climate reanalysis, OpenStreetMap infrastructure, vulnerability proxies

---

## Limitations

- Remote-sensing artifacts (clouds, mixed pixels, resolution/temporal gaps)
- Manual labels carry human disagreement and coverage bias
- Vegetation–temperature relationships are statistical, not causal, unless separately validated
- Bengaluru-trained models require explicit evaluation before transfer to other cities
- Optimization quality is bounded by the accuracy of its cost/constraint inputs

---

## Ethics

CANOPY is a decision-support layer for planners, ecologists, and city authorities — not an autonomous authority for land acquisition, displacement, enforcement, or service denial. The project prioritizes transparency, documented assumptions, uncertainty reporting, and human oversight.

---

## Future Research

- Temporal transformers / spatiotemporal neural models (only where they beat strong baselines)
- Multi-sensor fusion (S1 + S2 + Landsat + thermal + DEM + climate)
- Higher-resolution change detection
- Causal intervention evaluation (quasi-experimental / before-after / matched controls)
- Cross-city generalization studies
- Human-in-the-loop expert validation
- Explainable, auditable intervention ranking

---

## Citation

```
CANOPY Research Team.
CANOPY: Temporal Geospatial AI for Urban Vegetation Loss Detection
and Climate Risk Mitigation. GitHub repository.
```

Machine-readable citation available in [`CITATION.cff`](CITATION.cff).

---

## License

Released under the [MIT License](LICENSE).
