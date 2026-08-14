#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.experiments.m3_detection import run_m3_detection


def main() -> None:
    parser = argparse.ArgumentParser(description="M3: baseline vegetation detection evaluation")
    parser.add_argument("--config", default="configs/m3_baseline_detection.yaml")
    args = parser.parse_args()
    stack = ROOT / "data/processed/pilot/monthly_stack.nc"
    if not stack.exists():
        print("Monthly stack missing. Running M2 first...")
        from canopy.experiments.m2_validation import run_m2_validation

        run_m2_validation(ROOT / "configs/m2_data_validation.yaml")

    result = run_m3_detection(ROOT / args.config)
    print("M3 detection evaluation complete.")
    print(f"  auto_labeled={result.get('auto_labeled')}")
    print(f"  n_test_cells={result.get('n_test_cells')}")
    for method, metrics in result.get("test_set_results", {}).items():
        print(
            f"  {method}: f1={metrics.get('persistent_f1', 'n/a'):.3f} "
            f"fpr={metrics.get('false_positive_rate', 'n/a'):.3f} "
            f"delay={metrics.get('median_detection_delay_days')}"
        )
    print(f"  proceed_to_m4={result.get('go_decision', {}).get('proceed_to_m4_temporal_model')}")
    print("  report=results/m3/detection_baselines.json")


if __name__ == "__main__":
    main()
