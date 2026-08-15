#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.experiments.m8_intervention import run_m8_intervention


def main() -> None:
    parser = argparse.ArgumentParser(description="M8 preserve/plant/restore intervention simulator")
    parser.add_argument("--config", default="configs/m8_intervention.yaml")
    args = parser.parse_args()
    stack = ROOT / "data/processed/pilot/monthly_stack.nc"
    if not stack.exists():
        from canopy.experiments.m2_validation import run_m2_validation

        run_m2_validation(ROOT / "configs/m2_data_validation.yaml")
    result = run_m8_intervention(ROOT / args.config)
    print("M8 intervention simulator complete.")
    print(f"  n_eval_cells={result['n_eval_cells']}")
    print(f"  n_preserve_candidates={result['n_preserve_candidates']}")
    for action, stats in result["action_summary"].items():
        print(
            f"  {action}: n={stats['n_feasible']} "
            f"mean_reduction={stats['mean_exposure_reduction']:.2f} "
            f"mean_bpc={stats['mean_benefit_per_cost']:.2f}"
        )
    pvp = result["preserve_vs_plant"]
    print(
        "  preserve_median_bpc="
        f"{pvp['preserve_median_benefit_per_cost']:.2f} "
        f"plant_median_bpc={pvp['plant_median_benefit_per_cost']:.2f}"
    )
    print(f"  proceed_to_m9={result['go_decision']['proceed_to_m9_optimizer']}")
    print("  report=results/m8/intervention_sim_eval.json")


if __name__ == "__main__":
    main()
