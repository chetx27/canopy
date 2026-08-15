from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from canopy.config import ensure_dir, load_config, save_json
from canopy.data.stack_loader import load_monthly_stack, stack_to_cube
from canopy.evaluation.registry import ExperimentRegistry
from canopy.heat.layers import derive_pilot_heat_layers, mean_canopy_from_stack
from canopy.intervention.grid import build_intervention_grid, load_heat_surfaces_for_intervention
from canopy.intervention.simulator import InterventionParams
from canopy.optimization.evaluation import compare_strategies


def _strategy_figure(strategy_rows: dict[str, dict[str, Any]], out_path: Path) -> str:
    names = list(strategy_rows.keys())
    benefits = [strategy_rows[n]["total_benefit"] for n in names]
    fig, ax = plt.subplots(figsize=(11, 4))
    colors = ["darkgreen" if n == "canopy_optimizer" else "steelblue" for n in names]
    ax.bar(names, benefits, color=colors)
    ax.set_ylabel("Total modeled exposure reduction")
    ax.set_title("M9 optimization strategies (fixed budget)")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


def run_m9_optimization(config_path: str | Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    stack_path = Path(cfg["paths"]["processed_stack"])
    nodata = cfg.get("preprocessing", {}).get("nodata", -9999.0)
    ds = load_monthly_stack(stack_path)
    cube, times = stack_to_cube(ds, nodata=nodata)

    canopy = mean_canopy_from_stack(cube)
    layers = derive_pilot_heat_layers(canopy, seed=cfg.get("project", {}).get("seed", 42), cfg=cfg)
    exposure_surface = load_heat_surfaces_for_intervention(
        canopy,
        layers["lst"],
        layers["population"],
        layers["building_density"],
        cfg,
    )
    intervention_cells = build_intervention_grid(
        cube,
        canopy,
        layers["lst"],
        layers["population"],
        layers["building_density"],
        exposure_surface,
        cfg,
        seed=cfg.get("project", {}).get("seed", 42),
    )
    params = InterventionParams.from_config(cfg)
    comparison = compare_strategies(intervention_cells, params, cfg)

    min_gain = float(cfg.get("evaluation", {}).get("min_optimizer_gain_fraction", 0.05))
    gain_fraction = comparison["optimizer_gain_fraction_vs_best_baseline"]
    optimizer_result = comparison["raw_results"].get("canopy_optimizer")
    optimizer_ok = bool(
        optimizer_result
        and optimizer_result.total_benefit > 0
        and np.isfinite(gain_fraction)
        and gain_fraction >= min_gain
    )

    payload: dict[str, Any] = {
        "experiment_id": cfg.get("experiment_id", "m9"),
        "stack_path": str(stack_path),
        "n_times": len(times),
        "latest_time": times[-1] if times else None,
        "synthetic_layers": layers.get("synthetic", True),
        "n_eval_cells": len(intervention_cells),
        "baseline_total_exposure": comparison["baseline_total_exposure"],
        "budget_units": comparison["budget_units"],
        "water_budget_m3": comparison["water_budget_m3"],
        "strategies": comparison["strategies"],
        "best_baseline": comparison["best_baseline"],
        "optimizer_gain_vs_best_baseline": comparison["optimizer_gain_vs_best_baseline"],
        "optimizer_gain_fraction_vs_best_baseline": gain_fraction,
        "optimizer_vs_baseline_jaccard": comparison["optimizer_vs_baseline_jaccard"],
        "go_decision": {
            "proceed_to_m10_robustness": optimizer_ok,
            "optimizer_beats_best_baseline": optimizer_ok,
            "min_gain_fraction_required": min_gain,
            "note": "Benefits come from M8 intervention simulator counterfactuals under fixed budget.",
        },
    }

    out_dir = Path(cfg["paths"]["results"])
    ensure_dir(out_dir)
    fig = _strategy_figure(comparison["strategies"], out_dir / "optimization_strategy_comparison.png")
    payload["figure_paths"] = [fig]
    save_json(out_dir / "optimization_eval.json", payload)
    ExperimentRegistry().register(cfg.get("experiment_id", "m9"), payload)
    return payload
