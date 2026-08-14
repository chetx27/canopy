# CANOPY

**Temporal Geospatial AI for Early Urban Vegetation-Loss Detection, Climate-Risk Forecasting, and Intervention Optimization**

Research-grade experimental system. Primary case study: Bengaluru, India.

## Status

- Milestone 1 (research discovery): complete
- Milestone 2 (pilot data validation): pipeline implemented
- Milestone 3 (baseline detection): pipeline implemented
- Milestone 4 (temporal model): pipeline implemented
- Milestone 5 (ground truth): pipeline implemented
- Real manual labels + imagery: pending

## Milestone 2 — Data validation

```bash
# Optional: export real Sentinel-2 monthly NDVI (requires GEE auth)
pip install -e ".[gee]"
earthengine authenticate
python scripts/gee_export_sentinel2.py --check-auth
python scripts/gee_export_sentinel2.py

# Run QC + preprocessing (uses data/raw/s2_pilot/*.tif if present, else synthetic demo)
python scripts/run_m2_validation.py
# or: python -m canopy m2
```

Outputs:
- `data/processed/pilot/monthly_stack.nc`
- `results/qc/pilot_aoi_qc.json`
- `results/qc/figures/`
- `docs/datasets/preprocessing_spec_pilot.md`

## Milestone 3 — Baseline detection

Requires M2 stack (`data/processed/pilot/monthly_stack.nc`).

```bash
python scripts/run_m3_detection.py
# or: python -m canopy m3
```

Uses manual labels from `data/external/m3_labels.csv` if present; otherwise auto-labels from stack trajectories (**weak proxy**, flagged in report).

Outputs:
- `results/m3/detection_baselines.json`
- `results/m3/baseline_f1_comparison.png`

Baselines: NDVI threshold, bi-temporal delta, BFAST-style monitor, harmonic persistence. Evaluation uses spatial block holdout on test cells.

## Milestone 5 — Ground truth expansion

```bash
python scripts/run_m5_ground_truth.py
python scripts/run_m5_ground_truth.py --no-simulate   # human annotation mode only
# or: python -m canopy m5
```

Outputs:
- `data/external/annotation_batch.csv` — 500+ cells ready for manual labeling
- `data/external/m5_merged_labels.csv` — consensus labels (after raters provided)
- `results/m5/ground_truth_report.json` — Cohen's kappa and merge stats

For real research: fill `annotation_batch.csv`, split between two annotators as `rater_a_labels.csv` and `rater_b_labels.csv`, re-run without `--no-simulate` and with `simulate_raters_for_pipeline_test: false` in config.

## Milestone 4 — Temporal anomaly model

Requires M5 merged labels (or falls back to auto-labels).

```bash
python scripts/run_m5_ground_truth.py
python scripts/run_m4_detection.py
# or both: python scripts/run_m4_m5.py
# or: python -m canopy m4
```

Outputs:
- `results/m4/temporal_model_eval.json`
- `results/m4/m4_method_comparison.png`
- `results/m4/m4_ablation_comparison.png`

Includes temporal GBM + sequence alerter, compared to M3 baselines, with feature ablations (full / ndvi_only / no_seasonal).

## Research question

Can a reproducible temporal geospatial pipeline detect emerging urban vegetation degradation, forecast localized heat-exposure consequences, and optimize geographically targeted interventions under realistic constraints—in a way that measurably outperforms established baselines?

## Architecture

```
Data -> QC/Harmonization -> Features -> Temporal Model -> Detection
  -> Forecasting -> Heat Exposure -> Intervention Model -> Optimization
  -> Uncertainty -> Evaluation -> Visualization
```

## Repository layout

```
canopy/
  configs/           Experiment YAML
  src/canopy/        Core modules
  scripts/           Runnable experiments
  tests/             Unit tests
  docs/              Research documentation
  data/external/     AOI GeoJSON, label templates
  results/           Experiment outputs (generated)
  app/               Research inspection CLI
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Google Earth Engine (optional):

```bash
pip install -e ".[gee]"
earthengine authenticate
```

## Quick start

```bash
pytest
python scripts/run_mvre.py
python scripts/run_optimization_eval.py
python app/research_interface.py --label persistent_loss --seed 303
```

## Data acquisition

1. Place AOI GeoJSON at `data/external/bengaluru_pilot_aoi.geojson`
2. Export imagery: `python scripts/gee_export_sentinel2.py`
3. Create labels CSV from manual interpretation (`data/external/mvre_labels_template.csv`)

## Documentation

| Document | Description |
|---|---|
| [docs/research_discovery.md](docs/research_discovery.md) | Problem formulation, gaps, roadmap, MVRE |
| [docs/research_question.md](docs/research_question.md) | RQs and hypotheses |
| [docs/literature/literature_table.md](docs/literature/literature_table.md) | Literature table |
| [docs/dataset_card.md](docs/dataset_card.md) | Dataset inventory |
| [docs/experimental_protocol.md](docs/experimental_protocol.md) | Baselines and metrics |
| [docs/methodology/methodology.md](docs/methodology/methodology.md) | Methods |
| [docs/limitations.md](docs/limitations.md) | Known limitations |
| [docs/reproducibility.md](docs/reproducibility.md) | Reproduction steps |

## Modules

| Module | Purpose |
|---|---|
| `detection/` | NDVI threshold, bi-temporal, harmonic persistence, BFAST-style |
| `forecasting/` | Persistence, seasonal naive, linear, GBDT |
| `heat/` | Population-weighted exposure |
| `optimization/` | Greedy preserve/plant/restore optimizer + baselines |
| `uncertainty/` | Spatial conformal intervals, ranking stability |
| `evaluation/` | Metrics, spatial splits, experiment registry |

## Experiments

All parameters are configurable via YAML. No experimental metrics are hard-coded.

- MVRE detection pilot: `configs/mvre_detection.yaml`
- Optimization baselines: `configs/experiment_optimization.yaml`

## Limitations

See [docs/limitations.md](docs/limitations.md). Synthetic smoke tests validate wiring only; they are not scientific results.

## Citation

See [CITATION.cff](CITATION.cff).

## License

MIT — see [LICENSE](LICENSE).
