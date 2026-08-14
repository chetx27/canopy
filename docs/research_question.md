# CANOPY Research Questions and Hypotheses

## Primary research question (recommended)

> Can a reproducible temporal geospatial pipeline—combining persistence-aware vegetation anomaly detection, short-horizon loss forecasting, population-weighted heat-exposure modeling, and constrained preserve/plant optimization—detect emerging urban vegetation degradation earlier than conventional baselines and produce intervention priorities that are more beneficial, more equity-sensitive, and more stable under uncertainty than standard heuristic strategies, in Bengaluru?

This question is structured to **fail**. Any sub-component may not outperform baselines.

## Secondary research questions

| ID | Question | Data dependency |
|---|---|---|
| RQ1 | Can temporal models distinguish abnormal decline from seasonal variation? | 18+ months clear observations; annotated seasonal cases |
| RQ2 | Does temporal information improve early detection vs single-date imagery? | Same as RQ1 |
| RQ3 | How early can persistent decline be detected vs threshold/CCDC/DIST-ALERT? | Tier-1 confirmation dates |
| RQ4 | Which EO features contribute most to early detection? | Multi-sensor stack |
| RQ5 | Can vegetation trajectories forecast future canopy loss? | Dense time series |
| RQ6 | Can loss forecasts translate to localized heat-exposure risk? | LST + population layers |
| RQ7 | Does human-weighted exposure change intervention locations vs temperature-only? | Population / vulnerability proxy |
| RQ8 | Does constrained optimization beat heuristic placement under fixed budget? | Intervention simulator |
| RQ9 | How sensitive are optimal locations to input uncertainty? | Perturbation experiments |
| RQ10 | Does optimization favor data-rich areas? | Data quality mask |
| RQ11 | Robustness to missing/cloudy/noisy observations? | Stress tests |
| RQ12 | When does the system recommend preservation over planting? | Maturity + benefit functions |
| RQ13 | Generalization to a second Indian city? | External city labels (late phase) |

## Hypotheses (to test, not assume)

| ID | Hypothesis | Falsified if |
|---|---|---|
| H1 | Temporal models outperform single-date models for persistent change detection | No significant improvement in persistent F1 or detection delay |
| H2 | Multi-source features beat NDVI-only | Ablation shows ≤1 pt F1 gain |
| H3 | Human-weighted exposure shifts priorities vs temperature-only | Top-k Jaccard overlap >0.9 |
| H4 | Constrained optimizer beats random/heat/vegetation/population heuristics | ≤5% exposure reduction difference |
| H5 | Preservation sometimes beats equivalent new planting per resource unit | Planting always dominates in all budget scenarios |
| H6 | Uncertainty materially changes intervention rankings | Rankings identical under wide intervals |

## Spatial experimental units

- **Training region:** Non-adjacent BBMP ward cluster (TBD after AOI polygon).
- **Validation region:** Separate ward cluster for threshold/weight tuning.
- **Test region:** Held-out spatial blocks, no adjacency to training.
- **External city:** Deferred until Bengaluru MVRE completes.

Random pixel splits are **not** independent generalization tests.

## Contribution formulations under evaluation

See `docs/research_discovery.md` Section 6:

- **A (recommended):** Integrated decision-centric evaluation
- **B:** Urban early-warning beyond operational alerts
- **C:** Preservation-aware optimization under uncertainty

Final selection after MVRE (Section 17 of research discovery).
