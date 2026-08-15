# M9 Optimization Protocol

## Objective

Compare CANOPY constrained optimization (preserve + restore + plant) against heuristic baselines under fixed budget and water constraints, using M8 intervention counterfactual benefits.

## Strategies

- `random` — random feasible planting
- `max_lst` — plant in hottest cells
- `min_canopy` — plant in lowest-canopy cells
- `max_population` — plant in highest-population cells
- `greedy_exposure` — plant in highest exposure cells
- `canopy_plant_only` — greedy optimizer restricted to planting
- `canopy_optimizer` — full preserve/restore/plant greedy optimizer

## Evaluation design

- Build intervention grid from M7/M8 layers (stratified sampling)
- Benefits computed via M8 `simulate_action` exposure reductions
- Fixed budget (`budget_units`) and water budget (`water_budget_m3`)
- Metrics: total exposure reduction, benefit per cost, selected-cell overlap (Jaccard)

## Run

```bash
python scripts/run_m9_optimization.py
# or: python -m canopy m9
```

## Go to M10

Proceed if CANOPY optimizer total benefit exceeds the best baseline by at least 5% (configurable via `min_optimizer_gain_fraction`).
