from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from canopy.config import load_config, save_json
from canopy.detection.baselines import detection_index, run_detector
from canopy.evaluation.metrics import binary_detection_metrics
from canopy.evaluation.registry import ExperimentRegistry
from canopy.temporal.persistence import detection_delay_days


def simulate_ndvi_series(label: str, n_months: int, seed: int) -> tuple[np.ndarray, np.ndarray, int | None]:
    rng = np.random.default_rng(seed)
    times = np.arange(n_months, dtype=float)
    seasonal = 0.15 * np.sin(2 * np.pi * times / 12.0)
    base = 0.55 + seasonal + rng.normal(0, 0.03, size=n_months)
    event_index = None
    if label == "persistent_loss":
        event_index = n_months // 2
        base[event_index:] -= np.linspace(0.05, 0.35, n_months - event_index)
    elif label == "seasonal":
        base[5:8] -= 0.2
    base = np.clip(base, 0.05, 0.95)
    return times, base, event_index


def load_labels(cfg: dict[str, Any]) -> pd.DataFrame:
    labels_path = Path(cfg["labels"]["path"])
    if labels_path.exists():
        return pd.read_csv(labels_path)
    rows = []
    seed = cfg.get("project", {}).get("seed", 42)
    rng = np.random.default_rng(seed)
    for label in ["stable", "seasonal", "persistent_loss"]:
        for i in range(50):
            rows.append({"cell_id": f"{label}_{i}", "label": label, "seed": int(rng.integers(0, 1_000_000))})
    return pd.DataFrame(rows)


def run_mvre(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    labels_df = load_labels(cfg)
    methods = cfg["detection"]["methods"]
    det_cfg = cfg["detection"]
    n_months = 18
    results: dict[str, Any] = {
        "experiment_id": cfg.get("experiment_id", "mvre"),
        "methods": {},
        "go_decision": None,
    }

    for method in methods:
        y_true = []
        y_pred = []
        stable_mask = []
        delays = []
        for row in labels_df.itertuples(index=False):
            seed = int(getattr(row, "seed", hash(row.cell_id) % 1_000_000))
            times, series, event_index = simulate_ndvi_series(row.label, n_months, seed)
            det = run_detector(method, series, times, **det_cfg)
            predicted = bool(det.flags.any())
            y_true.append(row.label == "persistent_loss")
            y_pred.append(predicted)
            stable_mask.append(row.label == "stable")
            if row.label == "persistent_loss" and event_index is not None:
                idx = detection_index(det)
                if idx is not None:
                    delay = detection_delay_days(idx, event_index, days_per_step=30.0)
                    if delay is not None:
                        delays.append(delay)
        metrics = binary_detection_metrics(
            np.array(y_true, dtype=bool),
            np.array(y_pred, dtype=bool),
            stable_mask=np.array(stable_mask, dtype=bool),
        )
        results["methods"][method] = {
            "persistent_f1": metrics.f1,
            "precision": metrics.precision,
            "recall": metrics.recall,
            "false_positive_rate": metrics.false_positive_rate,
            "median_detection_delay_days": float(np.median(delays)) if delays else None,
            "n_delay_samples": len(delays),
        }

    baseline = results["methods"].get("ndvi_threshold", {})
    candidate = results["methods"].get("harmonic_persistence", {})
    f1_gain = (candidate.get("persistent_f1") or 0.0) - (baseline.get("persistent_f1") or 0.0)
    delay_gain = None
    if baseline.get("median_detection_delay_days") is not None and candidate.get("median_detection_delay_days") is not None:
        delay_gain = baseline["median_detection_delay_days"] - candidate["median_detection_delay_days"]

    go = f1_gain >= cfg["evaluation"].get("go_threshold_f1_gain", 5.0) / 100.0
    if delay_gain is not None:
        go = go or delay_gain >= cfg["evaluation"].get("go_threshold_delay_days", 30)

    results["go_decision"] = {
        "proceed_to_full_pipeline": bool(go),
        "f1_gain_vs_ndvi_threshold": f1_gain,
        "delay_gain_days_vs_ndvi_threshold": delay_gain,
        "note": "Uses synthetic series unless labels CSV is provided at cfg.labels.path",
    }

    out_dir = Path(cfg["paths"]["results"])
    out_dir.mkdir(parents=True, exist_ok=True)
    save_json(out_dir / "detection_pilot.json", results)
    ExperimentRegistry().register(cfg.get("experiment_id", "mvre"), results)
    return results
