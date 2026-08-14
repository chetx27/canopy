#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from canopy.detection.baselines import run_detector
from canopy.forecasting.baselines import run_forecast


def inspect_cell(label: str, seed: int, n_months: int = 18) -> None:
    from canopy.experiments.mvre import simulate_ndvi_series

    times, series, event_index = simulate_ndvi_series(label, n_months, seed)
    print(f"cell label={label} seed={seed} event_month={event_index}")
    print("month\tndvi")
    for t, v in zip(times, series):
        print(f"{int(t):02d}\t{v:.3f}")
    det = run_detector("harmonic_persistence", series, times)
    print(f"harmonic_persistence flags={det.flags.tolist()}")
    fc = run_forecast("gbdt", series, horizon=3)
    print(f"3-month forecast: {fc.point:.3f} [{fc.lower:.3f}, {fc.upper:.3f}]")


def main() -> None:
    parser = argparse.ArgumentParser(description="CANOPY research cell inspector")
    parser.add_argument("--label", default="persistent_loss")
    parser.add_argument("--seed", type=int, default=303)
    args = parser.parse_args()
    inspect_cell(args.label, args.seed)


if __name__ == "__main__":
    main()
