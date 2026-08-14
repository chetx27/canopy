# CANOPY Research Discovery Phase

**Status:** Milestone 1 deliverable. No implementation, training, or frontend work has begun.

**Working title:** CANOPY: Temporal Geospatial AI for Early Urban Vegetation-Loss Detection, Climate-Risk Forecasting, and Intervention Optimization

**Primary case study:** Bengaluru, Karnataka, India (initial experimental environment; not assumed representative of all cities)

---

## 1. Precise Problem Formulation

### 1.1 Decision context

Urban vegetation in rapidly growing cities is spatially heterogeneous, seasonally dynamic, and increasingly stressed by land-use conversion, infrastructure expansion, drought, and heat. Municipal agencies and researchers can often map where vegetation exists or where it has already disappeared, but they lack integrated, evidence-based tools that answer the downstream decision questions:

- Is a detected vegetation signal **abnormal** relative to expected seasonal behavior?
- Is decline **persistent** rather than reversible phenological variation?
- If the trend continues, **where** and **when** is further loss likely?
- How might that loss affect **population-weighted heat exposure**, not just land-surface temperature?
- Under a fixed budget and environmental constraints, should resources go to **preservation**, **restoration**, or **new planting**?
- How **uncertain** are these recommendations, and do they remain stable under data perturbations?

### 1.2 Formal problem statement

Given a study region \(R\) partitioned into spatial units \(i \in \{1,\ldots,N\}\) (e.g., 30 m or 100 m grid cells), and a sequence of Earth-observation and auxiliary observations \(\{X_i(t)\}_{t=1}^{T}\), CANOPY investigates whether a closed-loop framework can:

1. **Detect** emerging persistent vegetation degradation earlier than conventional threshold-based change detectors, while controlling false alarms from monsoon seasonality and cloud gaps.
2. **Forecast** short-horizon vegetation trajectories with calibrated uncertainty.
3. **Estimate** localized human heat exposure as a function of vegetation, urban morphology, meteorology, and population distribution.
4. **Optimize** geographically targeted interventions (preserve / restore / plant / none) under budget, water, spacing, and land-availability constraints.
5. **Evaluate** whether this integrated pipeline produces measurably different and more beneficial intervention priorities than established heuristics, and whether those priorities are robust to uncertainty.

This is a **hypothesis-testing** problem. A negative result (e.g., temporal models do not beat simple baselines, or optimization is unstable) is scientifically valid and must be reported.

### 1.3 Scope boundaries

CANOPY explicitly does **not** claim to:

- Replace operational global alert systems (DIST-ALERT, GLAD, RADD, Hansen GFC).
- Predict individual health outcomes.
- Make autonomous governmental decisions.
- Prove causality between a single tree and measured air temperature without independent validation.

CANOPY operates at the **population / grid-cell / decision-support** level using publicly reproducible data and explicit uncertainty.

### 1.4 Distinction from existing fragmented workflows

| Existing focus | Typical output | Missing link CANOPY investigates |
|---|---|---|
| Vegetation / LULC mapping | Static or annual maps | Persistence-aware early anomaly scoring |
| Deforestation / disturbance alerts | Binary loss alerts | Urban sub-pixel tree loss + forecast + intervention |
| Urban heat mapping | LST / UHI maps | Population-weighted exposure trajectories |
| Tree planting prioritization | Heuristic suitability layers | Closed loop from detected loss to constrained optimization |
| Preservation advocacy | Qualitative policy arguments | Quantified preserve-vs-plant tradeoffs under budget |

---

## 2. Literature Review Strategy

### 2.1 Objectives

Build a structured, citable evidence base before any modeling. For each CANOPY layer, identify established methods, datasets, metrics, limitations, and unresolved questions.

### 2.2 Search domains and query templates

