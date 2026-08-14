#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canopy.config import load_config, save_json
from canopy.evaluation.registry import ExperimentRegistry
from canopy.heat.exposure import population_weighted_exposure, total_exposure
from canopy.optimization.engine import CellState, OptimizationConfig, greedy_optimize, random_baseline, rank_baseline


def synthetic_cells(n: int = 200, seed: int = 42) -> list[CellState]:
    rng = np.random.default_rng(seed)
    cells = []
    for i in range(n):
        canopy = float(rng.uniform(0.05, 0.8))
        lst = float(rng.uniform(28, 42) - 4 * canopy)
        pop = float(rng.uniform(0, 200))
        maturity = float(rng.uniform(0, 1))
        exposure = float(population_weighted_exposure(np.array([lst]), np.array([pop]))[0])
        cells.append(
            CellState(
                cell_id=i,
                lst=lst,
                canopy=canopy,
                population=pop,
                maturity=maturity,
                water_feasible=bool(rng.random() > 0.2),
                plantable=bool(rng.random() > 0.35),
                preserve_candidate=maturity > 0.6 and canopy > 0.4,
                exposure=exposure,
            )
        )
    return cells


def main() -> None:
    cfg = load_config(ROOT / "configs/experiment_optimization.yaml")
    opt_cfg = OptimizationConfig(
        budget_units=cfg["optimization"]["budget_units"],
        water_budget_m3=cfg["optimization"]["water_budget_m3"],
    )
    cells = synthetic_cells(300, seed=cfg.get("project", {}).get("seed", 42))
    baseline_exposure = total_exposure(np.array([c.exposure for c in cells]))
    strategies = cfg["optimization"]["strategies"]
    rng = np.random.default_rng(42)
    outcomes = {}
    for strategy in strategies:
        if strategy == "random":
            res = random_baseline(cells, opt_cfg, rng)
        elif strategy == "canopy_optimizer":
            res = greedy_optimize(cells, opt_cfg, plant_only=False)
        elif strategy == "canopy_plant_only":
            res = greedy_optimize(cells, opt_cfg, plant_only=True)
        elif strategy in {"max_lst", "min_canopy", "max_population", "greedy_exposure"}:
            res = rank_baseline(cells, opt_cfg, strategy)
        else:
            continue
        outcomes[strategy] = {
            "total_benefit": res.total_benefit,
            "total_cost": res.total_cost,
            "total_water": res.total_water,
            "n_selected": len(res.selected),
            "exposure_reduction_fraction": res.total_benefit / max(baseline_exposure, 1e-9),
        }
    payload = {"baseline_total_exposure": baseline_exposure, "strategies": outcomes}
    out = Path(cfg["paths"]["results"]) / "baseline_comparison.json"
    save_json(out, payload)
    ExperimentRegistry().register(cfg["experiment_id"], payload)
    print(payload)


if __name__ == "__main__":
    main()
