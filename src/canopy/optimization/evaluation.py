from __future__ import annotations

from typing import Any

import numpy as np

from canopy.intervention.simulator import InterventionCell, InterventionParams, simulate_action
from canopy.optimization.engine import (
    BenefitFn,
    CellState,
    OptimizationConfig,
    OptimizationResult,
    greedy_optimize,
    random_baseline,
    rank_baseline,
)


def to_cell_states(cells: list[InterventionCell]) -> list[CellState]:
    return [
        CellState(
            cell_id=cell.cell_id,
            lst=cell.lst,
            canopy=cell.canopy,
            population=cell.population,
            maturity=cell.maturity,
            water_feasible=cell.water_feasible,
            plantable=cell.plantable,
            preserve_candidate=cell.preserve_candidate,
            exposure=cell.exposure,
            restorable=cell.restorable,
        )
        for cell in cells
    ]


def make_simulator_benefit_fn(
    intervention_cells: list[InterventionCell],
    params: InterventionParams,
) -> BenefitFn:
    by_id = {cell.cell_id: cell for cell in intervention_cells}

    def benefit_fn(cell: CellState, action: str) -> float:
        outcome = simulate_action(by_id[cell.cell_id], action, params)
        return outcome.exposure_reduction if outcome.feasible else 0.0

    return benefit_fn


def optimization_config_from_config(cfg: dict[str, Any], params: InterventionParams) -> OptimizationConfig:
    opt = cfg.get("optimization", {})
    return OptimizationConfig(
        budget_units=int(opt.get("budget_units", 1000)),
        water_budget_m3=float(opt.get("water_budget_m3", 50000.0)),
        preserve_cost=params.preserve_cost,
        restore_cost=params.restore_cost,
        plant_cost=params.plant_cost,
        preserve_water=params.preserve_water_m3,
        restore_water=params.restore_water_m3,
        plant_water=params.plant_water_m3,
        preserve_benefit_factor=float(opt.get("preserve_benefit_factor", 1.5)),
        allow_preserve=bool(opt.get("allow_preserve", True)),
        allow_restore=bool(opt.get("allow_restore", True)),
        allow_plant=bool(opt.get("allow_plant", True)),
    )


def serialize_result(result: OptimizationResult) -> dict[str, Any]:
    return {
        "strategy": result.strategy,
        "n_selected": len(result.selected),
        "total_benefit": result.total_benefit,
        "total_cost": result.total_cost,
        "total_water": result.total_water,
        "benefit_per_cost": result.total_benefit / max(result.total_cost, 1e-9),
        "selected_actions": [{"cell_id": cid, "action": action} for cid, action in result.selected[:20]],
    }


def selected_cell_jaccard(a: OptimizationResult, b: OptimizationResult) -> float:
    sa = {cell_id for cell_id, _ in a.selected}
    sb = {cell_id for cell_id, _ in b.selected}
    if not sa and not sb:
        return float("nan")
    if not sa or not sb:
        return 0.0
    return float(len(sa & sb) / len(sa | sb))


def run_strategy(
    strategy: str,
    cells: list[CellState],
    opt_cfg: OptimizationConfig,
    benefit_fn: BenefitFn,
    seed: int,
) -> OptimizationResult:
    rng = np.random.default_rng(seed)
    if strategy == "random":
        return random_baseline(cells, opt_cfg, rng, benefit_fn=benefit_fn)
    if strategy == "canopy_optimizer":
        return greedy_optimize(cells, opt_cfg, plant_only=False, benefit_fn=benefit_fn)
    if strategy == "canopy_plant_only":
        return greedy_optimize(cells, opt_cfg, plant_only=True, benefit_fn=benefit_fn)
    if strategy in {"max_lst", "min_canopy", "max_population", "greedy_exposure"}:
        return rank_baseline(cells, opt_cfg, strategy, benefit_fn=benefit_fn)
    raise ValueError(f"Unknown strategy: {strategy}")


def compare_strategies(
    intervention_cells: list[InterventionCell],
    params: InterventionParams,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    cells = to_cell_states(intervention_cells)
    benefit_fn = make_simulator_benefit_fn(intervention_cells, params)
    opt_cfg = optimization_config_from_config(cfg, params)
    strategies = cfg.get("optimization", {}).get(
        "strategies",
        [
            "random",
            "max_lst",
            "min_canopy",
            "max_population",
            "greedy_exposure",
            "canopy_plant_only",
            "canopy_optimizer",
        ],
    )
    seed = int(cfg.get("project", {}).get("seed", 42))
    baseline_exposure = float(sum(c.exposure for c in cells))

    results: dict[str, OptimizationResult] = {}
    serialized: dict[str, dict[str, Any]] = {}
    for strategy in strategies:
        result = run_strategy(strategy, cells, opt_cfg, benefit_fn, seed=seed)
        results[strategy] = result
        row = serialize_result(result)
        row["exposure_reduction_fraction"] = result.total_benefit / max(baseline_exposure, 1e-9)
        serialized[strategy] = row

    baselines = [s for s in strategies if s not in {"canopy_optimizer"}]
    best_baseline = max(baselines, key=lambda s: results[s].total_benefit)
    optimizer = results.get("canopy_optimizer")
    optimizer_benefit = optimizer.total_benefit if optimizer else 0.0
    best_baseline_benefit = results[best_baseline].total_benefit
    gain = optimizer_benefit - best_baseline_benefit
    gain_fraction = gain / max(best_baseline_benefit, 1e-9)

    overlap = {}
    if optimizer:
        for strategy in baselines:
            overlap[strategy] = selected_cell_jaccard(optimizer, results[strategy])

    return {
        "baseline_total_exposure": baseline_exposure,
        "budget_units": opt_cfg.budget_units,
        "water_budget_m3": opt_cfg.water_budget_m3,
        "strategies": serialized,
        "best_baseline": best_baseline,
        "optimizer_gain_vs_best_baseline": gain,
        "optimizer_gain_fraction_vs_best_baseline": gain_fraction,
        "optimizer_vs_baseline_jaccard": overlap,
        "raw_results": results,
    }
