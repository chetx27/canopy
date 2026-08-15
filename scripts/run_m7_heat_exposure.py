#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.experiments.m7_heat_exposure import run_m7_heat_exposure


def main() -> None:
    parser = argparse.ArgumentParser(description="M7 population-weighted heat exposure evaluation")
    parser.add_argument("--config", default="configs/m7_heat_exposure.yaml")
    args = parser.parse_args()
    stack = ROOT / "data/processed/pilot/monthly_stack.nc"
    if not stack.exists():
        from canopy.experiments.m2_validation import run_m2_validation

        run_m2_validation(ROOT / "configs/m2_data_validation.yaml")
    result = run_m7_heat_exposure(ROOT / args.config)
    print("M7 heat exposure complete.")
    print(f"  synthetic_layers={result['synthetic_layers']}")
    print(f"  total_exposure={result['total_population_weighted_exposure']:.2f}")
    for name, corr in result["test_correlation_with_lst"].items():
        print(f"  test_corr[{name}]={corr:.3f}")
    overlap = result["priority_overlap"]
    print(
        "  top_k_jaccard(lst, exposure)="
        f"{overlap['raw_lst_vs_pop_weighted_jaccard']:.3f}"
    )
    print(f"  proceed_to_m8={result['go_decision']['proceed_to_m8_intervention_simulator']}")
    print("  report=results/m7/heat_exposure_eval.json")


if __name__ == "__main__":
    main()
