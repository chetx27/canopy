#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.experiments.m6_forecasting import run_m6_forecasting


def main() -> None:
    parser = argparse.ArgumentParser(description="M6 vegetation forecasting and uncertainty evaluation")
    parser.add_argument("--config", default="configs/m6_forecasting.yaml")
    args = parser.parse_args()
    stack = ROOT / "data/processed/pilot/monthly_stack.nc"
    if not stack.exists():
        from canopy.experiments.m2_validation import run_m2_validation

        run_m2_validation(ROOT / "configs/m2_data_validation.yaml")
    result = run_m6_forecasting(ROOT / args.config)
    print("M6 forecasting complete.")
    print(f"  n_test_cells={result['n_eval_cells_test']}")
    for method, horizons in result["test_results"].items():
        for h, metrics in horizons.items():
            print(f"  {method}@{h}m: mae={metrics['mae']:.4f} rmse={metrics['rmse']:.4f} cov80={metrics['coverage_80']:.3f}")
    print(f"  proceed_to_m7={result['go_decision']['proceed_to_m7_heat_exposure']}")
    print("  report=results/m6/forecast_eval.json")


if __name__ == "__main__":
    main()
