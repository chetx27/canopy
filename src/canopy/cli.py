from __future__ import annotations

import argparse
from pathlib import Path

from canopy.config import load_config
from canopy.data.inventory import write_inventory_markdown
from canopy.experiments.mvre import run_mvre


def main() -> None:
    parser = argparse.ArgumentParser(prog="canopy", description="CANOPY research CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    mvre = sub.add_parser("mvre", help="Run minimum viable research experiment")
    mvre.add_argument("--config", default="configs/mvre_detection.yaml")

    inv = sub.add_parser("inventory", help="Write dataset inventory markdown")
    inv.add_argument("--output", default="docs/datasets/inventory_generated.md")

    m2 = sub.add_parser("m2", help="Run M2 pilot data validation and QC")
    m2.add_argument("--config", default="configs/m2_data_validation.yaml")

    m3 = sub.add_parser("m3", help="Run M3 baseline detection evaluation")
    m3.add_argument("--config", default="configs/m3_baseline_detection.yaml")

    m5 = sub.add_parser("m5", help="Run M5 ground-truth batch and inter-rater agreement")
    m5.add_argument("--config", default="configs/m5_ground_truth.yaml")

    m4 = sub.add_parser("m4", help="Run M4 temporal GBM detection evaluation")
    m4.add_argument("--config", default="configs/m4_temporal_model.yaml")

    m6 = sub.add_parser("m6", help="Run M6 forecasting and uncertainty evaluation")
    m6.add_argument("--config", default="configs/m6_forecasting.yaml")

    m7 = sub.add_parser("m7", help="Run M7 heat exposure surface evaluation")
    m7.add_argument("--config", default="configs/m7_heat_exposure.yaml")

    args = parser.parse_args()
    if args.command == "mvre":
        result = run_mvre(Path(args.config))
        print(f"MVRE complete. go={result['go_decision']}")
    elif args.command == "inventory":
        write_inventory_markdown(args.output)
        print(f"Inventory written to {args.output}")
    elif args.command == "m2":
        from canopy.experiments.m2_validation import run_m2_validation

        result = run_m2_validation(Path(args.config))
        print(f"M2 complete. proceed_to_m3={result['go_decision']['proceed_to_m3_detection']}")
    elif args.command == "m3":
        from pathlib import Path as P

        from canopy.experiments.m3_detection import run_m3_detection

        stack = P("data/processed/pilot/monthly_stack.nc")
        if not stack.exists():
            from canopy.experiments.m2_validation import run_m2_validation

            run_m2_validation(P("configs/m2_data_validation.yaml"))
        result = run_m3_detection(Path(args.config))
        print(f"M3 complete. proceed_to_m4={result['go_decision']['proceed_to_m4_temporal_model']}")
    elif args.command == "m5":
        from canopy.experiments.m5_ground_truth import run_m5_ground_truth

        result = run_m5_ground_truth(Path(args.config))
        print(f"M5 complete. kappa={result['inter_rater'].get('overall_kappa')}")
    elif args.command == "m4":
        from canopy.experiments.m4_detection import run_m4_detection

        result = run_m4_detection(Path(args.config))
        print(f"M4 complete. proceed_to_m6={result['go_decision']['proceed_to_m6_forecasting']}")
    elif args.command == "m6":
        from canopy.experiments.m6_forecasting import run_m6_forecasting

        result = run_m6_forecasting(Path(args.config))
        print(f"M6 complete. proceed_to_m7={result['go_decision']['proceed_to_m7_heat_exposure']}")
    elif args.command == "m7":
        from canopy.experiments.m7_heat_exposure import run_m7_heat_exposure

        result = run_m7_heat_exposure(Path(args.config))
        print(
            "M7 complete. "
            f"proceed_to_m8={result['go_decision']['proceed_to_m8_intervention_simulator']}"
        )


if __name__ == "__main__":
    main()
