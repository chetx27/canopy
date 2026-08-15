# M7 Heat Exposure Protocol

## Objective

Estimate population-weighted heat exposure surfaces on the M2 pilot grid, compare exposure formulations, and test whether human weighting changes intervention priorities relative to temperature-only ranking.

## Formulations

- `raw_lst` — land-surface temperature only
- `lst_x_population` — simple LST × population product
- `downscaled_lst_proxy` — morphology-adjusted LST proxy (canopy + building density)
- `population_weighted_exposure` — exceedance above reference LST, weighted by population (primary)

## Evaluation design

- Derive pilot LST/population/building layers from mean NDVI when real rasters are absent (flagged in report)
- Spatial block holdout (same split logic as M3–M6)
- Exp-H1: Pearson correlation of each formulation with held-out LST on test blocks
- Exp-H2: Population layer sensitivity (0.5×, 1.0×, 2.0× scaling)
- Priority overlap: top-k Jaccard between raw LST and population-weighted exposure

## Run

```bash
python scripts/run_m7_heat_exposure.py
# or: python -m canopy m7
```

## Go to M8

Proceed if:

1. Population-weighted exposure top-k overlap with raw LST is below 0.9 (priorities differ), and
2. Primary formulation correlates with held-out LST at r ≥ 0.5 on test blocks

Both gates are configurable in `configs/m7_heat_exposure.yaml`.