| Domain | Primary databases | Example queries |
|---|---|---|
| Temporal vegetation change | Web of Science, Scopus, IEEE, Remote Sensing of Environment | `CCDC`, `BFAST monitor`, `urban vegetation dynamics`, `seasonal anomaly` |
| Urban tree / canopy mapping | ISPRS, Forests, Urban Forestry | `urban tree cover Sentinel-2`, `Bengaluru tree cover`, `sub-pixel canopy` |
| Early warning / disturbance | Nature Communications, GFW docs, LP DAAC | `DIST-ALERT`, `GLAD-S2`, `near real-time vegetation loss` |
| Urban heat & exposure | Building and Environment, Urban Climate, Commun Earth Environ | `population heat exposure`, `LST downscaling`, `thermal comfort` |
| Intervention optimization | Landscape and Urban Planning, Frontiers in Ecology | `tree planting prioritization`, `P-EHI`, `constrained optimization urban greening` |
| Uncertainty in GeoAI | IJGIS, Annals of GIS | `conformal prediction spatial`, `uncertainty geospatial machine learning` |

### 2.3 Inclusion criteria

- Peer-reviewed journal or major conference paper, or authoritative product documentation (NASA/USGS/ESA/Copernicus).
- Explicit spatial and temporal resolution stated.
- Evaluation metrics reported on independent reference data (not self-generated labels only).
- Published 2009–2026, with emphasis on 2018–2026 for operational alert systems.

### 2.4 Exclusion criteria

- Blog posts, uncited dashboards, and hackathon READMEs as primary evidence.
- Papers without spatial or temporal evaluation.
- Methods evaluated only on synthetic data unless used as methodological reference.

### 2.5 Review workflow

1. **Seed collection** from canonical methods (CCDC, BFAST, Hansen GFC, DIST-ALERT, i-Tree / Nowak urban forestry, Locke Baltimore prioritization).
2. **Forward/backward citation chaining** from seed papers.
3. **Bengaluru-specific search** for local validation context (IISc land-use studies, Nölke 2021 tree cover, SAM land-cover pipeline).
4. **Gap matrix construction** (Section 4 below).
5. **Living table maintenance** in `docs/literature/literature_table.md` with DOI/URL for every entry.

### 2.6 Deliverable cadence

- **Week 1–2:** 25 seed papers + product specs documented.
- **Week 3–4:** 50+ entries with gap annotations.
- **Before Milestone 3 coding:** Every CANOPY component mapped to at least 3 prior approaches.

---

## 3. Existing Systems and Key Papers (by topic)

### 3.1 Satellite vegetation change detection

| Work | Contribution | Relevance |
|---|---|---|
| Zhu et al. (2014) CCDC | Continuous harmonic-model change detection on dense Landsat series | Core classical baseline; handles seasonality |
| Verbesselt et al. (2010) BFAST | Trend/season break detection | Separates phenology from degradation |
| Bullock et al. (2025) DIST-ALERT | Operational 30 m global vegetation-loss alerts (HLS) | Strong operational baseline; detection lag benchmarks |
| Potapov et al. / Hansen GFC | Annual global forest cover loss | Reference product, not early warning |
| Smith et al. (2019) EWMACD comparison | Simulated benchmark of BFAST/CCDC/EWMACD | Guides baseline selection |
| Li et al. (2021) Shenzhen dynamics | Process-oriented urban greenness change | Urban-specific temporal framing |

### 3.2 Urban tree-canopy mapping

| Work | Contribution | Relevance |
|---|---|---|
| Nölke (2021) Bengaluru | Continuous urban tree cover from Landsat; MAE 13.04% | Direct Bengaluru canopy reference |
| Land-cover Bengaluru (SAM4627) | 11-class 10 m OBIA with S1+S2+OSM | Local LULC pipeline; monsoon cloud strategy |
| Lang et al. (2023) ETH canopy height | Global 10 m canopy height from S2+GEDI | Auxiliary structure layer |
| Tree cover mapping reviews (2025) | Sentinel-2 classifiers survey | Feature and accuracy expectations |

### 3.3 Urban heat exposure

| Work | Contribution | Relevance |
|---|---|---|
| Sun et al. (2025) Boston | Downscaled air temperature; vulnerability-weighted exposure; tree vs cool roof optimization | Closest integrated optimization precedent |
| Shahfahad et al. (2025) Bengaluru thermal comfort | LST–NDVI link 1993–2023 | Local heat–vegetation relationship |
| Govind & Ramesh (2020) Bengaluru LST | Concentric-ring LST analysis | Spatial UHI structure |
| Zhao et al. (2024) Hangzhou phenology | Urban forest phenology vs climate | Seasonality modeling reference |

