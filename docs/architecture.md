# CANOPY System Architecture

```mermaid
flowchart TB
    subgraph acquire [Data Acquisition]
        S2[Sentinel-2 L2A]
        S1[Sentinel-1 SAR]
        HLS[HLS / DIST-ALERT]
        AUX[WorldPop / ERA5 / OSM]
    end

    subgraph prep [QC and Harmonization]
        QC[Cloud and QC filters]
        HARM[CRS align and resample]
        FEAT[Spectral indices and morphology]
    end

    subgraph temporal [Temporal Representation]
        HAR[Harmonic seasonality]
        PER[Persistence filter]
    end

    subgraph detect [Detection]
        B1[NDVI threshold]
        B2[Bi-temporal delta]
        B3[BFAST-style monitor]
        B4[Harmonic persistence]
    end

    subgraph forecast [Forecasting]
        F1[Persistence / seasonal naive]
        F2[Linear trend / GBDT]
    end

    subgraph impact [Impact]
        HEAT[LST and exposure surface]
        EXP[Population-weighted exposure]
    end

    subgraph decide [Intervention]
        SIM[Preserve / restore / plant simulator]
        OPT[Constrained greedy optimizer]
        UNC[Conformal uncertainty]
    end

    subgraph eval [Evaluation]
        MET[Metrics and spatial CV]
        REG[Experiment registry]
    end

    acquire --> prep --> temporal --> detect
    detect --> forecast --> impact --> decide
    decide --> eval
    UNC --> decide
```

## Module map

| Layer | Package | Entry points |
|---|---|---|
| Config | `canopy.config` | YAML load/merge |
| Indices | `canopy.features.indices` | NDVI, EVI, NDWI, NDBI, SAVI |
| Temporal | `canopy.temporal.*` | Harmonic fit, persistence |
| Detection | `canopy.detection.baselines` | All detector methods |
| Forecasting | `canopy.forecasting.baselines` | Horizon forecasts |
| Heat | `canopy.heat.exposure` | Exposure surfaces |
| Optimization | `canopy.optimization.engine` | Optimizer + baselines |
| Uncertainty | `canopy.uncertainty.conformal` | Intervals, ranking stability |
| Evaluation | `canopy.evaluation.*` | Metrics, splits, registry |
| Experiments | `canopy.experiments.mvre` | MVRE runner |

## Runnable scripts

| Script | Purpose |
|---|---|
| `scripts/run_mvre.py` | Minimum viable detection experiment |
| `scripts/run_optimization_eval.py` | Optimization baseline comparison |
| `scripts/gee_export_sentinel2.py` | GEE export template |
| `app/research_interface.py` | Cell-level trajectory inspector |
