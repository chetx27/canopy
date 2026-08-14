# Model Card (CANOPY v0.1)

## Intended use

Research evaluation of temporal urban vegetation anomaly detection, short-horizon forecasting, heat-exposure estimation, and constrained intervention optimization in Bengaluru.

## Out of scope

Operational municipal decision-making, individual health prediction, legal enforcement of tree violations.

## Components

| Component | Type | Output |
|---|---|---|
| harmonic_persistence | Rule + harmonic model | Persistent anomaly flags |
| bfast_monitor_style | Statistical monitor | Anomaly flags |
| gbdt forecast | Gradient boosting | Point + interval NDVI forecast |
| exposure model | Weighted exceedance | Population-weighted heat exposure surface |
| greedy optimizer | Constrained heuristic | preserve/restore/plant assignments |

## Training data

Real training requires exported Sentinel time series and independently labeled reference cells. Synthetic data is used only for pipeline smoke tests.

## Evaluation data

Tier-1 manual labels (see `docs/research_discovery.md` Section 10).

## Metrics

Detection F1, detection delay, FPR, forecast MAE/RMSE, exposure reduction, ranking stability.

## Uncertainty

Spatial conformal intervals for regression targets; ranking Kendall tau under input perturbation for optimization.

## Known failure modes

- Confusing monsoon seasonal dips with loss
- Cloud gaps delaying detection
- Sub-pixel tree loss omission
- Optimizer instability when exposure surfaces are flat

## Version

0.1.0 — research alpha