### 3.4 Urban greening / tree-placement optimization

| Work | Contribution | Relevance |
|---|---|---|
| Nowak et al. USDA Baltimore | P-EHI, pollution gradients, spatial planting scenarios | Foundational optimization heuristics |
| Locke et al. (2021) Joliette | Multi-indicator street-tree priority index | Practical municipal baseline |
| Dortmund TPP framework (2025) | Hex-grid composite suitability | Modern GIS overlay baseline |
| Duke Durham model (2023) | Budget-constrained census-tract allocation | Simple constrained baseline |

### 3.5 Deforestation early warning

| Work | Contribution | Relevance |
|---|---|---|
| DIST-ALERT (2025) | Mean lag ~6–20 days depending on event magnitude | Sets realistic early-detection expectations |
| GLAD / RADD / integrated GFW alerts | Multi-sensor alert fusion | Operational comparison point |
| Vargas et al. (2019) Peru Landsat alerts | Tropical early warning | Methodological precedent |

### 3.6 Temporal anomaly detection

| Work | Contribution | Relevance |
|---|---|---|
| BFAST Monitor | Near-real-time abnormal deviation detection | Strong seasonal baseline |
| COLD / NRT-CCDC / S-CCD | Recursive state-space NRT variants | Alternative NRT baselines |
| Universal NRT framework (2025) | Survey of parametric NRT methods | Method selection guide |

### 3.7 Urban climate intervention modeling

| Work | Contribution | Relevance |
|---|---|---|
| Chen et al. (2024) tree cooling efficacy | Morphology- and climate-dependent cooling | Context-dependent benefit functions |
| Nature Comm. (2026) urban forestry hurdles | Maturity and protection critical for cooling | Supports preserve-vs-plant hypothesis |
| Roloff et al. (2021) urban tree stock model | Age-structure ecosystem services | Parameter source for preservation modeling |

### 3.8 Uncertainty-aware geospatial AI

| Work | Contribution | Relevance |
|---|---|---|
| Lou et al. (2025) GeoCP | Spatially weighted conformal prediction intervals | Decision uncertainty layer |
| GeoSIMCP / geoconformal package | Feature-aware spatial conformal | Heterogeneous urban landscapes |

Full structured table: `docs/literature/literature_table.md`

---

## 4. Comparison Table: What Existing Approaches Already Do

| Capability | CCDC / BFAST / DIST-ALERT | Urban canopy mapping (e.g., Nölke 2021) | UHI / LST studies (Bengaluru) | Tree planting prioritization (Nowak, Locke, Sun 2025) | **Gap for CANOPY** |
|---|---|---|---|---|---|
| Multi-temporal vegetation monitoring | Yes | Partial (annual snapshots) | Indirect via NDVI | No | Urban **persistent anomaly** scoring with seasonality |
| Early loss detection | Yes (global, 30 m) | No | No | No | **Urban sub-pixel** loss at actionable scale |
| Distinction seasonal vs persistent | Partial (method-dependent) | No | Limited | No | Explicit **persistence-aware** evaluation |
| Short-horizon vegetation forecast | Rare | Some LULC forecasting projects | No | No | Forecast linked to **intervention timing** |
| Heat exposure (population-weighted) | No | No | Mostly LST / comfort indices | Yes (recent Boston work) | Couple forecasted **loss trajectories** to exposure |
| Constrained optimization | No | No | No | Yes ( planting only in most work) | **Preserve + restore + plant** under water budget |
| Uncertainty in decisions | Limited in alerts | Rare | Rare | Emerging (Sun 2025 deterministic scenarios) | **Ranking stability** under uncertainty |
| Bengaluru-specific validation | No | Yes (partial AOI) | Yes | No | Integrated Bengaluru **closed-loop** evaluation |
| Equity / fairness analysis | No | No | No | Partial | Explicit **equity sensitivity** |

