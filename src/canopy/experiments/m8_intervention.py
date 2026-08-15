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
from canopy.intervention.simulator import (
    InterventionParams,
    aggregate_action_outcomes,
    counterfactual_all_actions,
    simulate_action,
)


def _action_summary_figure(summary: dict[str, dict[str, float]], out_path: Path) -> str:
    actions = [a for a in ["preserve", "restore", "plant"] if a in summary]
    reductions = [summary[a]["mean_exposure_reduction"] for a in actions]
    bpc = [summary[a]["mean_benefit_per_cost"] for a in actions]
    x = np.arange(len(actions))
    width = 0.35
    fig, ax1 = plt.subplots(figsize=(9, 4))
    ax1.bar(x - width / 2, reductions, width=width, label="mean exposure reduction", color="seagreen")
    ax1.set_ylabel("Exposure reduction")
    ax1.set_xticks(x)
    ax1.set_xticklabels(actions)
    ax1.set_title("M8 intervention counterfactuals (feasible cells)")
    ax2 = ax1.twinx()
    ax2.bar(x + width / 2, bpc, width=width, label="benefit / cost", color="darkorange", alpha=0.8)
    ax2.set_ylabel("Benefit per cost")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


def _serialize_outcome(outcome) -> dict[str, Any]:
    return {
        "action": outcome.action,
        "feasible": outcome.feasible,
        "exposure_before": outcome.exposure_before,
        "exposure_after": outcome.exposure_after,
        "exposure_reduction": outcome.exposure_reduction,
        "canopy_after": outcome.canopy_after,
        "lst_after": outcome.lst_after,
        "cost": outcome.cost,
        "water_m3": outcome.water_m3,
        "benefit_per_cost": outcome.benefit_per_cost,
        "note": outcome.note,
    }


def run_m8_intervention(config_path: str | Path) -> dict[str, Any]:
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
    cells = build_intervention_grid(
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

    action_outcomes: dict[str, list] = {"none": [], "preserve": [], "restore": [], "plant": []}
    cell_counterfactuals: list[dict[str, Any]] = []
    for cell in cells:
        cf = counterfactual_all_actions(cell, params)
        cell_counterfactuals.append(
            {
                "cell_id": cell.cell_id,
                "row": cell.row,
                "col": cell.col,
                "maturity": cell.maturity,
                "canopy": cell.canopy,
                "exposure": cell.exposure,
                "preserve_candidate": cell.preserve_candidate,
                "plantable": cell.plantable,
                "restorable": cell.restorable,
                "counterfactuals": {k: _serialize_outcome(v) for k, v in cf.items()},
            }
        )
        for action, outcome in cf.items():
            action_outcomes[action].append(outcome)

    action_summary = {
        action: aggregate_action_outcomes(outcomes)
        for action, outcomes in action_outcomes.items()
        if action != "none"
    }

    preserve_candidates = [c for c in cells if c.preserve_candidate]
    preserve_bpc = [
        simulate_action(c, "preserve", params).benefit_per_cost for c in preserve_candidates
    ]
    plant_feasible = [c for c in cells if c.plantable and c.water_feasible]
    plant_bpc = [simulate_action(c, "plant", params).benefit_per_cost for c in plant_feasible]

    preserve_median_bpc = float(np.median(preserve_bpc)) if preserve_bpc else float("nan")
    plant_median_bpc = float(np.median(plant_bpc)) if plant_bpc else float("nan")
    preserve_beats_plant = bool(
        np.isfinite(preserve_median_bpc)
        and np.isfinite(plant_median_bpc)
        and preserve_median_bpc > plant_median_bpc
    )

    preserve_reduction = action_summary.get("preserve", {}).get("mean_exposure_reduction", float("nan"))
    plant_reduction = action_summary.get("plant", {}).get("mean_exposure_reduction", float("nan"))
    actions_differ = bool(
        np.isfinite(preserve_reduction)
        and np.isfinite(plant_reduction)
        and abs(preserve_reduction - plant_reduction) > 1e-6
    )
    min_preserve_candidates = int(cfg.get("evaluation", {}).get("min_preserve_candidates", 10))
    enough_candidates = len(preserve_candidates) >= min_preserve_candidates

    payload: dict[str, Any] = {
        "experiment_id": cfg.get("experiment_id", "m8"),
        "stack_path": str(stack_path),
        "n_times": len(times),
        "latest_time": times[-1] if times else None,
        "synthetic_layers": layers.get("synthetic", True),
        "n_eval_cells": len(cells),
        "n_preserve_candidates": len(preserve_candidates),
        "n_plant_feasible": len(plant_feasible),
        "n_restorable": sum(1 for c in cells if c.restorable),
        "intervention_params": params.__dict__,
        "action_summary": action_summary,
        "preserve_vs_plant": {
            "preserve_median_benefit_per_cost": preserve_median_bpc,
            "plant_median_benefit_per_cost": plant_median_bpc,
            "preserve_beats_plant_on_mature_cells": preserve_beats_plant,
        },
        "sample_counterfactuals": cell_counterfactuals[: min(5, len(cell_counterfactuals))],
        "go_decision": {
            "proceed_to_m9_optimizer": bool(
                enough_candidates and preserve_beats_plant and actions_differ
            ),
            "preserve_beats_plant_on_mature_cells": preserve_beats_plant,
            "counterfactuals_differ_by_action": actions_differ,
            "enough_preserve_candidates": enough_candidates,
            "note": "Modeled scenarios only. Parameters are configurable, not observed causal impacts.",
        },
    }

    out_dir = Path(cfg["paths"]["results"])
    ensure_dir(out_dir)
    fig = _action_summary_figure(action_summary, out_dir / "intervention_counterfactuals.png")
    payload["figure_paths"] = [fig]
    save_json(out_dir / "intervention_sim_eval.json", payload)
    ExperimentRegistry().register(cfg.get("experiment_id", "m8"), payload)
    return payload
