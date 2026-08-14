from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from canopy.config import ensure_dir, save_json
from canopy.data.preprocess import harmonize_monthly_stack, load_monthly_tifs, write_monthly_stack
from canopy.data.qc import PilotQCReport, build_qc_report
from canopy.data.synthetic import generate_synthetic_pilot_stack
from canopy.evaluation.registry import ExperimentRegistry


def _write_qc_figures(report: PilotQCReport, fig_dir: Path) -> list[str]:
    ensure_dir(fig_dir)
    paths: list[str] = []
    months = [m.month for m in report.months]
    valid_frac = [m.valid_pixel_fraction for m in report.months]
    obs = [m.n_observations for m in report.months]
    means = [m.ndvi_mean for m in report.months]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(months, valid_frac, color="steelblue")
    ax.set_title("Valid pixel fraction by month")
    ax.set_ylabel("Valid fraction")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    p1 = fig_dir / "valid_fraction_by_month.png"
    fig.savefig(p1, dpi=120)
    plt.close(fig)
    paths.append(str(p1))

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(months, obs, marker="o")
    ax.set_title("Source observation count by month")
    ax.set_ylabel("Observations")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    p2 = fig_dir / "observations_by_month.png"
    fig.savefig(p2, dpi=120)
    plt.close(fig)
    paths.append(str(p2))

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(months, means, marker="o", color="forestgreen")
    ax.set_title("Mean NDVI (valid pixels)")
    ax.set_ylabel("NDVI")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    p3 = fig_dir / "mean_ndvi_by_month.png"
    fig.savefig(p3, dpi=120)
    plt.close(fig)
    paths.append(str(p3))
    return paths


def _write_preprocessing_spec(cfg: dict[str, Any], report: PilotQCReport, path: Path) -> None:
    prep = cfg.get("preprocessing", {})
    lines = [
        "# Pilot AOI Preprocessing Specification",
        "",
        f"Generated: M2 validation",
        "",
        "## AOI",
        f"- Path: `{cfg['study_area']['aoi_path']}`",
        f"- CRS: `{cfg['project']['crs']}`",
        f"- Resolution: {cfg['study_area']['grid_resolution_m']} m",
        "",
        "## Temporal",
        f"- Start: {cfg['temporal']['start_date']}",
        f"- End: {cfg['temporal']['end_date']}",
        f"- Composite: {cfg['temporal']['composite']}",
        "",
        "## Cloud masking",
        f"- SCL classes masked: {prep.get('cloud_mask_scl', [])}",
        f"- Max scene cloud fraction: {prep.get('max_cloud_fraction', 0.6)}",
        "",
        "## Compositing",
        f"- Method: {prep.get('composite_method', 'median')}",
        f"- Nodata: {prep.get('nodata', -9999)}",
        "",
        "## Output grid",
        f"- Shape: {report.grid_shape}",
        f"- Alignment OK: {report.alignment_ok}",
        "",
        "## QC summary",
        f"- Months: {report.n_months}",
        f"- Overall valid fraction: {report.overall_valid_fraction:.3f}",
        f"- Monsoon valid fraction: {report.monsoon_mean_valid_fraction:.3f}",
        f"- Synthetic: {report.synthetic}",
        f"- Go to M3: {report.go_decision.get('proceed_to_m3_detection')}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def run_m2_validation(config_path: str | Path) -> dict[str, Any]:
    from canopy.config import load_config

    cfg = load_config(config_path)
    raw_dir = Path(cfg["paths"]["raw_s2"])
    synthetic = False
    meta: dict[str, Any] = {}

    if raw_dir.exists() and any(raw_dir.glob("**/*.tif")):
        monthly, counts, meta = load_monthly_tifs(raw_dir)
    else:
        monthly, counts = generate_synthetic_pilot_stack(cfg)
        synthetic = True

    monthly = harmonize_monthly_stack(monthly)
    report = build_qc_report(monthly, counts, cfg, synthetic=synthetic)

    stack_path = Path(cfg["paths"]["processed_stack"])
    write_monthly_stack(
        monthly,
        stack_path,
        crs=cfg["project"]["crs"],
        transform=meta.get("transform"),
        nodata=cfg.get("preprocessing", {}).get("nodata", -9999.0),
    )

    fig_dir = Path(cfg["paths"]["qc_figures"])
    figure_paths = _write_qc_figures(report, fig_dir)

    qc_path = Path(cfg["paths"]["qc_report"])
    payload = report.to_dict()
    payload["figure_paths"] = figure_paths
    payload["processed_stack"] = str(stack_path)
    save_json(qc_path, payload)

    spec_path = Path(cfg["paths"]["preprocessing_spec"])
    _write_preprocessing_spec(cfg, report, spec_path)

    ExperimentRegistry().register(cfg.get("experiment_id", "m2"), payload)
    return payload
