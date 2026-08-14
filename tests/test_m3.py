import numpy as np
import pandas as pd
import pytest
import xarray as xr

from canopy.data.labeling import auto_label_cells_from_stack, infer_event_month
from canopy.data.stack_loader import extract_cell_series, stack_to_cube
from canopy.evaluation.splits import split_blocks


def _fake_cube(months: int = 12, rows: int = 20, cols: int = 20) -> tuple[np.ndarray, list[str]]:
    rng = np.random.default_rng(0)
    times = [f"2023-{m:02d}" for m in range(1, months + 1)]
    cube = rng.uniform(0.3, 0.7, size=(months, rows, cols))
    for row in range(5, 8):
        for col in range(5, 8):
            cube[6:, row, col] -= 0.25
    return cube, times


def test_infer_event_month():
    times = [f"2023-{m:02d}" for m in range(1, 13)]
    series = np.array([0.6] * 6 + [0.3] * 6, dtype=float)
    assert infer_event_month(series, times) == 6


def test_auto_label_cells():
    cube, times = _fake_cube()
    df = auto_label_cells_from_stack(cube, times, n_per_class=5, seed=0)
    assert len(df) == 15
    assert set(df["label"]) == {"stable", "seasonal", "persistent_loss"}


def test_stack_to_cube(tmp_path):
    months, rows, cols = 6, 10, 10
    data = np.ones((months, rows, cols)) * 0.5
    ds = xr.Dataset({"ndvi": (("time", "y", "x"), data)}, coords={"time": [f"2023-0{i}" for i in range(1, 7)]})
    path = tmp_path / "stack.nc"
    ds.to_netcdf(path)
    loaded = stack_to_cube(xr.open_dataset(path))
    assert loaded[0].shape == (6, 10, 10)


def test_extract_cell_series():
    cube, _ = _fake_cube()
    series = extract_cell_series(cube, 6, 6)
    assert series is not None
    assert len(series) == cube.shape[0]


def test_split_blocks_nonempty():
    blocks = np.array([1, 1, 2, 2, 3, 3])
    train, val, test = split_blocks(blocks, train_fraction=0.33, val_fraction=0.33, seed=0)
    assert len(train | val | test) >= 1


def test_m3_requires_stack(tmp_path):
    from pathlib import Path

    from canopy.config import load_config
    from canopy.experiments.m3_detection import run_m3_detection
    import yaml

    root = Path(__file__).resolve().parents[1]
    cfg = load_config(root / "configs/m3_baseline_detection.yaml")
    cfg["paths"]["processed_stack"] = str(tmp_path / "missing.nc")
    cfg_path = tmp_path / "m3.yaml"
    cfg_path.write_text(yaml.dump(cfg))
    with pytest.raises(FileNotFoundError):
        run_m3_detection(cfg_path)
