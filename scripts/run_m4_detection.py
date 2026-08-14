#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.experiments.m4_detection import run_m4_detection


def main() -> None:
    parser = argparse.ArgumentParser(description="M4 temporal GBM detection evaluation")
    parser.add_argument("--config", default="configs/m4_temporal_model.yaml")
    args = parser.parse_args()
    stack = ROOT / "data/processed/pilot/monthly_stack.nc"
    merged = ROOT / "data/external/m5_merged_labels.csv"
    if not stack.exists():
        from canopy.experiments.m2_validation import run_m2_validation

        run_m2_validation(ROOT / "configs/m2_data_validation.yaml")
    if not merged.exists():
        print("Merged labels missing. Run M5 first: python scripts/run_m5_ground_truth.py")
    result = run_m4_detection(ROOT / args.config)
    print("M4 complete.")
    for method, m in result["test_set_results"].items():
        print(f"  {method}: f1={m.get('persistent_f1', 0):.3f}")
    print(f"  proceed_to_m6={result['go_decision']['proceed_to_m6_forecasting']}")


if __name__ == "__main__":
    main()