**Honest assessment:** No single cited work performs the full OBSERVE → DETECT → FORECAST → IMPACT → OPTIMIZE loop with uncertainty-aware evaluation in Bengaluru. However, **each component is well studied**. CANOPY's defensible contribution must be framed as **integrated experimental evaluation**, not invention of remote sensing.

---

## 5. Genuine Gaps and Weaknesses in Existing Approaches

1. **Urban sub-pixel vegetation loss:** Operational alerts (30 m) and Landsat canopy products under-detect scattered urban trees (Nölke 2021; SAM4627 monsoon gaps).
2. **Seasonality in monsoon cities:** Many change detectors validated in temperate or forest contexts; Bengaluru has strong cloud contamination and irrigation-driven greenness reversals.
3. **Detection-to-decision disconnect:** DIST-ALERT and GFW stop at alerts; they do not forecast localized human consequences or optimize interventions.
4. **Planting-only optimization:** Most municipal tools prioritize new planting, under-modeling **preservation of mature canopy** despite strong ecological evidence (Roloff 2021; Nature Comm. 2026).
5. **LST ≠ human exposure:** Bengaluru literature often reports LST trends without consistent population weighting or air-temperature validation.
6. **Weak ground truth for urban tree removal:** Few public, georeferenced, time-stamped removal datasets exist at city scale.
7. **Optimization stability rarely tested:** Heuristic rankings seldom undergo perturbation / ranking-stability analysis.
8. **Spatial leakage in ML studies:** Random pixel splits inflate performance in geospatial settings.
9. **End-to-end uncertainty:** Alert confidence exists operationally, but intervention **decision uncertainty** is rarely quantified.
10. **Equity blind spots:** High-data neighborhoods may dominate recommendations.

---

## 6. Three Possible Formulations of CANOPY's Research Contribution

### Formulation A: Integrated decision-centric evaluation (recommended)

**Claim:** Rigorous experimental evaluation of whether coupling persistence-aware temporal vegetation anomaly detection, short-horizon forecasting, population-weighted heat exposure estimation, and constrained preserve/plant optimization produces **measurably different and more beneficial** intervention priorities than strong baselines—under explicit uncertainty and equity analysis—in Bengaluru.

**Strength:** Defensible if experiments are clean. Does not over-claim algorithmic novelty.
**Risk:** Reviewers may say "engineering integration." Mitigation: strong ablations, failure reporting, and open benchmark protocol.

### Formulation B: Urban early-warning beyond operational alerts

**Claim:** Specialized temporal models tuned for **urban scattered-canopy loss** detect persistent degradation earlier or with fewer false positives than DIST-ALERT / NDVI-threshold / BFAST Monitor in Bengaluru, using independent reference data.

**Strength:** Sharp, testable hypothesis (H1, RQ3).
**Risk:** DIST-ALERT is a moving target; urban reference labels are scarce; gains may be marginal.

### Formulation C: Preservation-aware optimization under uncertainty

**Claim:** Under fixed budget and water constraints, joint optimization over **preserve / restore / plant** actions yields higher expected population-weighted heat-exposure reduction than planting-only heuristics, and mature-tree preservation dominates in identifiable spatial regimes.

**Strength:** Policy-relevant; connects to H4, H5, RQ12.
**Risk:** Benefit functions depend on literature-derived parameters; must be transparent and sensitivity-tested.

---

## 7. Recommended Final Research Question

> **Primary RQ (recommended):**
> In Bengaluru, can a reproducible temporal geospatial pipeline—combining persistence-aware vegetation anomaly detection, short-horizon loss forecasting, population-weighted heat-exposure modeling, and constrained preserve/plant optimization—detect emerging urban vegetation degradation earlier than conventional baselines **and** produce intervention priorities that are more beneficial, more equity-sensitive, and more stable under uncertainty than standard heuristic strategies?

**Operational sub-questions** map directly to RQ1–RQ13 in the project specification. Hypotheses H1–H6 remain falsifiable.

**Why this formulation:** It anchors contribution in **measurable system-level evaluation** rather than unsupported novelty claims, while keeping room for negative results on any sub-component.

---

## 8. Recommended Datasets for Bengaluru

