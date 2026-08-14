# CANOPY

**Temporal Geospatial AI for Early Urban Vegetation-Loss Detection, Climate-Risk Forecasting, and Intervention Optimization**

Research-grade experimental system. Primary case study: Bengaluru, India.

## Status

- Milestone 1 (research discovery): complete
- Milestone 2 (pilot data validation): pipeline implemented; run locally
- Empirical results on **real** imagery: pending GEE export + labels

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
- `data/processed/pilot/monthly_stack.nc` — aligned monthly NDVI stack
- `results/qc/pilot_aoi_qc.json` — QC metrics and go/no-go for M3
- `results/qc/figures/` — valid fraction, observation count, mean NDVI plots
- `docs/datasets/preprocessing_spec_pilot.md` — frozen preprocessing spec

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
