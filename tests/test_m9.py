import pytest

from canopy.intervention.simulator import InterventionCell, InterventionParams, simulate_action
from canopy.optimization.engine import CellState, OptimizationConfig, greedy_optimize
from canopy.optimization.evaluation import (
    compare_strategies,
    make_simulator_benefit_fn,
    selected_cell_jaccard,
    to_cell_states,
)


def _intervention_cell(
    cell_id: int,
    exposure: float,
    *,
    preserve: bool = False,
    plantable: bool = True,
    restorable: bool = False,
) -> InterventionCell:
    return InterventionCell(
        cell_id=cell_id,
        row=cell_id,
        col=0,
        lst=40.0,
        canopy=0.2 if plantable else 0.5,
        population=100.0,
        building_density=0.5,
        maturity=0.7 if preserve else 0.2,
        exposure=exposure,
        water_feasible=True,
        plantable=plantable,
        preserve_candidate=preserve,
        restorable=restorable,
    )


def test_to_cell_states():
    cell = _intervention_cell(1, 500.0, preserve=True)
    states = to_cell_states([cell])
    assert len(states) == 1
    assert states[0].restorable is False
    assert states[0].preserve_candidate is True


def test_simulator_benefit_fn():
    params = InterventionParams()
    cell = _intervention_cell(0, 1000.0, preserve=True)
    benefit_fn = make_simulator_benefit_fn([cell], params)
    state = to_cell_states([cell])[0]
    assert benefit_fn(state, "preserve") > 0
    assert benefit_fn(state, "plant") >= 0


def test_greedy_optimizer_selects_high_benefit_cells():
    params = InterventionParams()
    cells = [
        _intervention_cell(0, 100.0, plantable=True),
        _intervention_cell(1, 5000.0, preserve=True),
        _intervention_cell(2, 3000.0, preserve=True),
    ]
    benefit_fn = make_simulator_benefit_fn(cells, params)
    states = to_cell_states(cells)
    cfg = OptimizationConfig(budget_units=10, water_budget_m3=1000.0)
    result = greedy_optimize(states, cfg, benefit_fn=benefit_fn)
    assert result.total_benefit > 0
    assert len(result.selected) >= 1


def test_selected_cell_jaccard():
    from canopy.optimization.engine import OptimizationResult

    a = OptimizationResult(selected=[(1, "plant"), (2, "preserve")], total_benefit=1, total_cost=1, total_water=1, strategy="a")
    b = OptimizationResult(selected=[(2, "preserve"), (3, "plant")], total_benefit=1, total_cost=1, total_water=1, strategy="b")
    assert selected_cell_jaccard(a, b) == pytest.approx(1 / 3)


def test_compare_strategies():
    params = InterventionParams()
    cells = [
        _intervention_cell(i, float(500 + i * 200), preserve=(i % 5 == 0), plantable=True, restorable=(i % 7 == 0))
        for i in range(30)
    ]
    cfg = {
        "project": {"seed": 0},
        "optimization": {
            "budget_units": 50,
            "water_budget_m3": 5000,
            "strategies": ["random", "greedy_exposure", "canopy_optimizer"],
        },
    }
    out = compare_strategies(cells, params, cfg)
    assert "canopy_optimizer" in out["strategies"]
    assert out["baseline_total_exposure"] > 0
