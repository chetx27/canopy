from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class CellState:
    cell_id: int
    lst: float
    canopy: float
    population: float
    maturity: float
    water_feasible: bool
    plantable: bool
    preserve_candidate: bool
    exposure: float = 0.0


@dataclass
class OptimizationConfig:
    budget_units: int = 1000
    water_budget_m3: float = 50000.0
    preserve_cost: float = 1.0
    restore_cost: float = 2.0
    plant_cost: float = 3.0
    preserve_water: float = 5.0
    restore_water: float = 15.0
    plant_water: float = 25.0
    preserve_benefit_factor: float = 1.5
    allow_preserve: bool = True
    allow_restore: bool = True
    allow_plant: bool = True


@dataclass
class OptimizationResult:
    selected: list[tuple[int, str]]
    total_benefit: float
    total_cost: float
    total_water: float
    strategy: str
    explanations: dict[int, list[str]] = field(default_factory=dict)


def _benefit(cell: CellState, action: str, cfg: OptimizationConfig) -> float:
    base = cell.exposure
    if action == "preserve":
        return base * 0.8 * cfg.preserve_benefit_factor
    if action == "restore":
        return base * 0.5
    if action == "plant":
        return base * 0.35
    return 0.0


def _cost(action: str, cfg: OptimizationConfig) -> float:
    return {"preserve": cfg.preserve_cost, "restore": cfg.restore_cost, "plant": cfg.plant_cost}.get(action, 0.0)


def _water(action: str, cfg: OptimizationConfig) -> float:
    return {"preserve": cfg.preserve_water, "restore": cfg.restore_water, "plant": cfg.plant_water}.get(action, 0.0)


def greedy_optimize(cells: list[CellState], cfg: OptimizationConfig, plant_only: bool = False) -> OptimizationResult:
    remaining_budget = cfg.budget_units
    remaining_water = cfg.water_budget_m3
    selected: list[tuple[int, str]] = []
    explanations: dict[int, list[str]] = {}
    total_benefit = 0.0
    total_cost = 0.0
    total_water = 0.0
    candidates: list[tuple[float, int, str, float, float]] = []
    for cell in cells:
        actions = []
        if not plant_only and cfg.allow_preserve and cell.preserve_candidate:
            actions.append("preserve")
        if cfg.allow_restore and cell.plantable:
            actions.append("restore")
        if cfg.allow_plant and cell.plantable:
            actions.append("plant")
        for action in actions:
            if action in {"restore", "plant"} and not cell.water_feasible:
                continue
            benefit = _benefit(cell, action, cfg)
            cost = _cost(action, cfg)
            water = _water(action, cfg)
            if cost <= 0:
                continue
            ratio = benefit / cost
            candidates.append((ratio, cell.cell_id, action, benefit, cost, water))
    candidates.sort(reverse=True, key=lambda x: x[0])
    used_cells: set[int] = set()
    for ratio, cell_id, action, benefit, cost, water in candidates:
        if cell_id in used_cells:
            continue
        if cost > remaining_budget or water > remaining_water:
            continue
        selected.append((cell_id, action))
        used_cells.add(cell_id)
        total_benefit += benefit
        total_cost += cost
        total_water += water
        remaining_budget -= cost
        remaining_water -= water
        reasons = [f"high_exposure={benefit:.3f}", f"benefit_cost_ratio={ratio:.3f}"]
        if action == "preserve":
            reasons.append("mature_canopy_preservation")
        if action == "plant":
            reasons.append("plantable_feasible_site")
        explanations[cell_id] = reasons
    strategy = "canopy_plant_only" if plant_only else "canopy_optimizer"
    return OptimizationResult(
        selected=selected,
        total_benefit=total_benefit,
        total_cost=total_cost,
        total_water=total_water,
        strategy=strategy,
        explanations=explanations,
    )


def random_baseline(cells: list[CellState], cfg: OptimizationConfig, rng: np.random.Generator) -> OptimizationResult:
    plantable = [c for c in cells if c.plantable and c.water_feasible]
    rng.shuffle(plantable)
    selected = []
    remaining = cfg.budget_units
    total_benefit = 0.0
    total_cost = 0.0
    total_water = 0.0
    for cell in plantable:
        cost = _cost("plant", cfg)
        water = _water("plant", cfg)
        if cost > remaining:
            break
        selected.append((cell.cell_id, "plant"))
        total_benefit += _benefit(cell, "plant", cfg)
        total_cost += cost
        total_water += water
        remaining -= cost
    return OptimizationResult(
        selected=selected,
        total_benefit=total_benefit,
        total_cost=total_cost,
        total_water=total_water,
        strategy="random",
    )


def rank_baseline(cells: list[CellState], cfg: OptimizationConfig, key: str) -> OptimizationResult:
    if key == "max_lst":
        ranked = sorted(cells, key=lambda c: c.lst, reverse=True)
    elif key == "min_canopy":
        ranked = sorted(cells, key=lambda c: c.canopy)
    elif key == "max_population":
        ranked = sorted(cells, key=lambda c: c.population, reverse=True)
    elif key == "greedy_exposure":
        ranked = sorted(cells, key=lambda c: c.exposure, reverse=True)
    else:
        raise ValueError(key)
    selected = []
    remaining = cfg.budget_units
    total_benefit = 0.0
    total_cost = 0.0
    total_water = 0.0
    for cell in ranked:
        if not cell.plantable or not cell.water_feasible:
            continue
        cost = _cost("plant", cfg)
        if cost > remaining:
            break
        selected.append((cell.cell_id, "plant"))
        total_benefit += _benefit(cell, "plant", cfg)
        total_cost += cost
        total_water += _water("plant", cfg)
        remaining -= cost
    return OptimizationResult(
        selected=selected,
        total_benefit=total_benefit,
        total_cost=total_cost,
        total_water=total_water,
        strategy=key,
    )