| Dataset | Provider | Resolution | Temporal | Role in CANOPY | License / access |
|---|---|---|---|---|---|
| Sentinel-2 L2A (S2_SR_HARMONIZED) | Copernicus / GEE | 10–20 m | 5-day revisit (combined) | Primary optical time series, indices | Free; GEE registration |
| Sentinel-1 GRD (VH/VV) | Copernicus / GEE | 10 m | 6–12 day | Monsoon-gap gap-filling, structure | Free; GEE |
| HLS (L30 + S30) | NASA LP DAAC / GEE | 30 m | 1–4 day | DIST-ALERT-compatible baseline | Free |
| Landsat 5/7/8/9 C2 L2 | USGS / GEE | 30 m | 16-day | Long historical context (pre-2015) | Free |
| ERA5-Land hourly | ECMWF / GEE | ~9 km | Hourly | Meteorology, water-stress proxies | Free for research |
| WorldPop 100 m | WorldPop / GEE | 100 m | 2015–2030 annual | Exposure weighting | Open |
| GHSL built-up / SMOD | EC JRC | 10–100 m | Multi-date | Morphology, urban gradient | Free |
| Microsoft Building Footprints | Microsoft | Vector | Snapshot | Building density proxy | Open (check terms) |
| OSM (roads, land use, water) | OpenStreetMap | Vector | Continuous | Constraints, irrigation proxies | ODbL |
| Copernicus DEM / CartoSat DEM | ESA / ISRO | 30 m | Static | Terrain | Free |
| Dynamic World / ESA WorldCover | Google / ESA | 10 m | Near-real-time / annual | Weak LULC prior (not ground truth) | Free |
| MODIS LST (MOD11A1) | NASA | 1 km | Daily | Coarse LST validation | Free |
| Landsat LST (st_*) | USGS | 30 m | 16-day | Primary LST target candidate | Free |
| ETH Canopy Height 2020 | ETH / GEE | 10 m | 2020 | Maturity proxy | Free |
| Global Tree Canopy Cover v4 | Hansen/UMD | 30 m | 2000–2022 | Baseline canopy reference | Free |
| DIST-ALERT (OPERA) | NASA OPERAS | 30 m | Near-real-time | External alert baseline | Free |
| IMD station observations | India Met Dept | Point | Daily/hourly | Air temp validation (limited stations) | Restricted; partial open |
| BBMP / Karnataka open data | Municipal | Vector | Varies | Permits, lakes, wards (if available) | Varies |
| OpenAQ | OpenAQ | Point | Hourly | Optional air-quality covariate | Open |

Detailed inventory: `docs/dataset_card.md`

---

## 9. Data Availability Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Monsoon cloud gaps (Jun–Oct) | **High** | S1 SAR fusion; multi-sensor HLS; gap-aware metrics; don't impute without flags |
| Sub-pixel urban trees invisible at 10–30 m | **High** | Aggregate to 100 m for primary experiments; use Nölke-style validation subset with high-res reference |
| No public georeferenced tree-removal ledger | **High** | Multi-source weak + strong labels (see Section 10) |
| LST ≠ air temperature | **Medium** | Treat LST as primary target; downscale with literature-informed model; validate at IMD stations |
| WorldPop disaggregation uncertainty | **Medium** | Sensitivity analysis; ward-level census where available |
| ERA5-Land 9 km smoothing | **Medium** | Use as meteorological covariate, not microclimate truth |
| OSM incompleteness in fringe areas | **Medium** | Cross-check GHSL; mark data-quality layer |
| GEE export quotas / compute limits | **Medium** | Tile-based pipeline; pilot AOI before full metro |
| Licensing for high-res truth imagery | **Medium** | Planet/NRSCC only if licensed; otherwise manual annotation on public basemap samples |
| Temporal misalignment across sensors | **Low–Med** | Strict date metadata; harmonized grid |
| Over-reliance on Dynamic World as labels | **High** | Never treat as ground truth |

---

## 10. Ground-Truth Strategy

CANOPY requires **independent** labels. Proposed hierarchy:

### Tier 1: Strong reference (preferred for test set)

