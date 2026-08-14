#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.config import load_config, save_json
from canopy.experiments.mvre import run_mvre


def main() -> None:
    parser = argparse.ArgumentParser(description="CANOPY end-to-end research pipeline stub")
    parser.add_argument("--config", default="configs/mvre_detection.yaml")
    parser.add_argument("--skip-mvre", action="store_true")
    args = parser.parse_args()
    cfg = load_config(ROOT / args.config)
    summary = {"pipeline": "canopy", "stages": []}
    if not args.skip_mvre:
        mvre = run_mvre(ROOT / args.config)
        summary["stages"].append({"name": "mvre_detection", "result": mvre["go_decision"]})
    out = Path(cfg.get("paths", {}).get("results", "results")) / "pipeline_summary.json"
    save_json(out, summary)
    print(summary)


if __name__ == "__main__":
    main()
