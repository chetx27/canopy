from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


LABEL_CLASSES = ["stable", "seasonal", "persistent_loss"]


def generate_annotation_batch(
    cube: np.ndarray,
    times: list[str],
    n_total: int = 500,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    _, rows, cols = cube.shape
    per_class = n_total // len(LABEL_CLASSES)
    remainder = n_total - per_class * len(LABEL_CLASSES)

    candidates = []
    for row in range(rows):
        for col in range(cols):
            series = cube[:, row, col]
            valid = np.isfinite(series)
            if valid.sum() < 8:
                continue
            trend = np.polyfit(np.arange(len(series))[valid], series[valid], 1)[0]
            seasonal = float(np.nanstd(series))
            candidates.append(
                {
                    "row": row,
                    "col": col,
                    "ndvi_mean": float(np.nanmean(series)),
                    "ndvi_std": seasonal,
                    "trend": float(trend),
                    "valid_fraction": float(valid.mean()),
                }
            )
    pool = pd.DataFrame(candidates)
    if pool.empty:
        raise ValueError("No valid cells available for annotation batch")

    stable_pool = pool[(pool["trend"].abs() < 0.006) & (pool["ndvi_std"] < 0.13)]
    seasonal_pool = pool[(pool["trend"].abs() < 0.01) & (pool["ndvi_std"] >= 0.13)]
    loss_pool = pool[pool["trend"] <= -0.007]

    def pick(pool_df: pd.DataFrame, n: int) -> pd.DataFrame:
        if pool_df.empty:
            pool_df = pool
        n = min(n, len(pool_df))
        return pool_df.sample(n=n, random_state=int(rng.integers(0, 1_000_000)))

    parts = [
        pick(stable_pool, per_class + (1 if remainder > 0 else 0)),
        pick(seasonal_pool, per_class + (1 if remainder > 1 else 0)),
        pick(loss_pool, per_class + (1 if remainder > 2 else 0)),
    ]
    batch = pd.concat(parts, ignore_index=True)
    batch = batch.drop_duplicates(subset=["row", "col"])
    if len(batch) < n_total:
        extra = pool.sample(n=min(n_total - len(batch), len(pool)), random_state=seed)
        batch = pd.concat([batch, extra], ignore_index=True).drop_duplicates(subset=["row", "col"])
    batch = batch.head(n_total)
    batch["cell_id"] = batch.apply(lambda r: f"cell_{int(r['row'])}_{int(r['col'])}", axis=1)
    batch["label"] = ""
    batch["event_month"] = ""
    batch["annotator"] = ""
    batch["notes"] = ""
    return batch[
        [
            "cell_id",
            "row",
            "col",
            "ndvi_mean",
            "ndvi_std",
            "trend",
            "valid_fraction",
            "label",
            "event_month",
            "annotator",
            "notes",
        ]
    ]


def cohen_kappa(rater_a: pd.Series, rater_b: pd.Series) -> float:
    labels = sorted(set(rater_a.unique()) | set(rater_b.unique()))
    n = len(rater_a)
    if n == 0:
        return float("nan")
    conf = pd.crosstab(rater_a, rater_b, dropna=False).reindex(index=labels, columns=labels, fill_value=0)
    conf = conf.loc[labels, labels]
    po = np.trace(conf.values) / n
    pa = conf.sum(axis=1).values / n
    pb = conf.sum(axis=0).values / n
    pe = float(np.sum(pa * pb))
    if pe == 1.0:
        return 1.0
    return float((po - pe) / (1 - pe))


def inter_rater_report(df_a: pd.DataFrame, df_b: pd.DataFrame) -> dict[str, Any]:
    key = ["cell_id", "row", "col"]
    a = df_a[key + ["label"]].rename(columns={"label": "label_a"})
    b = df_b[key + ["label"]].rename(columns={"label": "label_b"})
    merged = a.merge(b, on=key, how="inner")
    if merged.empty:
        return {"error": "no_overlap", "n_overlap": 0}
    merged = merged[(merged["label_a"].astype(str).str.strip() != "") & (merged["label_b"].astype(str).str.strip() != "")]
    if merged.empty:
        return {"error": "no_labeled_overlap", "n_overlap": 0}

    overall_kappa = cohen_kappa(merged["label_a"], merged["label_b"])
    per_class = {}
    for cls in LABEL_CLASSES:
        y_a = (merged["label_a"] == cls).astype(int)
        y_b = (merged["label_b"] == cls).astype(int)
        per_class[cls] = cohen_kappa(y_a, y_b)

    return {
        "n_overlap": len(merged),
        "overall_kappa": overall_kappa,
        "per_class_kappa": per_class,
        "agreement_rate": float((merged["label_a"] == merged["label_b"]).mean()),
    }


def merge_rater_labels(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    min_kappa: float = 0.6,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    report = inter_rater_report(df_a, df_b)
    key = ["cell_id", "row", "col"]
    a = df_a.copy()
    b = df_b.copy()
    if "event_month" not in a.columns:
        a["event_month"] = ""
    if "event_month" not in b.columns:
        b["event_month"] = ""
    merged = a.merge(b, on=key, suffixes=("_a", "_b"), how="outer")
    rows = []
    adjudicated = 0
    for _, row in merged.iterrows():
        la = str(row.get("label_a", "")).strip()
        lb = str(row.get("label_b", "")).strip()
        if la and lb and la == lb:
            label = la
        elif la and not lb:
            label = la
        elif lb and not la:
            label = lb
        else:
            label = ""
            adjudicated += 1
        event = row.get("event_month_a") or row.get("event_month_b") or ""
        if pd.isna(event):
            event = ""
        rows.append(
            {
                "cell_id": row["cell_id"],
                "row": int(row["row"]),
                "col": int(row["col"]),
                "label": label,
                "event_month": str(event).strip(),
                "consensus": bool(la and lb and la == lb),
                "needs_adjudication": bool((la and lb and la != lb) or (not la and not lb)),
            }
        )
    out = pd.DataFrame(rows)
    out = out[out["label"].str.strip() != ""]
    meta = {
        **report,
        "n_merged_labels": len(out),
        "n_needs_adjudication": int(out["needs_adjudication"].sum()),
        "min_kappa_threshold": min_kappa,
        "quality_ok": report.get("overall_kappa", 0) >= min_kappa if "overall_kappa" in report else False,
        "adjudicated_conflicts": adjudicated,
    }
    return out, meta


def simulate_rater_b_from_reference(
    reference: pd.DataFrame,
    agreement_rate: float = 0.85,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    out = reference.copy()
    if "event_month" not in out.columns:
        out["event_month"] = ""
    out["label_b"] = out["label"]
    n_flip = int(len(out) * (1 - agreement_rate))
    flip_idx = rng.choice(len(out), size=n_flip, replace=False)
    for idx in flip_idx:
        options = [c for c in LABEL_CLASSES if c != out.iloc[idx]["label"]]
        out.iloc[idx, out.columns.get_loc("label_b")] = rng.choice(options)
    out = out.rename(columns={"label": "label_a"})
    return out[["cell_id", "row", "col", "label_a", "label_b", "event_month"]]
