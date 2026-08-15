# M6 Forecasting Protocol

## Objective

Evaluate short-horizon NDVI forecasting on the M2 monthly stack with holdout targets and interval coverage.

## Methods

- persistence
- seasonal_naive
- linear_trend
- gbdt

## Horizons

1, 3, and 6 months (configurable).

## Evaluation design

- History = all months before holdout window
- Target = observed NDVI at history_end + horizon
- Spatial block holdout on labeled/eval cells (same split logic as M3/M4)
- Metrics: MAE, RMSE, 80% interval coverage

## Run

```bash
python scripts/run_m6_forecasting.py
```

## Go to M7

Proceed if GBDT MAE is within 5% of persistence at all horizons or better (configurable gate in experiment output).
