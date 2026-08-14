from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np


@dataclass
class MonthQC:
    month: str
    n_observations: int
    valid_pixel_fraction: float
    ndvi_min: float
    ndvi_max: float
    ndvi_mean: float
    ndvi_std: float
    cloud_gap: bool


@dataclass
class PilotQCReport:
    aoi_path: str
    crs: str
    resolution_m: float
    start_date: str
    end_date: str
    n_months: int
    months: list[MonthQC] = field(default_factory=list)
    overall_valid_fraction: float = 0.0
    monsoon_mean_valid_fraction: float = 0.0
    non_monsoon_mean_valid_fraction: float = 0.0
    ndvi_global_min: float = 0.0
    ndvi_global_max: float = 0.0
    grid_shape: tuple[int, int] = (0, 0)
    alignment_ok: bool = True
    synthetic: bool = False
    go_decision: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "aoi_path": self.aoi_path,
            "crs": self.crs,
            "resolution_m": self.resolution_m,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "n_months": self.n_months,
            "months": [m.__dict__ for m in self.months],
            "overall_valid_fraction": self.overall_valid_fraction,
            "monsoon_mean_valid_fraction": self.monsoon_mean_valid_fraction,
            "non_monsoon_mean_valid_fraction": self.non_monsoon_mean_valid_fraction,
            "ndvi_global_min": self.ndvi_global_min,
            "ndvi_global_max": self.ndvi_global_max,
            "grid_shape": list(self.grid_shape),
            "alignment_ok": self.alignment_ok,
            "synthetic": self.synthetic,
            "go_decision": self.go_decision,
        }


def compute_month_qc(
    ndvi: np.ndarray,
    month: str,
    n_observations: int,
    nodata: float = -9999.0,
    monsoon_months: set[int] | None = None,
) -> MonthQC:
    arr = np.asarray(ndvi, dtype=float)
    if nodata is not None:
        valid_mask = np.isfinite(arr) & (arr != nodata)
    else:
        valid_mask = np.isfinite(arr)
    valid = arr[valid_mask]
    valid_frac = float(valid_mask.mean()) if valid_mask.size else 0.0
    month_num = datetime.strptime(month, "%Y-%m").month
    monsoon = monsoon_months or {6, 7, 8, 9, 10}
    if valid.size == 0:
        return MonthQC(
            month=month,
            n_observations=n_observations,
            valid_pixel_fraction=valid_frac,
            ndvi_min=float("nan"),
            ndvi_max=float("nan"),
            ndvi_mean=float("nan"),
            ndvi_std=float("nan"),
            cloud_gap=valid_frac < 0.3 or month_num in monsoon and valid_frac < 0.5,
        )
    return MonthQC(
        month=month,
        n_observations=n_observations,
        valid_pixel_fraction=valid_frac,
        ndvi_min=float(np.min(valid)),
        ndvi_max=float(np.max(valid)),
        ndvi_mean=float(np.mean(valid)),
        ndvi_std=float(np.std(valid)),
        cloud_gap=valid_frac < 0.3 or (month_num in monsoon and valid_frac < 0.5),
    )


def build_qc_report(
    monthly_ndvi: dict[str, np.ndarray],
    monthly_obs_counts: dict[str, int],
    cfg: dict[str, Any],
    synthetic: bool = False,
) -> PilotQCReport:
    qc_cfg = cfg.get("qc", {})
    monsoon = set(qc_cfg.get("monsoon_months", [6, 7, 8, 9, 10]))
    nodata = cfg.get("preprocessing", {}).get("nodata", -9999)
    months_sorted = sorted(monthly_ndvi.keys())
    month_qcs = [
        compute_month_qc(
            monthly_ndvi[m],
            m,
            monthly_obs_counts.get(m, 0),
            nodata=nodata,
            monsoon_months=monsoon,
        )
        for m in months_sorted
    ]
    valid_fracs = [m.valid_pixel_fraction for m in month_qcs if np.isfinite(m.valid_pixel_fraction)]
    monsoon_fracs = [
        m.valid_pixel_fraction
        for m in month_qcs
        if datetime.strptime(m.month, "%Y-%m").month in monsoon and np.isfinite(m.valid_pixel_fraction)
    ]
    non_monsoon_fracs = [
        m.valid_pixel_fraction
        for m in month_qcs
        if datetime.strptime(m.month, "%Y-%m").month not in monsoon and np.isfinite(m.valid_pixel_fraction)
    ]
    all_valid = []
    for m in months_sorted:
        arr = np.asarray(monthly_ndvi[m], dtype=float)
        mask = np.isfinite(arr) & (arr != nodata)
        if mask.any():
            all_valid.append(arr[mask])
    concat = np.concatenate(all_valid) if all_valid else np.array([])
    first = monthly_ndvi[months_sorted[0]]
    shapes = {monthly_ndvi[m].shape for m in months_sorted}
    alignment_ok = len(shapes) == 1
    report = PilotQCReport(
        aoi_path=cfg["study_area"]["aoi_path"],
        crs=cfg["project"]["crs"],
        resolution_m=float(cfg["study_area"]["grid_resolution_m"]),
        start_date=cfg["temporal"]["start_date"],
        end_date=cfg["temporal"]["end_date"],
        n_months=len(months_sorted),
        months=month_qcs,
        overall_valid_fraction=float(np.mean(valid_fracs)) if valid_fracs else 0.0,
        monsoon_mean_valid_fraction=float(np.mean(monsoon_fracs)) if monsoon_fracs else 0.0,
        non_monsoon_mean_valid_fraction=float(np.mean(non_monsoon_fracs)) if non_monsoon_fracs else 0.0,
        ndvi_global_min=float(np.min(concat)) if concat.size else float("nan"),
        ndvi_global_max=float(np.max(concat)) if concat.size else float("nan"),
        grid_shape=first.shape,
        alignment_ok=alignment_ok,
        synthetic=synthetic,
    )
    ndvi_range = qc_cfg.get("ndvi_valid_range", [-0.2, 1.0])
    min_months = qc_cfg.get("min_months_required", 12)
    go = (
        report.n_months >= min_months
        and alignment_ok
        and report.overall_valid_fraction >= (1.0 - qc_cfg.get("max_missing_fraction", 0.5))
        and (concat.size == 0 or (report.ndvi_global_min >= ndvi_range[0] and report.ndvi_global_max <= ndvi_range[1]))
    )
    report.go_decision = {
        "proceed_to_m3_detection": bool(go),
        "n_months_ok": report.n_months >= min_months,
        "alignment_ok": alignment_ok,
        "overall_valid_fraction": report.overall_valid_fraction,
        "monsoon_mean_valid_fraction": report.monsoon_mean_valid_fraction,
        "note": "Synthetic QC only if no real imagery was processed.",
    }
    return report