- **Manual interpretation** of high-resolution time series (Maxar/Google Earth Pro historical imagery where permitted, or licensed PlanetScope) for a stratified sample of several hundred 30 m cells.
- **Documented change polygons** from peer-reviewed Bengaluru LULC studies if authors provide supplementary geometries.
- **DIST-ALERT / Hansen confirmation events** used only as **reference timing** for large-magnitude loss, not as training labels (avoid circular evaluation).

### Tier 2: Medium reference

- **OpenStreetMap** land-use and land-cover change history (building additions, forest/water edits) with timestamp filtering.
- **11-class SAM Bengaluru land-cover** reprocessed for specific years if training data downloadable.

### Tier 3: Weak / pseudo labels (never called ground truth)

- NDVI-drop thresholds.
- Dynamic World class transitions.
- Model-generated alerts.

### Annotation protocol (pilot)

1. Define event types: `{tree removal, construction clearing, seasonal dip, irrigation green-up, cloud artifact}`.
2. Stratified sampling: urban core, peri-urban, green belt, water-adjacent.
3. Two independent annotators on 100 cells; compute Cohen's kappa.
4. Hold out **spatial blocks** (see experiments) for test.

### Spatial split design (leakage prevention)

- **Training region:** North/East BBMP wards (example; finalize after AOI polygon).
- **Validation region:** Non-adjacent ward cluster for threshold tuning.
- **Test region:** Spatially separated ward cluster.
- **External city (later):** Hyderabad or Pune after Bengaluru pipeline validated.

---

## 11. Proposed Baselines

### Detection

| ID | Method | Rationale |
|---|---|---|
| A | Single-date NDVI threshold | Simplest remote-sensing baseline |
| B | Bi-temporal NDVI delta | Common practice |
| C | BFAST Monitor | Seasonal NRT standard |
| D | CCDC / COLD-style harmonic residual | Strong classical temporal |
| E | DIST-ALERT product | Operational benchmark |
| F | Gradient-boosted temporal features | ML baseline without deep learning |
| G | Temporal CNN / Transformer | Proposed learned detector (only if F insufficient) |

### Forecasting

- Persistence (last value)
- Seasonal naive (same month prior year)
- Linear trend on deseasonalized series
- Random Forest on lag features
- Probabilistic GBM with quantile output

### Heat exposure

- Raw LST
- LST × population density
- Downscaled air-temperature regression (Sun 2025-style simplified)
- Morphology-adjusted exposure index

### Optimization

1. Random feasible placement
2. Highest LST cells
3. Lowest canopy cells
4. Highest population cells
5. Highest vulnerability proxy (if data available)
6. Greedy marginal heat-exposure reduction
7. **CANOPY optimizer** (preserve + plant + restore)
8. Planting-only variant of CANOPY (ablation)

---

## 12. Proposed Experiments

### Phase 0: Data validation (Weeks 1–4)

- Download pilot AOI (≈25 km²): cloud statistics, revisit gaps, CRS alignment checks.
- Compute QC report: missingness by month, sensor availability.

### Phase 1: Detection (Weeks 5–10)

- Exp-D1: Seasonal vs persistent discrimination on annotated sample.
- Exp-D2: Detection delay vs Baselines A–E relative to Tier-1 confirmation date.
- Exp-D3: Ablation of S1, red-edge, texture, morphology features.
- Exp-D4: Spatial block cross-validation.

### Phase 2: Forecasting (Weeks 8–12)

- Exp-F1: 1/3/6-month horizon MAE/RMSE by land-use stratum.
- Exp-F2: Prediction interval calibration (coverage vs nominal).

### Phase 3: Heat exposure (Weeks 10–14)

- Exp-H1: Compare exposure formulations; spatial correlation with held-out LST.
- Exp-H2: Sensitivity to population layer choice.

### Phase 4: Optimization (Weeks 12–18)

- Exp-O1: Fixed budget (e.g., 1k / 5k / 10k intervention units) across baselines 1–7.
- Exp-O2: Preserve-vs-plant counterfactuals.
- Exp-O3: Weight sensitivity and Pareto frontier (heat vs water vs equity).
- Exp-O4: Ranking stability under 20% perturbation of heat and canopy inputs.

### Phase 5: Robustness & fairness (Weeks 16–22)

