# M8 Intervention Simulator Protocol

## Objective

Model counterfactual effects of preserve, restore, and plant actions on population-weighted heat exposure, with configurable cost and water parameters.

## Actions

| Action | Modeled effect |
|---|---|
| `none` | Baseline exposure (no change) |
| `preserve` | Avoid projected canopy loss on mature cells |
| `restore` | Canopy gain with partial immediacy |
| `plant` | New canopy gain with lower immediacy (young trees) |

All outputs are **modeled scenarios**, not observed causal impacts.

## Evaluation design

- Build intervention grid from M7 heat layers (top exposure cells on pilot stack)
- Estimate maturity from canopy time series stability + level
- Run full counterfactuals per cell for all actions
- Compare mean exposure reduction and benefit-per-cost by action
- Test H5: preserve median benefit/cost exceeds plant on mature candidate cells

## Run

```bash
python scripts/run_m8_intervention.py
# or: python -m canopy m8
```

## Go to M9

Proceed if:

1. At least 10 preserve-candidate cells exist,
2. Preserve median benefit/cost exceeds plant on mature cells, and
3. Action counterfactuals produce distinct mean exposure reductions

Gates are configurable in `configs/m8_intervention.yaml`.
