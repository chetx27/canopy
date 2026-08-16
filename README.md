CANOPY

Temporal Geospatial AI for Urban Vegetation-Loss Detection, Climate-Risk Forecasting, and Intervention Optimization

""Python" (https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)" (https://www.python.org/)
""License" (https://img.shields.io/badge/License-MIT-green.svg)" (LICENSE)
""Research Status" (https://img.shields.io/badge/Research-Active-orange.svg)"
""Domain" (https://img.shields.io/badge/Domain-Geospatial%20AI-2f6f8f.svg)"
""Remote Sensing" (https://img.shields.io/badge/Remote%20Sensing-Satellite%20%2B%20Temporal%20Analysis-4c8bf5.svg)"

«CANOPY is an end-to-end geospatial intelligence framework for detecting abnormal urban vegetation loss, forecasting future vegetation and heat-exposure risk, quantifying intervention impact, and optimizing where limited urban-greening resources should be deployed.»

CANOPY is designed as a research system rather than a single predictive model.

The central research question is:

«Given where vegetation is changing, how quickly it is changing, what future risk may emerge, who is exposed to that risk, and what interventions are operationally feasible, where should a city act first?»

The system connects remote sensing, temporal modeling, geospatial analysis, uncertainty quantification, climate-risk assessment, and constrained spatial optimization into a single reproducible pipeline.

The initial study area is Bengaluru, India, with the architecture designed to support future transfer to other cities.

---

Table of Contents

- "Research Motivation" (#research-motivation)
- "Problem Definition" (#problem-definition)
- "What CANOPY Does" (#what-canopy-does)
- "Research Hypothesis" (#research-hypothesis)
- "System Overview" (#system-overview)
- "End-to-End Pipeline" (#end-to-end-pipeline)
- "Architecture" (#architecture)
- "Core Research Modules" (#core-research-modules)
  - "Data Acquisition and Harmonization" (#1-data-acquisition-and-harmonization)
  - "Spectral Feature Engineering" (#2-spectral-feature-engineering)
  - "Temporal Representation" (#3-temporal-representation)
  - "Vegetation-Loss Detection" (#4-vegetation-loss-detection)
  - "Future Risk Forecasting" (#5-future-risk-forecasting)
  - "Heat Exposure Modeling" (#6-heat-exposure-modeling)
  - "Intervention Modeling" (#7-intervention-modeling)
  - "Spatial Optimization" (#8-spatial-optimization)
  - "Uncertainty Quantification" (#9-uncertainty-quantification)
  - "Evaluation and Experiment Registry" (#10-evaluation-and-experiment-registry)
- "Detection Strategy" (#detection-strategy)
- "Forecasting Strategy" (#forecasting-strategy)
- "Heat and Exposure Model" (#heat-and-exposure-model)
- "Intervention Optimization" (#intervention-optimization)
- "Uncertainty and Reliability" (#uncertainty-and-reliability)
- "Research Methodology" (#research-methodology)
- "Experimental Protocol" (#experimental-protocol)
- "Evaluation Metrics" (#evaluation-metrics)
- "Leakage Prevention" (#leakage-prevention)
- "Spatial Validation" (#spatial-validation)
- "Temporal Validation" (#temporal-validation)
- "Reproducibility" (#reproducibility)
- "Repository Structure" (#repository-structure)
- "Installation" (#installation)
- "Configuration" (#configuration)
- "Running CANOPY" (#running-canopy)
- "Research Experiments" (#research-experiments)
- "Data" (#data)
- "Dataset and Labeling Strategy" (#dataset-and-labeling-strategy)
- "Minimum Viable Research Experiment" (#minimum-viable-research-experiment)
- "Research Outputs" (#research-outputs)
- "Interpretation of Results" (#interpretation-of-results)
- "Limitations" (#limitations)
- "Ethics and Responsible Use" (#ethics-and-responsible-use)
- "Future Research" (#future-research)
- "Citation" (#citation)
- "License" (#license)

---

Research Motivation

Urban vegetation is not static infrastructure.

Trees and other forms of urban vegetation continuously change because of:

- construction,
- road widening,
- land-use conversion,
- drought,
- heat stress,
- disease,
- water availability,
- maintenance practices,
- storm damage,
- development pressure,
- and gradual degradation that may not be immediately visible.

Traditional urban-greening workflows often operate after the visible problem has already emerged.

CANOPY investigates a different approach:

detect change early → understand persistence → estimate future risk → quantify exposure → identify feasible interventions → optimize limited resources.

The objective is not simply to generate another vegetation map.

The objective is to transform remotely sensed observations into an evidence-driven decision-support pipeline.

---

Problem Definition

CANOPY decomposes the broader urban-resilience problem into several linked research problems.

Problem 1 — Detection

Can abnormal vegetation decline be detected earlier and more reliably than simple single-date thresholding?

Problem 2 — Temporal reasoning

Can persistent vegetation degradation be separated from:

- seasonal variation,
- temporary anomalies,
- cloud contamination,
- sensor noise,
- and short-lived disturbances?

Problem 3 — Forecasting

Given an observed vegetation trajectory, can future vegetation loss or risk be estimated across multiple horizons?

Problem 4 — Exposure

How can vegetation loss be translated into a spatial estimate of heat exposure and population impact?

Problem 5 — Intervention

If a city has limited:

- budget,
- planting capacity,
- water,
- land access,
- and operational resources,

which locations should receive priority?

Problem 6 — Uncertainty

How confident should the system be before recommending an intervention?

CANOPY treats these as connected components rather than independent models.

---

What CANOPY Does

At a high level:

Satellite Observations
        |
        v
Quality Control + Harmonization
        |
        v
Spectral / Spatial Features
        |
        v
Temporal Representation
        |
        v
Vegetation-Loss Detection
        |
        v
Future Risk Forecasting
        |
        v
Heat Exposure Estimation
        |
        v
Intervention Simulation
        |
        v
Constrained Spatial Optimization
        |
        v
Uncertainty-Aware Priority Ranking
        |
        v
Decision-Support Outputs

The output is not simply:

«"Plant a tree here."»

Instead, CANOPY attempts to answer:

«Why this location, how urgent is it, what happens if nothing is done, what intervention is feasible, what population may benefit, what does it cost, and how stable is this recommendation under uncertainty?»

---

Research Hypothesis

The primary hypothesis investigated by CANOPY is:

«Temporal and uncertainty-aware geospatial modeling can identify persistent urban vegetation degradation earlier and produce more useful intervention priorities than static vegetation thresholds or purely heuristic spatial ranking.»

This hypothesis is evaluated through explicit baselines, spatial validation, temporal validation, ablation experiments, robustness tests, and intervention comparisons.

CANOPY therefore does not assume that the proposed methodology is automatically superior.

The system is structured so that it can fail scientifically.

Negative results, unstable rankings, poor calibration, and weak transfer performance are valid research outcomes.

---

System Overview

CANOPY is organized as a modular research pipeline.

Stage| Research Question| Output
Data acquisition| What observations are available?| Harmonized observations
Quality control| Which observations are trustworthy?| Clean temporal data
Feature engineering| What vegetation signals are informative?| Spectral/spatial features
Temporal modeling| What constitutes persistent change?| Temporal representations
Detection| Where is abnormal loss occurring?| Alerts / anomaly maps
Forecasting| What may happen next?| Risk trajectories
Heat modeling| What is the potential exposure impact?| Exposure surfaces
Intervention| What actions are feasible?| Candidate interventions
Optimization| Where should resources be allocated?| Priority ranking
Uncertainty| How stable are the predictions?| Confidence / intervals
Evaluation| Does the system actually work?| Metrics and experiment registry

---

End-to-End Pipeline

Stage 1 — Acquire

Potential observation sources include:

- Sentinel-2 multispectral imagery
- Sentinel-1 SAR
- Harmonized Landsat/Sentinel products
- DIST-ALERT / disturbance products
- MODIS-derived information
- land-use and land-cover information
- population datasets
- climate reanalysis
- OpenStreetMap-derived infrastructure
- auxiliary urban datasets

The architecture intentionally separates data acquisition from downstream modeling so that additional sources can be introduced without redesigning the entire system.

---

Stage 2 — Quality Control

Satellite observations are not treated as automatically valid.

The preprocessing stage considers:

- cloud contamination,
- invalid pixels,
- missing observations,
- coordinate reference systems,
- spatial resolution,
- temporal alignment,
- resampling,
- and feature consistency.

The goal is to ensure that a temporal signal represents environmental change rather than preprocessing artifacts.

---

Stage 3 — Feature Engineering

CANOPY can derive vegetation and urban spectral indicators including:

- NDVI
- EVI
- NDWI
- NDBI
- SAVI

These features provide complementary information about:

- vegetation vigor,
- vegetation moisture,
- built-up intensity,
- soil/background effects,
- and urban structure.

The system is designed to support feature ablation so that the contribution of individual feature groups can be measured rather than assumed.

---

Architecture

The repository follows a modular research architecture.

flowchart TB

    A[Satellite + Auxiliary Data]

    A --> B[Data Acquisition]
    B --> C[Quality Control]
    C --> D[CRS Alignment + Resampling]

    D --> E[Spectral Features]
    E --> F[Temporal Representation]

    F --> G[Vegetation Change Detection]

    G --> H[Risk Forecasting]

    H --> I[Heat / Exposure Modeling]

    I --> J[Intervention Simulation]

    J --> K[Constrained Optimization]

    K --> L[Uncertainty Quantification]

    L --> M[Evaluation + Experiment Registry]

    M --> N[Decision-Support Outputs]

The implemented module map is organized around configuration, spectral indices, temporal processing, detection, forecasting, heat exposure, optimization, uncertainty, evaluation, and experiments.

---

Core Research Modules

1. Data Acquisition and Harmonization

The data layer is responsible for turning heterogeneous remote-sensing observations into analysis-ready spatial-temporal representations.

Key operations include:

- data ingestion,
- temporal alignment,
- CRS harmonization,
- spatial resampling,
- quality filtering,
- missing-data handling,
- AOI clipping,
- and feature preparation.

The repository contains Bengaluru AOI definitions and pilot labeling templates under "data/external/".

---

2. Spectral Feature Engineering

CANOPY uses spectral indices as compact representations of vegetation and urban conditions.

NDVI

The Normalized Difference Vegetation Index is:

$$
NDVI = \frac{NIR - Red}{NIR + Red}
$$

NDVI provides a basic vegetation signal and is useful for:

- vegetation monitoring,
- change detection,
- baseline comparison,
- temporal trend analysis.

However, NDVI alone is insufficient for robust urban vegetation monitoring because:

- seasonal variability can mimic decline,
- shadows can affect observations,
- mixed pixels can occur,
- urban surfaces complicate interpretation,
- and isolated observations provide weak evidence of persistence.

CANOPY therefore treats NDVI as one signal within a larger temporal framework.

---

EVI

Enhanced Vegetation Index provides additional sensitivity in dense vegetation and attempts to reduce some atmospheric and background effects.

---

NDWI

NDWI provides a complementary moisture-related signal.

It can help distinguish vegetation decline associated with changes in water availability from purely spectral fluctuations.

---

NDBI

NDBI provides information related to built-up surfaces.

In an urban setting, this is important because vegetation loss associated with construction or land conversion may have a different spatial signature from vegetation stress.

---

SAVI

Soil Adjusted Vegetation Index can provide additional robustness where exposed soil influences vegetation measurements.

---

3. Temporal Representation

The central idea behind CANOPY is that vegetation loss is an event in time, not simply a low pixel value.

A single observation can be misleading.

A temporal representation allows the system to distinguish:

Normal seasonal variation
        |
        |---- temporary anomaly
        |
        |---- sensor / cloud artifact
        |
        |---- persistent decline
        |
        |---- structural vegetation loss

CANOPY therefore uses temporal representations such as:

- harmonic seasonality,
- persistence filtering,
- temporal differences,
- lagged features,
- trend estimation,
- and temporal residual analysis.

The purpose is to model the expected behavior of a location before deciding whether its current state represents abnormal change.

---

4. Vegetation-Loss Detection

CANOPY does not rely on a single detector.

Instead, the detection layer is designed around explicit baselines.

Baseline A — Single-Date NDVI Threshold

A location is flagged when vegetation falls below a configurable threshold.

This provides a simple baseline.

Baseline B — Bi-Temporal NDVI Delta

The system compares vegetation between two time windows.

$$
\Delta NDVI = NDVI_t - NDVI_{t-k}
$$

A sufficiently negative change may indicate vegetation decline.

Baseline C — BFAST-Style Monitoring

BFAST-style reasoning attempts to identify structural changes in temporal signals rather than relying on a single threshold.

Baseline D — Harmonic + Persistence

Seasonality is modeled first.

A candidate anomaly is considered more meaningful when the deviation persists rather than appearing as a single observation.

Additional Research Baselines

The experimental protocol also defines broader detection baselines including:

- DIST-ALERT,
- temporal gradient-boosted models,
- and temporal deep models where justified by earlier experimental results.

This prevents the research from comparing the proposed approach only against weak baselines.

---

Detection Objective

The detection problem can be represented as:

$$
P(Y_t = Loss \mid X_{1:t})
$$

where:

- $X_{1:t}$ represents observations available up to time $t$,
- $Y_t$ represents the vegetation state,
- and no future observations should influence the prediction at time $t$.

A key objective is minimizing detection delay without producing an unacceptable increase in false positives.

---

5. Future Risk Forecasting

Detection answers:

«"What is happening?"»

Forecasting asks:

«"What is likely to happen next?"»

CANOPY supports baseline forecasting approaches including:

- persistence,
- seasonal naive forecasting,
- linear trend,
- random forest,
- gradient-boosted models,
- and other temporal feature-based models.

Forecasting can be performed across multiple horizons.

For example:

Observed trajectory
      |
      +---- 30 day horizon
      |
      +---- 60 day horizon
      |
      +---- 90 day horizon
      |
      +---- longer planning horizon

The system evaluates both point accuracy and uncertainty.

---

6. Heat Exposure Modeling

Vegetation is not only an ecological variable.

Urban vegetation can influence local thermal conditions and exposure.

CANOPY therefore introduces an impact layer connecting vegetation state with heat exposure.

Potential inputs include:

- land surface temperature,
- vegetation indicators,
- built-up intensity,
- population distribution,
- spatial vulnerability proxies,
- and other contextual variables.

The primary target documented by the experimental protocol is land surface temperature (LST), with a secondary downscaled air-temperature proxy where appropriate.

---

Population-Weighted Exposure

A temperature map alone does not answer:

«"Who is affected?"»

CANOPY therefore considers population-weighted exposure.

Conceptually:

$$
Exposure = \sum_i Population_i \times Risk_i
$$

where the spatial unit $i$ may represent:

- grid cells,
- administrative units,
- or other analysis regions.

This creates a bridge between environmental change and human impact.

---

7. Intervention Modeling

Once risk has been identified, CANOPY moves from prediction toward decision support.

Possible intervention categories include:

- preserve existing vegetation,
- restore degraded vegetation,
- plant new trees,
- prioritize high-exposure regions,
- or combine preservation and planting.

The intervention module allows candidate actions to be evaluated against constraints.

---

Intervention Constraints

Real-world urban greening is constrained.

A theoretically optimal location may be impossible to implement because of:

- insufficient land,
- water scarcity,
- budget limitations,
- inaccessible infrastructure,
- existing land use,
- operational capacity,
- or competing priorities.

CANOPY therefore treats intervention planning as a constrained optimization problem rather than simply ranking locations by temperature.

---

8. Spatial Optimization

The optimization stage asks:

«Given a limited intervention budget, where should resources be allocated to maximize expected benefit?»

Candidate objectives may include:

- reduction in population-weighted heat exposure,
- benefit per tree,
- benefit per unit cost,
- benefit per unit water,
- population reached,
- vulnerability-weighted benefit,
- and equity constraints.

The repository includes explicit optimization experiment configurations and a constrained greedy optimization architecture.

---

Optimization Formulation

A simplified objective can be expressed as:

$$
\max_{S} ; B(S)
$$

subject to:

$$
Cost(S) \leq B
$$

$$
Water(S) \leq W
$$

$$
Land(S) \leq L
$$

where:

- $S$ is the selected intervention set,
- $B(S)$ is expected benefit,
- $B$ is the available budget,
- $W$ is available water,
- and $L$ represents land/access constraints.

A more complete objective may combine multiple terms:

$$
J(S) =
\lambda_1 E(S)
+
\lambda_2 H(S)
+
\lambda_3 V(S)
+
\lambda_4 Q(S)

\lambda_5 C(S)

\lambda_6 U(S)
$$

where:

- $E(S)$ = expected exposure reduction,
- $H(S)$ = heat-risk reduction,
- $V(S)$ = vulnerability-weighted benefit,
- $Q(S)$ = equity contribution,
- $C(S)$ = operational cost,
- $U(S)$ = uncertainty penalty.

The exact objective is configurable rather than hard-coded into the research concept.

---

9. Uncertainty Quantification

A decision-support system should not only output:

Risk = 0.87

It should also communicate:

Risk = 0.87
Uncertainty = high

CANOPY includes uncertainty-aware components intended to estimate:

- prediction intervals,
- confidence,
- ranking stability,
- and sensitivity to perturbations.

The architecture includes conformal uncertainty methods and uncertainty-aware intervention ranking.

---

Why Uncertainty Matters

Consider two candidate intervention locations:

Location| Expected Benefit| Uncertainty
A| 0.91| High
B| 0.86| Low

A purely predictive system may select A.

A decision-support system should ask whether A remains preferable when model uncertainty is considered.

CANOPY therefore investigates ranking stability under perturbations.

One planned metric is Kendall's $\tau$ between rankings generated from baseline and perturbed inputs.

---

10. Evaluation and Experiment Registry

CANOPY treats reproducibility as part of the research architecture.

Each experiment is intended to have:

- a configuration ID,
- a random seed,
- documented data splits,
- explicit metrics,
- and a registry entry.

The repository includes:

- experiment configurations,
- experiment documentation,
- evaluation modules,
- and research scripts.

This allows experiments to be reproduced and compared rather than existing as undocumented notebook states.

---

Detection Strategy

CANOPY's detection research can be summarized as:

Raw observations
       |
       v
Quality filtering
       |
       v
Spectral indices
       |
       v
Expected seasonal behavior
       |
       v
Observed - expected residual
       |
       v
Persistence filtering
       |
       v
Candidate vegetation loss
       |
       v
Spatial validation
       |
       v
Risk score

The important distinction is between:

Observation

A value changed.

and:

Evidence of persistent change

A value changed in a way that is:

- statistically meaningful,
- temporally persistent,
- spatially plausible,
- and not explained by known artifacts.

CANOPY focuses on the second problem.

---

Forecasting Strategy

Forecasting experiments compare increasingly complex approaches.

Persistence

Assume the current state continues.

This is intentionally simple and difficult to beat in some real-world forecasting settings.

Seasonal Naive

Use historical seasonal behavior as a baseline.

Linear Trend

Estimate future trajectory from recent observations.

Tree-Based Models

Use lagged temporal and contextual features with:

- Random Forest,
- Gradient Boosting,
- or related estimators.

Probabilistic Forecasting

Where supported, generate prediction intervals rather than only point predictions.

The system evaluates:

- MAE,
- RMSE,
- horizon-specific performance,
- and interval coverage.

---

Heat and Exposure Model

The heat module translates environmental conditions into an exposure surface.

A simplified conceptual relationship is:

$$
Risk_i = f(LST_i, Vegetation_i, BuiltUp_i, Population_i, Vulnerability_i)
$$

This is deliberately treated as a modeling problem rather than assuming a universal deterministic relationship.

The experimental protocol requires the target variable and construct validity of the exposure metric to be explicitly documented.

---

Intervention Optimization

CANOPY compares the proposed intervention strategy against simpler alternatives.

Possible baseline strategies include:

1. Random allocation
2. Maximum LST
3. Minimum canopy
4. Maximum population
5. Maximum vulnerability proxy
6. Greedy exposure reduction
7. Full CANOPY optimization
8. Plant-only CANOPY strategy

These baselines help answer whether the complete system adds value beyond intuitive heuristics.

---

Uncertainty and Reliability

A recommendation is useful only when its uncertainty is understood.

CANOPY investigates uncertainty through:

- prediction intervals,
- conformal methods,
- perturbation experiments,
- ranking stability,
- missing-data experiments,
- cloud/noise injection,
- and sensitivity analysis.

A recommendation can therefore be interpreted using:

Priority
Expected benefit
Confidence
Uncertainty
Feasibility
Cost
Population impact

rather than using a single opaque score.

---

Research Methodology

CANOPY follows a staged methodology.

Phase 1 — Research Discovery

Establish:

- research question,
- literature landscape,
- candidate datasets,
- candidate methods,
- evaluation metrics,
- and known limitations.

Phase 2 — Pilot Data Validation

Verify:

- data availability,
- spatial coverage,
- temporal density,
- preprocessing feasibility,
- and labeling feasibility.

Phase 3 — Baseline Detection

Implement and evaluate simple detection baselines before introducing additional complexity.

Phase 4 — Temporal Modeling

Introduce:

- seasonality,
- persistence,
- temporal features,
- and temporal change detection.

Phase 5 — Ground-Truth Validation

Compare detected events against manually interpreted labels and other documented reference sources.

Phase 6 — Forecasting

Estimate future vegetation trajectories and quantify uncertainty.

Phase 7 — Heat Exposure

Connect environmental conditions with spatial exposure.

Phase 8 — Intervention Modeling

Model preserve, restore, and planting scenarios.

Phase 9 — Optimization

Optimize interventions under explicit constraints.

This staged structure is represented in the repository through milestone configurations and experiment documentation.

---

Experimental Protocol

CANOPY follows several methodological rules.

Rule 1 — No test leakage

Held-out test regions must not influence:

- feature selection,
- threshold tuning,
- model selection,
- or preprocessing statistics.

Rule 2 — No future information

Features available at time $t$ must not use observations from $t+1$ or later.

Rule 3 — Pseudo-labels are not ground truth

External disturbance products may be used as reference or comparison data, but they must not automatically be presented as ground-truth labels.

Rule 4 — Report negative results

A method that fails should remain documented.

Rule 5 — Experiments are registered

Experiments should have:

- configuration IDs,
- seeds,
- split definitions,
- metrics,
- and reproducible parameters.

These principles are explicitly defined in the repository's experimental protocol.

---

Evaluation Metrics

Detection

Primary metrics include:

- Precision
- Recall
- F1
- Persistent-class F1
- False Positive Rate
- Detection Delay
- IoU where polygon labels are available

The central operational metric is not simply classification accuracy.

A detector that discovers vegetation loss six months late may have high accuracy but low practical value.

Therefore:

«Detection delay matters.»

---

Forecasting Metrics

Forecasting is evaluated using:

- MAE
- RMSE
- horizon-specific error
- prediction interval coverage
- sharpness
- CRPS where probabilistic forecasts are available

---

Heat / Exposure Metrics

Potential metrics include:

- RMSE
- MAE
- spatial Pearson correlation
- station-based validation where appropriate
- population-weighted exposure error

---

Optimization Metrics

Optimization evaluation includes:

- total expected population-weighted exposure reduction,
- benefit per tree,
- benefit per currency unit,
- benefit per water unit,
- population benefited,
- equity metrics,
- ranking stability.

Equity analysis can include:

- Gini coefficient of ward-level benefits,
- minimum quintile benefit share,
- and distributional comparisons.

These metrics are part of the defined experimental protocol rather than post-hoc additions.

---

Leakage Prevention

CANOPY explicitly guards against several common geospatial ML failure modes.

Spatial Leakage

Nearby pixels can be highly correlated.

Random pixel-level train/test splits can therefore produce unrealistically optimistic results.

CANOPY uses spatial blocks instead.

Temporal Leakage

Forecasting models cannot use future observations during feature construction.

Label Leakage

External disturbance products cannot simultaneously be treated as both:

- the prediction target,
- and the independent validation source.

Preprocessing Leakage

Normalization and other learned preprocessing statistics should be computed using training regions only.

---

Spatial Validation

A representative spatial split is:

Bengaluru
│
├── Training blocks
│
├── Validation blocks
│
└── Test blocks
       |
       └── spatial buffer from training regions

The experimental protocol specifies block-based validation and a buffer between training and test regions to reduce spatial autocorrelation leakage.

---

Temporal Validation

For forecasting experiments, a representative temporal structure is:

Months 1 ───────────── 12
        TRAIN

Months 13 ─────── 15
        VALIDATION

Months 16 ─────── 18
        TEST

This ensures that forecasting performance is evaluated on genuinely future observations rather than shuffled temporal samples.

---

Reproducibility

CANOPY is structured as a research repository rather than an ad-hoc notebook collection.

The project uses:

- Python packaging through "pyproject.toml"
- YAML experiment configurations
- deterministic experiment configuration
- pytest-based testing
- modular source packages
- documented research protocols
- experiment registries
- explicit data definitions

The package currently targets Python ">=3.9" and exposes a "canopy" command-line entry point.

---

Repository Structure

canopy/
│
├── app/
│   └── research_interface.py
│
├── configs/
│   ├── defaults.yaml
│   ├── experiment_optimization.yaml
│   ├── m2_data_validation.yaml
│   ├── m3_baseline_detection.yaml
│   ├── m4_temporal_model.yaml
│   ├── m5_ground_truth.yaml
│   ├── m6_forecasting.yaml
│   ├── m7_heat_exposure.yaml
│   ├── m8_intervention.yaml
│   ├── m9_optimization.yaml
│   └── mvre_detection.yaml
│
├── data/
│   └── external/
│       ├── bengaluru_aoi.geojson
│       ├── bengaluru_pilot_aoi.geojson
│       ├── m3_labels_template.csv
│       └── mvre_labels_template.csv
│
├── docs/
│   ├── architecture.md
│   ├── dataset_card.md
│   ├── experimental_protocol.md
│   ├── ethics.md
│   ├── limitations.md
│   │
│   ├── datasets/
│   │   └── preprocessing_spec_pilot.md
│   │
│   ├── experiments/
│   │   ├── m3_baseline_detection.md
│   │   ├── m4_temporal_model.md
│   │   ├── m5_ground_truth.md
│   │   ├── m6_forecasting.md
│   │   ├── m7_heat_exposure.md
│   │   ├── m8_intervention.md
│   │   └── m9_optimization.md
│   │
│   ├── literature/
│   │   └── literature_table.md
│   │
│   └── methodology/
│
├── results/
│
├── scripts/
│   ├── run_mvre.py
│   ├── run_optimization_eval.py
│   └── gee_export_sentinel2.py
│
├── src/
│   └── canopy/
│       ├── cli.py
│       ├── config.py
│       ├── data/
│       ├── detection/
│       ├── evaluation/
│       ├── experiments/
│       ├── features/
│       ├── forecasting/
│       ├── geospatial/
│       ├── heat/
│       ├── intervention/
│       ├── optimization/
│       ├── temporal/
│       ├── uncertainty/
│       └── visualization/
│
├── tests/
│
├── CITATION.cff
├── LICENSE
├── pyproject.toml
└── README.md

The repository currently follows this modular organization, including separate packages for detection, forecasting, heat, intervention, optimization, temporal modeling, uncertainty, evaluation, and visualization.

---

Installation

Requirements

- Python 3.9+
- pip
- Git
- GDAL-compatible geospatial environment where required
- Optional Google Earth Engine access for GEE-based workflows

---

Clone

git clone https://github.com/chetx27/canopy.git
cd canopy

---

Create a virtual environment

macOS / Linux

python3 -m venv .venv
source .venv/bin/activate

Windows

python -m venv .venv
.venv\Scripts\activate

---

Install the package

pip install -e .

---

Install development dependencies

pip install -e ".[dev]"

---

Install Google Earth Engine dependencies

pip install -e ".[gee]"

---

Install MLflow support

pip install -e ".[mlflow]"

---

Install everything

pip install -e ".[all]"

The optional dependency groups are defined in "pyproject.toml".

---

Configuration

CANOPY uses YAML configuration files rather than embedding experimental parameters throughout source code.

Example configuration files include:

configs/
├── defaults.yaml
├── m2_data_validation.yaml
├── m3_baseline_detection.yaml
├── m4_temporal_model.yaml
├── m5_ground_truth.yaml
├── m6_forecasting.yaml
├── m7_heat_exposure.yaml
├── m8_intervention.yaml
├── m9_optimization.yaml
└── mvre_detection.yaml

This makes experimental changes:

- explicit,
- version-controlled,
- reproducible,
- reviewable,
- and easier to compare.

---

Running CANOPY

The project exposes a command-line entry point:

canopy

The research pipeline also contains dedicated experiment scripts.

---

Research Experiments

Minimum Viable Research Experiment

python scripts/run_mvre.py

The MVRE is designed to answer the first critical question:

«Is there enough signal in the pilot data to justify building the full system?»

---

Optimization Evaluation

python scripts/run_optimization_eval.py

This evaluates intervention strategies and compares optimization approaches.

---

Google Earth Engine Export

A template is provided for Sentinel-2 export workflows:

python scripts/gee_export_sentinel2.py

GEE-based experiments require the appropriate Earth Engine authentication and project configuration.

---

Data

CANOPY is designed to work with multiple geospatial data sources.

Primary Remote-Sensing Sources

Sentinel-2

Multispectral imagery used for vegetation and urban spectral analysis.

Potential applications:

- NDVI,
- EVI,
- NDWI,
- NDBI,
- SAVI,
- temporal vegetation monitoring.

Sentinel-1

SAR observations can provide additional information where optical observations are affected by:

- clouds,
- seasonal gaps,
- or other limitations.

Harmonized Landsat/Sentinel Products

Useful for increasing temporal coverage and constructing longer historical records.

DIST-ALERT

Disturbance information can be used as a comparison or auxiliary reference source.

---

Auxiliary Data

CANOPY can incorporate contextual datasets including:

- population,
- climate,
- land use,
- infrastructure,
- urban morphology,
- and vulnerability proxies.

These datasets allow the system to move from:

Vegetation loss

toward:

Vegetation loss
+
Heat exposure
+
Population
+
Feasibility
=
Intervention priority

---

Dataset and Labeling Strategy

Ground truth is one of the most important parts of the system.

Remote-sensing anomaly detection can easily produce apparently convincing maps that are wrong.

CANOPY therefore separates:

Observations

Raw or processed satellite-derived measurements.

Reference signals

External datasets that indicate possible disturbances.

Human labels

Manually interpreted cells or polygons.

Model predictions

Outputs generated by CANOPY.

These categories must not be conflated.

---

Minimum Viable Research Experiment

The repository's experimental protocol defines a pilot-scale MVRE.

Representative parameters include:

Parameter| Pilot Setting
Area| ~25 km² Bengaluru pilot
Period| ~18 months
Spatial grid| 30 m
Manual labels| 150 cells
Primary task| Vegetation-loss detection
Primary metrics| Persistent F1, detection delay, FPR

The protocol compares multiple detection methods and defines a go/no-go criterion before committing to full-scale experimentation.

---

Research Outputs

CANOPY is designed to produce several classes of outputs.

1. Vegetation Anomaly Maps

Spatial layers showing:

- detected vegetation anomalies,
- persistence,
- confidence,
- and temporal evolution.

---

2. Risk Maps

Spatial risk stratification across:

- geographic region,
- time horizon,
- severity,
- and uncertainty.

---

3. Forecast Trajectories

For individual cells or spatial regions:

Historical vegetation
        |
        v
Current state
        |
        v
Forecast trajectory
        |
        v
Prediction interval

---

4. Heat Exposure Surfaces

Maps showing estimated spatial exposure based on:

- temperature,
- vegetation,
- population,
- and contextual risk factors.

---

5. Intervention Priority Layers

Potential outputs include:

- preserve priority,
- restore priority,
- planting priority,
- combined intervention priority,
- expected benefit,
- cost,
- feasibility,
- and uncertainty.

---

6. Interactive Research Interface

The repository includes a research interface for inspecting cell-level trajectories and related outputs.

This is intended to make model behavior spatially interpretable rather than hiding results behind aggregate metrics.

---

Interpretation of Results

CANOPY distinguishes between:

Observed outcomes

Directly measured from available datasets.

Predicted outcomes

Generated by a statistical or machine-learning model.

Simulated outcomes

Produced by intervention scenarios.

Counterfactual outcomes

Estimated outcomes under alternative actions or no intervention.

This distinction is critical.

For example:

«"Planting 1,000 trees will reduce city temperature by X°C"»

would be an inappropriate claim unless supported by validated causal evidence.

Instead, CANOPY should report:

«"Under the modeled assumptions, the simulated intervention scenario is associated with an estimated reduction in the selected exposure metric."»

All intervention outputs should therefore be interpreted as modeled scenarios unless experimentally validated in the physical environment.

---

Decision-Support Philosophy

CANOPY is not intended to replace urban planners, ecologists, climate scientists, or infrastructure authorities.

It is intended to provide another layer of evidence.

The system should help decision-makers ask:

- Where is vegetation changing?
- Is the change persistent?
- How unusual is the change?
- What might happen next?
- Who is exposed?
- Which interventions are feasible?
- What is the expected benefit?
- How much will the intervention cost?
- How sensitive is the recommendation to uncertainty?
- Does the ranking remain stable under alternative assumptions?

---

Limitations

CANOPY has several important limitations.

Remote-Sensing Limitations

Satellite data can contain:

- cloud gaps,
- atmospheric effects,
- mixed pixels,
- spatial resolution limitations,
- temporal gaps,
- seasonal artifacts,
- and sensor inconsistencies.

---

Label Limitations

Manual interpretation is expensive and may contain:

- human disagreement,
- ambiguous events,
- incomplete coverage,
- and labeling bias.

---

Causal Limitations

A statistical relationship between vegetation and temperature does not automatically establish causality.

CANOPY's heat and intervention modules should therefore be interpreted as decision-support modeling unless causal validation is available.

---

Geographic Generalization

A model developed for Bengaluru may not automatically generalize to:

- Delhi,
- Mumbai,
- Singapore,
- London,
- Nairobi,
- or other urban environments.

Urban morphology, climate, vegetation types, satellite conditions, and intervention constraints can differ substantially.

Transferability must therefore be experimentally evaluated.

---

Optimization Limitations

An optimization algorithm can only optimize the assumptions and constraints provided to it.

If:

- cost estimates are wrong,
- land availability is wrong,
- water constraints are wrong,
- exposure models are biased,

the resulting ranking can also be wrong.

Optimization does not magically remove uncertainty from upstream models.

---

Ethics and Responsible Use

Urban environmental intelligence can affect real-world planning decisions.

CANOPY therefore emphasizes:

- transparency,
- uncertainty reporting,
- reproducibility,
- non-discrimination,
- documentation of assumptions,
- and human oversight.

The system should not be used as an autonomous authority for:

- land acquisition,
- displacement,
- enforcement,
- denial of services,
- or other high-impact decisions.

Environmental models should support decisions rather than conceal them behind algorithmic scores.

---

Research Robustness

CANOPY includes experiments designed to evaluate failure modes.

Missing Data

Evaluate degradation as observations are removed.

Cloud / Noise Injection

Introduce realistic observation corruption and measure false-alert behavior.

Ranking Stability

Perturb model inputs and determine whether intervention rankings remain stable.

Spatial Transfer

Evaluate performance on geographically separated regions.

Cross-City Transfer

Measure performance degradation when moving beyond Bengaluru.

Equity

Evaluate whether benefits are distributed fairly across population groups and spatial regions.

The experimental protocol explicitly includes robustness, equity, and zero-shot transfer experiments.

---

Experiment Catalog

ID| Phase| Research Question
MVRE-D0| Pilot| Is vegetation-loss detection feasible?
D1| Detection| Does temporal persistence improve detection?
D2| Detection| Can CANOPY detect events earlier?
D3| Detection| Which feature groups contribute most?
D4| Detection| Does performance hold under spatial CV?
F1| Forecasting| How accurate are future trajectories?
F2| Forecasting| Are uncertainty intervals calibrated?
H1| Heat| Which exposure formulation is most reliable?
H2| Heat| How sensitive is exposure to population weighting?
O1| Optimization| How does performance change with budget?
O2| Optimization| Is preservation preferable to planting in some settings?
O3| Optimization| How sensitive are rankings to objective weights?
O4| Optimization| How stable are intervention rankings?
R1| Robustness| How does missing data affect performance?
R2| Robustness| How does cloud/noise affect false positives?
R3| Equity| How are intervention benefits distributed?
X1| Transfer| How well does the system transfer to a new city?

This catalog follows the repository's documented experimental protocol.

---

Why CANOPY Is More Than a Vegetation Classifier

A conventional remote-sensing project might look like:

Satellite image
      ↓
ML model
      ↓
Vegetation / no vegetation

CANOPY instead attempts:

Satellite observations
        ↓
Temporal understanding
        ↓
Change detection
        ↓
Future forecasting
        ↓
Climate / heat exposure
        ↓
Population impact
        ↓
Intervention simulation
        ↓
Constrained optimization
        ↓
Uncertainty-aware decision support

That difference is fundamental.

The research problem is not:

«"Can AI identify trees?"»

It is:

«"Can temporal geospatial intelligence help cities identify emerging vegetation risk early enough to make better intervention decisions under real-world constraints?"»

---

Research Contributions

The intended contribution of CANOPY is the integration of several traditionally separated components:

1. Temporal Vegetation-Loss Detection

Detect persistent abnormal change rather than relying only on static vegetation thresholds.

2. Multi-Horizon Risk Forecasting

Move from detection toward estimation of future trajectories.

3. Environmental-to-Human Exposure Modeling

Connect vegetation and thermal conditions with population distribution.

4. Constraint-Aware Intervention Optimization

Optimize interventions under realistic budget, water, land, and operational constraints.

5. Uncertainty-Aware Decision Support

Expose uncertainty and ranking stability instead of producing unexplained deterministic recommendations.

6. Reproducible Geospatial Research

Make experiment configurations, splits, metrics, assumptions, and negative results explicit.

---

Design Principles

CANOPY is built around several principles.

Evidence Before Complexity

Start with strong baselines.

Do not use deep learning merely because the project is labeled AI.

Temporal Before Static

Environmental change is inherently temporal.

Spatial Validation Before Aggregate Accuracy

Pixel-level random splits can be misleading.

Uncertainty Before Overconfidence

Predictions should communicate confidence.

Optimization After Prediction

Do not optimize interventions before understanding the predictive problem.

Explicit Constraints

A recommendation that cannot be implemented is not operationally useful.

Reproducibility Before Claims

Every major claim should map to a reproducible experiment.

---

Future Research

Planned research directions include:

Advanced Temporal Models

Potential investigation of:

- temporal transformers,
- sequence models,
- spatiotemporal neural networks,
- neural state-space models,
- and foundation-model-based remote sensing representations.

Complex models should only be introduced when they provide measurable improvement over established baselines.

---

Multi-Sensor Fusion

Combine:

- Sentinel-1,
- Sentinel-2,
- Landsat,
- thermal products,
- DEM,
- climate data,
- and urban morphology.

---

Higher-Resolution Change Detection

Investigate finer-resolution imagery where data licensing and cost permit.

---

Causal Intervention Evaluation

Move beyond modeled intervention benefit toward:

- quasi-experimental analysis,
- before/after intervention studies,
- matched controls,
- and eventually causal impact evaluation.

---

Cross-City Generalization

Evaluate whether the system can transfer from Bengaluru to cities with different:

- climates,
- vegetation structures,
- densities,
- planning systems,
- and socioeconomic conditions.

---

Human-in-the-Loop Validation

Introduce expert feedback into the validation pipeline without allowing subjective feedback to silently become ground truth.

---

Explainable Intervention Ranking

Future intervention outputs can expose:

Priority: 0.91

Main contributors:
├── High heat exposure
├── Persistent canopy decline
├── High population exposure
├── High intervention feasibility
└── Moderate uncertainty

Counterfactuals:
├── No intervention
├── Preserve
├── Restore
└── Plant

This turns the optimizer from a black box into an auditable decision-support system.

---

Project Status

Current repository milestones include:

- Research discovery
- Pilot data validation
- Baseline detection pipeline
- Temporal modeling pipeline
- Ground-truth validation

The project remains research-oriented and should be considered an evolving experimental system rather than a production municipal platform.

---

Reproducibility Checklist

Before treating an experiment as final:

- [ ] Dataset version documented
- [ ] AOI documented
- [ ] Spatial resolution documented
- [ ] Temporal range documented
- [ ] Train/validation/test split documented
- [ ] Random seed recorded
- [ ] Configuration committed
- [ ] Preprocessing documented
- [ ] Feature construction documented
- [ ] No future observations used
- [ ] No test-region tuning performed
- [ ] Ground-truth source documented
- [ ] Baselines evaluated
- [ ] Primary metrics reported
- [ ] Confidence intervals reported where applicable
- [ ] Negative results documented
- [ ] Limitations documented
- [ ] Experiment registry updated

---

Getting Started for Researchers

If you are new to the repository, the recommended reading order is:

1. README.md
      ↓
2. docs/architecture.md
      ↓
3. docs/dataset_card.md
      ↓
4. docs/experimental_protocol.md
      ↓
5. docs/experiments/
      ↓
6. configs/
      ↓
7. src/canopy/
      ↓
8. scripts/
      ↓
9. results/

Start with the research protocol before changing model architecture.

The goal is to understand what is being measured and why before modifying how it is modeled.

---

Citation

If you use CANOPY in research, please cite the repository using the included "CITATION.cff".

CANOPY Research Team.
CANOPY: Temporal Geospatial AI for Urban Vegetation Loss Detection
and Climate Risk Mitigation.
GitHub repository.

A machine-readable citation file is included at:

CITATION.cff

---

License

CANOPY is released under the MIT License.

See "LICENSE" (LICENSE) for the full license text.

---

Acknowledgements

CANOPY is developed as part of research into climate-resilient urban infrastructure and geospatial AI.

The project builds upon the broader scientific and open-source ecosystems surrounding:

- Earth observation,
- remote sensing,
- geospatial computing,
- machine learning,
- climate science,
- urban analytics,
- and open spatial data.

---

Contact and Collaboration

CANOPY is intended to support research collaboration in:

- geospatial AI,
- remote sensing,
- climate-risk modeling,
- urban resilience,
- vegetation monitoring,
- spatial optimization,
- and environmental decision support.

For research collaboration, dataset partnerships, validation studies, or deployment discussions, please open a GitHub issue or contact the project maintainers.

---

Final Perspective

CANOPY is built around a simple idea:

«Cities should not have to wait until environmental damage becomes obvious before deciding where to act.»

Satellite observations can reveal change.

Temporal models can determine whether that change persists.

Forecasting can estimate what may happen next.

Heat-exposure modeling can connect environmental conditions to people.

Optimization can translate those estimates into constrained intervention priorities.

Uncertainty quantification can communicate how much confidence should be placed in those recommendations.

Together, these components form a research framework for moving from:

Observation
    ↓
Detection
    ↓
Prediction
    ↓
Impact
    ↓
Decision

rather than stopping at a map.

CANOPY is an attempt to turn urban vegetation monitoring into an evidence-driven, temporal, uncertainty-aware decision system.