- Exp-R1: Drop 10/30/50% observations.
- Exp-R2: Inject cloud-contaminated and noisy observations.
- Exp-R3: Benefit distribution across income / ward proxies.

### Phase 6: External validation (Month 9–12, optional)

- Exp-X1: Train Bengaluru → test Hyderabad (zero-shot).
- Exp-X2: Few-shot fine-tune with limited labels.

Every experiment receives a config ID, seed, and registry entry before execution.

---

## 13. Proposed Evaluation Metrics

| Task | Primary metrics | Secondary metrics |
|---|---|---|
| Detection | Detection delay (days/months), F1, precision/recall, FPR | IoU (if polygon labels), persistence accuracy |
| Seasonality | Confusion seasonal vs persistent | Month-stratified F1 |
| Forecasting | MAE, RMSE, CRPS | Prediction interval coverage, sharpness |
| Heat model | RMSE, spatial Pearson r, MAE | Calibration plot vs IMD stations |
| Exposure | Population-weighted exceedance hours | Vulnerability-weighted index |
| Optimization | Total expected exposure reduction, benefit per cost/water | Equity Gini on benefits, spatial coverage |
| Uncertainty | Coverage error, ranking Kendall τ under perturbation | Decision regret between strategies |
| Fairness | Benefit share by socioeconomic quintile proxy | Minimum-benefit constraint satisfaction |

**Never report accuracy alone.** Always report confidence intervals via spatial block bootstrap where appropriate.

---

## 14. Potential Threats to Validity

### Internal validity

- **Label noise** in weak references inflates or deflates detection metrics.
- **Co-registration error** between 10 m, 30 m, 100 m layers.
- **Hyperparameter tuning on test regions** if splits are not enforced.
- **Future data leakage** in temporal feature construction.

### External validity

- Bengaluru-specific irrigation, monsoon, and IT-corridor development patterns may not transfer.
- Results at 100 m may not hold at tree-crown scale.

### Construct validity

- NDVI decline may reflect senescence, species change, or mowing—not loss.
- LST-based exposure is a proxy for human thermal stress.
- Preservation benefit parameters from temperate literature may misapply.

### Conclusion validity

- Single train/test split insufficient; need multi-block and temporal splits.
- Multiple comparisons require careful reporting (not p-hacking across thresholds).

---

## 15. Potential Novelty Risks

| Risk | Description | Mitigation |
|---|---|---|
| **Integration fallacy** | "We combined known parts" without new empirical insight | Pre-register hypotheses; report ablations and failures |
| **Operational redundancy** | DIST-ALERT already detects loss quickly | Position CANOPY as **urban decision loop**, compare honestly on urban scattered loss |
| **Heuristic optimization parity** | Greedy heat-only may match optimizer | Report equivalence if true; analyze stability differences |
| **Parameter-driven preservation results** | Preserve wins if maturity bonus tuned too high | Literature-sourced ranges + sensitivity |
| **Overclaiming early detection** | Cloud gaps dominate true delay | Report clear-sky vs all-observation delays separately |
| **Pseudo-novelty** | Reframing i-Tree / Nowak without new evaluation | Explicit baseline reproduction under identical constraints |

**What CANOPY can defensibly claim if experiments succeed:**

- A reproducible **benchmark protocol** for closed-loop urban vegetation intervention research in monsoon megacities.
- Empirical evidence on whether **temporal persistence modeling** improves urban degradation detection beyond operational and classical baselines in Bengaluru.
- Quantified **preserve-vs-plant** tradeoffs under budget and water constraints with uncertainty-aware ranking.

**What CANOPY should not claim even if experiments succeed:**

- Inventing satellite change detection.
- Real-time municipal deployment readiness without validation.
- Causal health impact estimates.

---

## 16. Six-to-Twelve-Month Research Roadmap

