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


if __name__ == "__main__":
    main()
