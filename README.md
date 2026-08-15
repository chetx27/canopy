# CANOPY

Temporal geospatial AI for early urban vegetation loss detection, climate risk forecasting, and intervention optimization. Bengaluru case study.

## What it does

Detects abnormal vegetation change from satellite data, forecasts future loss, estimates heat exposure impact, and optimizes where to plant trees under realistic constraints (budget, water, land). Compares against baselines. Quantifies uncertainty.

## Status

- Milestone 1 (research discovery): complete
- Milestone 2 (pilot data validation): pipeline implemented
- Milestone 3 (baseline detection): pipeline implemented
- Milestone 4 (temporal model): pipeline implemented
- Milestone 5 (ground truth): pipeline implemented
- Milestone 6 (forecasting): pipeline implemented
- Milestone 7 (heat exposure): pipeline implemented
- Milestone 8 (intervention simulator): pipeline implemented
- Real manual labels + imagery: pending

## Milestone commands

### M2 — Data validation

```bash
pip install -e ".[gee]"
earthengine authenticate
python scripts/gee_export_sentinel2.py
python scripts/run_m2_validation.py
# or: python -m canopy m2
```

### M3 — Baseline detection

```bash
python scripts/run_m3_detection.py
# or: python -m canopy m3
```

### M5 — Ground truth

```bash
python scripts/run_m5_ground_truth.py
python scripts/run_m5_ground_truth.py --no-simulate
# or: python -m canopy m5
```

### M4 — Temporal anomaly model

```bash
python scripts/run_m5_ground_truth.py
python scripts/run_m4_detection.py
# or: python -m canopy m4
```

### M6 — Forecasting and uncertainty

```bash
python scripts/run_m6_forecasting.py
# or: python -m canopy m6
```

### M7 — Heat exposure

```bash
python scripts/run_m7_heat_exposure.py
# or: python -m canopy m7
```

### M8 — Intervention simulator

```bash
python scripts/run_m8_intervention.py
# or: python -m canopy m8
```

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
pytest tests/

python scripts/run_mvre.py
python scripts/run_optimization_eval.py
python app/research_interface.py --label persistent_loss --seed 303
```

## Data pipeline

1. Place study area: `data/external/bengaluru_pilot_aoi.geojson`
2. Export Sentinel-2: `python scripts/gee_export_sentinel2.py`
3. Create ground truth labels: `data/external/mvre_labels_template.csv`
4. Preprocess and validate: `python scripts/run_m2_validation.py`

## Architecture

```
Sentinel-2 imagery
  -> Cloud filtering, alignment, CRS validation
  -> Vegetation indices (NDVI, EVI, NDWI, etc)
  -> Temporal representation
  -> Anomaly detection
  -> Forecasting
  -> Heat exposure modeling
  -> Intervention modeling
  -> Constrained optimization
  -> Uncertainty quantification
  -> Evaluation
```

## Core modules

- `detection/` - Change detection baselines and temporal GBM
- `forecasting/` - Persistence, seasonal naive, linear, GBDT with holdout evaluation
- `heat/` - Population-weighted heat exposure
- `optimization/` - Constrained optimizer with preservation vs planting
- `uncertainty/` - Conformal intervals and ranking stability
- `evaluation/` - Spatial splits, metrics, experiment registry

## Baselines

Compared under identical budget:

1. Random allocation
2. Hottest locations only
3. Lowest canopy only
4. Highest population only
5. Vulnerability-weighted only
6. Greedy heat exposure reduction
7. CANOPY optimizer

## Key design choices

**Seasonality:** Normal seasonal drop is not degradation. Persistence-aware alerts required.

**Ground truth:** Independent labels from high-res imagery, not self-generated indices.

**Preservation vs planting:** Mature and new canopy are not equivalent.

**Data leakage prevention:** Spatial block holdouts, no future data in features.

## Milestones

1. Research discovery: DONE
2. Data validation: DONE (pipeline)
3. Baseline detection: DONE (pipeline)
4. Temporal anomaly model: DONE (pipeline)
5. Ground truth expansion: DONE (pipeline)
6. Forecasting: DONE (pipeline)
7. Heat exposure model: DONE (pipeline)
8. Intervention simulator: DONE (pipeline)
9. Optimization engine: NEXT
10. Robustness and ablation studies
11. Cross-city validation
12. Paper

## Docs

- `docs/research_discovery.md`
- `docs/research_question.md`
- `docs/dataset_card.md`
- `docs/experimental_protocol.md`
- `docs/methodology/methodology.md`
- `docs/literature/literature_table.md`
- `docs/limitations.md`
- `docs/reproducibility.md`

## Limits

- Cloud contamination in satellite data
- LST is not air temperature
- Tree cooling is context dependent
- Transfer to other cities not yet tested

See `docs/limitations.md` for full analysis.

## Tests

```bash
pytest tests/ -v
```

## Reproducibility

See `docs/reproducibility.md`.

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