| Month | Milestone | Deliverable |
|---|---|---|
| 1 | M1: Literature + formulation | This document, literature table, frozen primary RQ |
| 2 | M2: Data inventory + pilot AOI | QC report, preprocessing spec, 25 km² aligned stack |
| 3 | M3: Baseline detection | Reproducible Baselines A–E evaluation notebook/script |
| 4 | M4: Temporal anomaly model | Learned detector + spatial CV results |
| 5 | M5: Ground-truth expansion | 500+ annotated cells, inter-rater agreement |
| 6 | M6: Forecasting + uncertainty | Horizon evaluation with calibrated intervals |
| 7 | M7: Heat exposure model | Exposure surfaces + station validation |
| 8 | M8: Intervention simulator | Preserve/plant/restore effect module with sourced parameters |
| 9 | M9: Optimizer + baselines | Constrained optimization vs heuristics |
| 10 | M10: Ablation + robustness | Full experiment suite, ranking stability |
| 11 | M11: Research interface | Map-based inspection tool (research, not demo UI) |
| 12 | M12: Paper + reproducibility | Manuscript draft, CITATION.cff, experiment registry |

---

## 17. Recommended Minimum Viable Research Experiment (MVRE)

**Goal:** Answer a narrow, falsifiable question with minimal compute before building the full system.

**MVRE title:** Persistence-aware NDVI anomaly detection vs operational baseline for scattered urban canopy loss in a 25 km² Bengaluru pilot.

**AOI:** One spatially contiguous BBMP sub-region (~25 km²) with mixed built-up and remnant vegetation (e.g., northern metro transect used in Nölke 2021).

**Data (18 months):** Sentinel-2 L2A + Sentinel-1 VH/VV composites at 30 m monthly; DIST-ALERT alerts for same period.

**Labels:** 150 manually interpreted cells (50 persistent loss, 50 seasonal, 50 stable) from high-resolution historical imagery.

**Methods compared:**

1. Single-date NDVI threshold (Baseline A)
2. BFAST Monitor residual (Baseline C)
3. DIST-ALERT alerts (Baseline E)
4. CANOPY candidate: seasonal harmonic model + persistence filter (2+ anomalous months)

**Primary metric:** Detection delay relative to manual confirmation date, and persistent-vs-seasonal F1.

**Success criterion (proceed):** Candidate improves persistent F1 by ≥5 absolute points OR reduces median detection delay by ≥30 days vs A and B, without FPR >2× Baseline C.

**Failure criterion (still publishable):** No improvement → report that operational/classical methods suffice at 30 m in this AOI; pivot contribution to optimization-only (Formulation C) or expand AOI/labels.

**Compute budget:** GEE exports + local Python on laptop; no GPU required.

**Timeline:** 4–6 weeks.

**Outputs:** `results/mvre/detection_pilot.json`, QC figures, decision memo on whether to invest in deep temporal models.

---

## Decision Gate: Proceed to Implementation?

**Do not begin full repository implementation until:**

1. GEE access confirmed and pilot AOI exported.
2. MVRE annotation protocol pilot completed (≥100 cells, κ computed).
3. Primary RQ and Formulation A/B/C selection approved by research lead.
4. Literature table contains ≥40 entries covering all eight topic areas.

---

## References (seed set)

- Zhu, Z., et al. (2014). Continuous change detection and classification of land cover using all available Landsat data. *Remote Sensing of Environment*.
- Verbesselt, J., et al. (2010). Detecting trend and seasonal changes in satellite image time series. *Remote Sensing of Environment*.
- Bullock, E., et al. (2025). Rapid monitoring of global land change. *Nature Communications*. https://doi.org/10.1038/s41467-025-64014-9
- Nölke, N. (2021). Continuous Urban Tree Cover Mapping from Landsat Imagery in Bengaluru, India. *Forests*. https://doi.org/10.3390/f12020220
- Li, W., et al. (2021). Quantifying Urban Vegetation Dynamics from a Process Perspective. *Remote Sensing*.
- Nowak, D., et al. USDA Baltimore tree planting tradeoff methodology.
- Sun, T., et al. (2025). Integrated tree canopy expansion and cool roofs can optimize air temperature and heat exposure reductions in Boston. *Communications Earth & Environment*.
- Lou, X., et al. (2025). GeoConformal Prediction. *International Journal of Geographical Information Science*.
- Land cover mapping Bengaluru (SAM4627). https://doi.org/10.18494/sam4627

See `docs/literature/literature_table.md` for the full living bibliography.
