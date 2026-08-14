# Methodology

## Pipeline

1. Data acquisition (Sentinel-2, Sentinel-1, auxiliary layers)
2. Quality control and harmonization to analysis grid (EPSG:32643)
3. Feature engineering (spectral indices, morphology, population)
4. Temporal representation (harmonic seasonality + persistence)
5. Detection (baselines A–E + harmonic persistence candidate)
6. Forecasting (persistence through GBDT quantile baselines)
7. Heat exposure (population-weighted exceedance over reference LST)
8. Intervention optimization (preserve / restore / plant under budget and water)
9. Uncertainty (spatial conformal intervals, ranking stability)
10. Evaluation (spatial block splits, bootstrap CIs)

## Leakage prevention

- Spatial block holdouts for train/validation/test
- Normalization and threshold tuning on train/validation only
- Feature times must not exceed label event times (`evaluation/splits.py`)

## Parameter sources

Intervention benefit and cost parameters are configurable in YAML. Literature-derived ranges must be documented before reporting preserve-vs-plant results. No hard-coded experimental outcomes.

## Primary target variables

- Detection: persistent vegetation loss (binary, cell-month)
- Forecasting: NDVI or canopy fraction
- Heat: land-surface temperature (primary); downscaled air temperature (secondary, validation required)
- Exposure: population-weighted exceedance above reference LST
- Optimization: expected exposure reduction under modeled action effects
