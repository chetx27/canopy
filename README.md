# CANOPY

Temporal geospatial AI for early urban vegetation loss detection, climate risk forecasting, and intervention optimization. Bengaluru case study.

## What it does

Detects abnormal vegetation change from satellite data, forecasts future loss, estimates heat exposure impact, and optimizes where to plant trees under realistic constraints (budget, water, land). Compares against baselines. Quantifies uncertainty.

## Research question

Can temporal geospatial ML detect emerging vegetation degradation early enough to forecast localized heat exposure and optimize interventions under realistic constraints? Does it beat simple strategies?

## Key hypotheses

1. Temporal models beat single-date models for detecting persistent change
2. Multi-source data improves detection vs vegetation index only
3. Optimizing for human exposure produces different results than just optimizing for temperature
4. Constrained optimization beats random, heat-only, canopy-only strategies
5. Sometimes preserving mature trees is better than planting new ones
6. Model uncertainty matters for decisions

## Setup

```bash
git clone https://github.com/chetx27/canopy
cd canopy
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Optional Earth Engine:
```bash
pip install -e ".[gee]"
earthengine authenticate
```

## Run it

```bash
# Tests
pytest tests/

# Minimum viable experiment (MVRE)
python scripts/run_mvre.py --config configs/mvre_detection.yaml --seed 303

# Optimization baselines
python scripts/run_optimization_eval.py --config configs/experiment_optimization.yaml

# Interactive research interface
python app/research_interface.py --label persistent_loss --seed 303
```

## Data pipeline

1. Place study area: `data/external/bengaluru_pilot_aoi.geojson`
2. Export Sentinel-2: `python scripts/gee_export_sentinel2.py`
3. Create ground truth labels: `data/external/mvre_labels_template.csv` (manual interpretation)
4. Preprocess: `python scripts/preprocess_sentinel2.py`

## Architecture

```
Sentinel-2 imagery
  ↓
Cloud filtering, alignment, CRS validation
  ↓
Vegetation indices (NDVI, EVI, NDWI, etc)
  ↓
Temporal representation (seasonal decomposition, trajectories)
  ↓
Anomaly detection (5 baselines + learned model)
  ↓
Forecasting (persistence, seasonal naive, linear, GBDT)
  ↓
Heat exposure modeling (population weighted)
  ↓
Intervention modeling (preserve, plant, restore, nothing)
  ↓
Constrained optimization
  ↓
Uncertainty quantification
  ↓
Evaluation (spatial splits, ablations, robustness)
```

## Core modules

- `detection/` - Change detection methods (5+ baselines). Metrics: precision, recall, F1, IoU, detection delay.
- `forecasting/` - Vegetation state forecasts 1-12 months ahead. Metrics: MAE, RMSE, calibration, coverage.
- `heat/` - Human heat exposure (population weighted). Not just temperature.
- `optimization/` - Multi-objective constrained optimizer. Compares preservation vs planting.
- `uncertainty/` - Conformal intervals, ranking stability, sensitivity analysis.
- `evaluation/` - Spatial train/val/test splits (prevents leakage), experiment registry, baseline comparison.

## Baselines

All results compared against these under identical budget:
1. Random allocation
2. Hottest locations only
3. Lowest canopy only
4. Highest population only
5. Socioeconomic vulnerability only
6. Greedy heat exposure reduction
7. CANOPY optimizer

## Key design choices

**Seasonality:** Normal seasonal vegetation drop is not degradation. Explicitly models month-of-year, monsoon cycles, long-term trends. Requires repeated anomalies to trigger alert, not single observation.

**Ground truth:** Independent from features. Manual annotation from high-res imagery, not generated from spectral indices.

**Preservation vs planting:** Does not assume equivalence. Mature trees give immediate benefit. New trees take years. Optimizer picks preservation when cost-benefit favors it.

**Data leakage prevention:** Future imagery cannot inform past predictions. Neighboring pixels not randomly split. Normalization on training set only. Intervention locations not selected using test outcomes.

## Milestones

1. Research discovery: DONE
2. Data validation: IN PROGRESS (waiting for real Sentinel-2 export + labels)
3. Vegetation temporal baseline: NEXT
4. Temporal anomaly model
5. Vegetation forecasting
6. Heat exposure model
7. Intervention simulator
8. Optimization engine
9. Robustness and ablation studies
10. Cross-city validation
11. Research interface
12. Paper

## Docs

- `research_discovery.md` - Problem, literature gaps, roadmap
- `research_question.md` - RQs and hypotheses
- `dataset_card.md` - Data inventory and sources
- `experimental_protocol.md` - Baselines and metrics
- `methodology/methodology.md` - Technical details
- `literature/literature_table.md` - Structured review
- `limitations.md` - Known issues
- `reproducibility.md` - Step-by-step reproduction

## Status

- Research discovery and software infrastructure: done
- Real data and empirical results: not yet (requires actual Sentinel-2 export and ground truth labels)

No synthetic results claimed as real. No hard coded metrics.

## Limits

- Cloud contamination in satellite data
- LST is not air temperature
- Tree cooling is context dependent
- 5-6 years of data may miss rare events
- Transfer to other cities not yet tested
- Actual tree survival and social acceptance unknown

See `limitations.md` for full analysis.

## Tests

```bash
pytest tests/ -v --cov=src/canopy
```

Validates: coordinate transforms, spatial alignment, temporal ordering, leakage prevention, constraint enforcement.

## Reproducibility

Provided: environment specs, data scripts, training commands with random seeds, config files, experiment metadata.

To reproduce: See `reproducibility.md` for step-by-step.

## Citation

```bibtex
@software{canopy2026,
  title={CANOPY: Temporal Geospatial AI for Early Urban Vegetation Loss Detection},
  author={Chethana},
  year={2026},
  url={https://github.com/chetx27/canopy}
}
```

## License

MIT

---

Current status: Milestones 1-2 complete, empirical validation starting. Next: temporal baseline model.
