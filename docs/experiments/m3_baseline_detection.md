# M3 Baseline Detection Protocol

## Objective

Evaluate reproducible vegetation-change baselines on the M2 monthly NDVI stack using spatial block holdout.

## Methods

| ID | Config key | Description |
|---|---|---|
| A | `ndvi_threshold` | Single-date NDVI below threshold |
| B | `bi_temporal_delta` | Month-to-month NDVI drop |
| C | `bfast_monitor_style` | History mean/std monitor |
| D | `harmonic_persistence` | Harmonic history + persistence filter |

## Labels

**Strong (preferred):** `data/external/m3_labels.csv` with columns:

`cell_id, label, row, col, event_month`

**Weak (demo only):** auto-labeled from stack trends if CSV missing. Flagged as `auto_labeled: true` in results.

## Spatial evaluation

- Block size: 500 m (configurable)
- Split: 60% train / 20% val / 20% test blocks
- Report metrics on **test cells only**

## Metrics

- Persistent F1, precision, recall, FPR
- Median detection delay (days) for persistent-loss cells
- Block bootstrap CI on cell agreement scores

## Run

```bash
python scripts/run_m3_detection.py
```

## Go to M4

Proceed if harmonic persistence F1 exceeds NDVI threshold by >= 0.05 on test cells, or report negative result and consider optimization-focused contribution.
