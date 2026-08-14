# CANOPY Experimental Protocol

**Version:** 0.1  
**Prerequisite:** MVRE completion before full-scale experiments

## Principles

1. Every experiment has a config ID, random seed, and registry entry before execution.
2. No tuning on held-out test regions.
3. No future observations in feature construction.
4. Pseudo-labels never reported as ground truth.
5. Negative results are reported.

## Minimum viable research experiment (MVRE)

See `docs/research_discovery.md` Section 17.

| Parameter | Value |
|---|---|
| AOI | ~25 km² Bengaluru pilot |
| Period | 18 months (e.g., 2023-01 to 2024-06) |
| Grid | 30 m |
| Labels | 150 manually interpreted cells |
| Methods | NDVI threshold, BFAST Monitor, DIST-ALERT, harmonic+persistence |
| Primary metrics | Persistent F1, detection delay, FPR |
| Go/no-go | ±5 F1 pts or ≥30 days delay improvement without FPR blowup |

## Baseline registry

### Detection (A–G)

| ID | Name | Implementation source |
|---|---|---|
| A | Single-date NDVI threshold | Configurable percentile per land-cover stratum |
| B | Bi-temporal NDVI delta | Fixed window pair |
| C | BFAST Monitor | GEE or bfast R port |
| D | CCDC harmonic residual | ccdc package / simplified reimplementation |
| E | DIST-ALERT | LP DAAC direct |
| F | Temporal GBM | sklearn/lightgbm on lag features |
| G | Temporal deep model | Only if F fails MVRE gate |

### Forecasting

- Persistence, seasonal naive, linear trend, RF, quantile GBM

### Optimization (1–8)

- Random, max LST, min canopy, max population, max vulnerability proxy, greedy exposure, CANOPY full, CANOPY plant-only

## Spatial and temporal splits

```
Bengaluru
├── Train blocks (ward clusters A, B)
├── Validation blocks (ward cluster C, non-adjacent to test)
└── Test blocks (ward cluster D, buffer ≥500 m from train)
```

Temporal split for forecasting:

- Train: months 1–12
- Val: months 13–15
- Test: months 16–18

Document block IDs in each experiment config.

## Experiment catalog (full system)

| Exp ID | Phase | Question | Key metrics |
|---|---|---|---|
| MVRE-D0 | Pilot | Detection feasibility | F1, delay |
| D1 | Detection | Seasonal vs persistent | Stratified F1 |
| D2 | Detection | Early vs baselines | Detection delay |
| D3 | Detection | Feature ablation | ΔF1 per feature group |
| D4 | Detection | Spatial CV | Block bootstrap CI |
| F1 | Forecast | Horizon accuracy | MAE, RMSE |
| F2 | Forecast | Uncertainty calibration | Coverage, sharpness |
| H1 | Heat | Exposure formulation | RMSE, spatial r |
| H2 | Heat | Population sensitivity | Rank correlation |
| O1 | Optimization | Budget scenarios | Exposure reduction |
| O2 | Optimization | Preserve vs plant | Benefit per cost |
| O3 | Optimization | Weight sensitivity | Pareto area |
| O4 | Optimization | Ranking stability | Kendall τ under noise |
| R1 | Robustness | Missing data | Performance degradation curve |
| R2 | Robustness | Cloud/noise injection | Alert false positive rate |
| R3 | Equity | Benefit distribution | Quintile share, min benefit |
| X1 | Transfer | Zero-shot city | Persistent F1 drop |

## Evaluation metrics (mandatory reporting)

### Detection

- Precision, recall, F1 (persistent class primary)
- False positive rate on stable cells
- Detection delay (days from event onset to first alert)
- IoU if polygon labels available

### Forecasting

- MAE, RMSE by horizon and land-use stratum
- Prediction interval coverage at 80% and 90%
- CRPS if probabilistic

### Heat / exposure

- Target variable documented explicitly (primary: LST; secondary: downscaled Tair proxy)
- RMSE, MAE, spatial Pearson r
- Station validation at IMD points (where available)

### Optimization

- Total expected population-weighted exposure reduction
- Benefit per tree, per currency unit, per water unit
- Population benefited (count above threshold)
- Equity: Gini of ward-level benefits; minimum quintile benefit share
- Ranking stability: Kendall τ between baseline and perturbed inputs

### Statistical analysis

- Spatial block bootstrap 95% CI for primary metrics
- Paired comparison across methods on same test blocks
- Report n blocks, not just n pixels

## Leakage prevention checklist

- [ ] Normalization stats computed on train blocks only
- [ ] Threshold tuning on validation only
- [ ] Test blocks never used in feature selection
- [ ] DIST-ALERT not used as both method and sole label source
- [ ] Temporal features for time t use only observations ≤ t

## Threats to validity

Document in each experiment report:

- Label noise level
- Cloud gap rate in test period
- Construct validity of exposure metric
- External validity (Bengaluru-only)

## Reproducibility requirements (when implementation begins)

- `pyproject.toml` pinned dependencies
- Config YAML per experiment
- MLflow or local JSON experiment registry
- Preprocessing command log with checksums

## Decision explainability (future)

Each recommended intervention cell must export:

- Top contributing factors (exposure, canopy trend, feasibility, uncertainty)
- Counterfactual: expected exposure if no action vs preserve vs plant

Methods: SHAP for ML components; sensitivity for optimizer.

## Counterfactual scenarios (future)

| Scenario | Description |
|---|---|
| A | No intervention |
| B | 1k trees heat-only heuristic |
| C | 1k trees CANOPY optimizer |
| D | Preserve identified mature canopy |
| E | Mixed preserve + plant |

All outputs labeled **modeled scenarios**, not observed outcomes.
