import numpy as np
import pytest

from canopy.intervention.grid import build_intervention_grid, estimate_maturity, load_heat_surfaces_for_intervention
from canopy.intervention.simulator import (
    InterventionCell,
    InterventionParams,
    aggregate_action_outcomes,
    counterfactual_all_actions,
    simulate_action,
)


def _cell(**kwargs) -> InterventionCell:
    defaults = dict(
        cell_id=0,
        row=0,
        col=0,
        lst=38.0,
        canopy=0.5,
        population=120.0,
        building_density=0.4,
        maturity=0.7,
        exposure=800.0,
        water_feasible=True,
        plantable=False,
        preserve_candidate=True,
        restorable=False,
    )
    defaults.update(kwargs)
    return InterventionCell(**defaults)


def test_estimate_maturity_stable_series():
    series = np.full(12, 0.65)
    maturity = estimate_maturity(series, 0.65)
    assert maturity > 0.5


def test_preserve_feasible_on_mature_cell():
    outcome = simulate_action(_cell(), "preserve")
    assert outcome.feasible
    assert outcome.exposure_reduction > 0
    assert outcome.benefit_per_cost > 0


def test_plant_infeasible_when_canopy_high():
    outcome = simulate_action(_cell(canopy=0.7, plantable=False), "plant")
    assert not outcome.feasible
    assert outcome.exposure_reduction == 0.0


def test_plant_feasible_on_low_canopy():
    outcome = simulate_action(
        _cell(canopy=0.2, plantable=True, preserve_candidate=False, maturity=0.2),
        "plant",
    )
    assert outcome.feasible
    assert outcome.exposure_reduction > 0


def test_preserve_beats_plant_benefit_per_cost():
    params = InterventionParams()
    preserve = simulate_action(_cell(exposure=1000.0), "preserve", params)
    plant = simulate_action(
        _cell(canopy=0.2, plantable=True, preserve_candidate=False, exposure=1000.0),
        "plant",
        params,
    )
    assert preserve.benefit_per_cost > plant.benefit_per_cost


def test_counterfactual_all_actions():
    cf = counterfactual_all_actions(_cell())
    assert set(cf) == {"none", "preserve", "restore", "plant"}
    assert cf["none"].exposure_reduction == 0.0


def test_aggregate_action_outcomes():
    outcomes = [
        simulate_action(_cell(), "preserve"),
        simulate_action(_cell(canopy=0.2, plantable=True, preserve_candidate=False), "plant"),
    ]
    agg = aggregate_action_outcomes(outcomes)
    assert agg["n_feasible"] == 2
    assert agg["mean_exposure_reduction"] > 0


def test_build_intervention_grid():
    rng = np.random.default_rng(0)
    rows, cols = 20, 20
    cube = rng.uniform(0.2, 0.7, size=(10, rows, cols))
    canopy = np.nanmean(cube, axis=0)
    lst = 30 + 10 * (1 - canopy)
    population = rng.uniform(20, 200, size=(rows, cols))
    building = np.clip(1 - canopy, 0, 1)
    exposure = np.maximum(lst - 24, 0) * population
    cfg = {"intervention": {"max_eval_cells": 50, "min_exposure": 0.0}, "heat": {}}
    cells = build_intervention_grid(
        cube, canopy, lst, population, building, exposure, cfg, seed=0
    )
    assert 0 < len(cells) <= 50
    assert all(c.exposure >= 0 for c in cells)


def test_load_heat_surfaces_for_intervention():
    canopy = np.full((5, 5), 0.4)
    lst = np.full((5, 5), 36.0)
    population = np.full((5, 5), 100.0)
    building = np.full((5, 5), 0.5)
    surface = load_heat_surfaces_for_intervention(canopy, lst, population, building, {"heat": {}})
    assert surface.shape == (5, 5)
    assert np.all(surface >= 0)
