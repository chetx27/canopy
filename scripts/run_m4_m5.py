#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def ensure_stack() -> None:
    stack = ROOT / "data/processed/pilot/monthly_stack.nc"
    if not stack.exists():
        from canopy.experiments.m2_validation import run_m2_validation

        run_m2_validation(ROOT / "configs/m2_data_validation.yaml")


def main() -> None:
    parser = argparse.ArgumentParser(description="M5 then M4: ground truth and temporal model")
    parser.add_argument("--skip-m5", action="store_true")
    args = parser.parse_args()
    ensure_stack()
    if not args.skip_m5:
        from canopy.experiments.m5_ground_truth import run_m5_ground_truth

        m5 = run_m5_ground_truth(ROOT / "configs/m5_ground_truth.yaml")
        print(f"M5: batch={m5['n_batch_cells']} merged={m5['merge'].get('n_merged_labels', 0)}")
        print(f"M5: kappa={m5['inter_rater'].get('overall_kappa')}")
    from canopy.experiments.m4_detection import run_m4_detection

    m4 = run_m4_detection(ROOT / "configs/m4_temporal_model.yaml")
    print(f"M4: temporal_gbm f1={m4['test_set_results']['temporal_gbm']['persistent_f1']:.3f}")
    print(f"M4: proceed_to_m6={m4['go_decision']['proceed_to_m6_forecasting']}")


if __name__ == "__main__":
    main()
