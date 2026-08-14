# M4 Temporal Model Protocol

## Model

- **Cell classifier:** Gradient Boosting on temporal NDVI features (trend, lags, harmonic residual, seasonality)
- **Sequence alerter:** Sliding-window GBM for month-level alert flags with persistence filter

## Training

- Train on spatial **train blocks** only
- Validate on **val blocks**
- Report test metrics on **test blocks**

## Baselines compared

All M3 baselines plus `temporal_gbm`.

## Ablations

| Variant | Features removed |
|---|---|
| full_features | none |
| ndvi_only | harmonic + seasonal |
| no_seasonal | harmonic + seasonal correlations |

## Go to M6

Proceed if temporal GBM F1 exceeds best M3 baseline by >= 0.03 on test cells.
