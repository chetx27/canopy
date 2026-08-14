#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.config import load_config
from canopy.data.gee_export import check_gee_auth, export_monthly_composites


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Sentinel-2 monthly NDVI composites via GEE")
    parser.add_argument("--config", default="configs/m2_data_validation.yaml")
    parser.add_argument("--aoi", default=None)
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--check-auth", action="store_true")
    args = parser.parse_args()

    if args.check_auth:
        ok = check_gee_auth()
        print("gee_authenticated" if ok else "gee_not_authenticated")
        raise SystemExit(0 if ok else 1)

    cfg = load_config(ROOT / args.config)
    aoi = args.aoi or cfg["study_area"]["aoi_path"]
    start = args.start or cfg["temporal"]["start_date"]
    end = args.end or cfg["temporal"]["end_date"]
    out = args.out or cfg["paths"]["raw_s2"]

    if not Path(aoi).exists():
        raise SystemExit(f"AOI not found: {aoi}")

    manifest = export_monthly_composites(aoi, start, end, out, cfg=cfg)
    print(f"Export manifest written with {len(manifest['months'])} months")
    print(f"Collection size: {manifest['collection_size']}")


if __name__ == "__main__":
    main()
