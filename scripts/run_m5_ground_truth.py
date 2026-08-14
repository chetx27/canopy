#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.experiments.m5_ground_truth import run_m5_ground_truth


def main() -> None:
    parser = argparse.ArgumentParser(description="M5 ground-truth batch and inter-rater agreement")
    parser.add_argument("--config", default="configs/m5_ground_truth.yaml")
    parser.add_argument("--no-simulate", action="store_true", help="Do not simulate raters for pipeline test")
    args = parser.parse_args()
    stack = ROOT / "data/processed/pilot/monthly_stack.nc"
    if not stack.exists():
        from canopy.experiments.m2_validation import run_m2_validation

        run_m2_validation(ROOT / "configs/m2_data_validation.yaml")
    from canopy.config import load_config

    cfg = load_config(ROOT / args.config)
    if args.no_simulate:
        cfg.setdefault("ground_truth", {})["simulate_raters_for_pipeline_test"] = False
    result = run_m5_ground_truth(cfg)
    print("M5 complete.")
    print(f"  batch_cells={result['n_batch_cells']}")
    print(f"  merged_labels={result['merge'].get('n_merged_labels', 0)}")
    print(f"  kappa={result['inter_rater'].get('overall_kappa')}")
    print(f"  simulated={result['inter_rater'].get('simulated_raters', False)}")
    print(f"  ready_for_m4={result['go_decision']['ready_for_m4_training']}")


if __name__ == "__main__":
    main()
