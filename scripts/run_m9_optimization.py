#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.experiments.m9_optimization import run_m9_optimization


def main() -> None:
    parser = argparse.ArgumentParser(description="M9 constrained optimization vs baselines")
    parser.add_argument("--config", default="configs/m9_optimization.yaml")
    args = parser.parse_args()
    stack = ROOT / "data/processed/pilot/monthly_stack.nc"
    if not stack.exists():
        from canopy.experiments.m2_validation import run_m2_validation

        run_m2_validation(ROOT / "configs/m2_data_validation.yaml")
    result = run_m9_optimization(ROOT / args.config)
    print("M9 optimization complete.")
    print(f"  n_eval_cells={result['n_eval_cells']}")
    print(f"  best_baseline={result['best_baseline']}")
    print(
        "  optimizer_gain_fraction="
        f"{result['optimizer_gain_fraction_vs_best_baseline']:.3f}"
    )
    for strategy, row in result["strategies"].items():
        print(
            f"  {strategy}: benefit={row['total_benefit']:.1f} "
            f"n={row['n_selected']} bpc={row['benefit_per_cost']:.2f}"
        )
    print(f"  proceed_to_m10={result['go_decision']['proceed_to_m10_robustness']}")
    print("  report=results/m9/optimization_eval.json")


if __name__ == "__main__":
    main()
