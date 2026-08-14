#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.experiments.mvre import run_mvre


def main() -> None:
    config = ROOT / "configs" / "mvre_detection.yaml"
    result = run_mvre(config)
    print(result)


if __name__ == "__main__":
    main()
