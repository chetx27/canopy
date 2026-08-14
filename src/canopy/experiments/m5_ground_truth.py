from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from canopy.config import ensure_dir, load_config, save_json
from canopy.data.annotation import (
    generate_annotation_batch,
    inter_rater_report,
    merge_rater_labels,
    simulate_rater_b_from_reference,
)
from canopy.data.labeling import auto_label_cells_from_stack
from canopy.data.stack_loader import load_monthly_stack, stack_to_cube
from canopy.evaluation.registry import ExperimentRegistry


def run_m5_ground_truth(config_path: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(config_path, dict):
        cfg = config_path
    else:
        cfg = load_config(config_path)
    stack_path = Path(cfg["paths"]["processed_stack"])
    nodata = cfg.get("preprocessing", {}).get("nodata", -9999.0)
    ds = load_monthly_stack(stack_path)
    cube, times = stack_to_cube(ds, nodata=nodata)

    gt_cfg = cfg.get("ground_truth", {})
    n_total = int(gt_cfg.get("n_cells", 500))
    seed = cfg.get("project", {}).get("seed", 42)

    batch_path = Path(cfg["paths"]["annotation_batch"])
    ensure_dir(batch_path.parent)
    batch = generate_annotation_batch(cube, times, n_total=n_total, seed=seed)
    batch.to_csv(batch_path, index=False)

    rater_a_path = Path(cfg["paths"]["rater_a"])
    rater_b_path = Path(cfg["paths"]["rater_b"])
    merged_path = Path(cfg["paths"]["merged_labels"])

    agreement_report: dict[str, Any] = {"status": "pending_human_annotation"}
    merge_meta: dict[str, Any] = {}

    if rater_a_path.exists() and rater_b_path.exists():
        df_a = pd.read_csv(rater_a_path)
        df_b = pd.read_csv(rater_b_path)
        agreement_report = inter_rater_report(df_a, df_b)
        merged, merge_meta = merge_rater_labels(
            df_a, df_b, min_kappa=gt_cfg.get("min_kappa", 0.6)
        )
        merged.to_csv(merged_path, index=False)
    elif gt_cfg.get("simulate_raters_for_pipeline_test", False):
        reference = auto_label_cells_from_stack(
            cube, times, n_per_class=max(20, n_total // 3), seed=seed
        )
        reference = reference.rename(columns={"label": "label_a"})
        reference["event_month"] = reference.get("event_month", "")
        reference["label_b"] = reference["label_a"]
        sim = simulate_rater_b_from_reference(
            reference.rename(columns={"label_a": "label"}),
            agreement_rate=gt_cfg.get("simulated_agreement_rate", 0.85),
            seed=seed,
        )
        sim_a = sim[["cell_id", "row", "col", "label_a"]].rename(columns={"label_a": "label"})
        sim_b = sim[["cell_id", "row", "col", "label_b"]].rename(columns={"label_b": "label"})
        if "event_month" in sim.columns:
            sim_a["event_month"] = sim["event_month"]
            sim_b["event_month"] = sim["event_month"]
        sim_a.to_csv(rater_a_path, index=False)
        sim_b.to_csv(rater_b_path, index=False)
        agreement_report = inter_rater_report(sim_a, sim_b)
        merged, merge_meta = merge_rater_labels(sim_a, sim_b, min_kappa=gt_cfg.get("min_kappa", 0.6))
        merged.to_csv(merged_path, index=False)
        agreement_report["simulated_raters"] = True

    payload: dict[str, Any] = {
        "experiment_id": cfg.get("experiment_id", "m5"),
        "annotation_batch_path": str(batch_path),
        "n_batch_cells": len(batch),
        "rater_a_path": str(rater_a_path),
        "rater_b_path": str(rater_b_path),
        "merged_labels_path": str(merged_path),
        "inter_rater": agreement_report,
        "merge": merge_meta,
        "go_decision": {
            "ready_for_m4_training": merged_path.exists() and merge_meta.get("n_merged_labels", 0) >= gt_cfg.get("min_merged_labels", 100),
            "quality_ok": merge_meta.get("quality_ok", False),
            "note": "Fill annotation batch or provide rater CSVs for real ground truth.",
        },
    }

    out_dir = Path(cfg["paths"]["results"])
    ensure_dir(out_dir)
    save_json(out_dir / "ground_truth_report.json", payload)
    ExperimentRegistry().register(cfg.get("experiment_id", "m5"), payload)
    return payload
