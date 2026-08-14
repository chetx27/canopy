# Reproducibility

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Optional Google Earth Engine:

```bash
pip install -e ".[gee]"
earthengine authenticate
```

## Commands

```bash
pytest
python scripts/run_mvre.py
python scripts/run_optimization_eval.py
python -m canopy inventory
```

## Configuration

All experiments use YAML configs in `configs/`. Each run registers metadata in `results/experiments/`.

## Data

Raw imagery is not committed. Export using `scripts/gee_export_sentinel2.py` after placing AOI GeoJSON in `data/external/`.

## Random seeds

Default seed: 42 (`configs/defaults.yaml`).

## Results

No precomputed scientific results are shipped. Run experiments locally after acquiring data and labels.
