# M5 Ground Truth Protocol

## Deliverables

1. Annotation batch of 500+ cells with NDVI summary stats for manual review
2. Inter-rater agreement (Cohen's kappa) between two annotators
3. Merged consensus label file for training/evaluation

## Annotation batch columns

`cell_id, row, col, ndvi_mean, ndvi_std, trend, valid_fraction, label, event_month, annotator, notes`

## Workflow

1. Run `python scripts/run_m5_ground_truth.py` to generate `data/external/annotation_batch.csv`
2. Two annotators independently label cells using high-resolution historical imagery
3. Save as `data/external/rater_a_labels.csv` and `data/external/rater_b_labels.csv`
4. Set `simulate_raters_for_pipeline_test: false` in `configs/m5_ground_truth.yaml`
5. Re-run M5 to compute kappa and merged labels

## Quality gate

- Minimum merged labels: 100 (configurable)
- Minimum kappa: 0.6 (configurable)
- Cells with rater disagreement flagged as `needs_adjudication`

## Simulated raters

When `simulate_raters_for_pipeline_test: true`, the pipeline creates noisy duplicate labels for wiring tests only. **Not valid ground truth.**
