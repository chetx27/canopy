#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.experiments.m2_validation import run_m2_validation


def main() -> None:
    parser = argparse.ArgumentParser(description="M2: Bengaluru pilot data validation and QC")
    parser.add_argument("--config", default="configs/m2_data_validation.yaml")
    args = parser.parse_args()
    result = run_m2_validation(ROOT / args.config)
    print("M2 validation complete.")
    print(f"  synthetic={result.get('synthetic')}")
    print(f"  months={result.get('n_months')}")
    print(f"  overall_valid_fraction={result.get('overall_valid_fraction'):.3f}")
    print(f"  proceed_to_m3={result.get('go_decision', {}).get('proceed_to_m3_detection')}")
    print(f"  qc_report=results/qc/pilot_aoi_qc.json")
    print(f"  stack={result.get('processed_stack')}")


if __name__ == "__main__":
    main()
