from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from canopy.heat.exposure import exposure_reduction_from_canopy_gain, population_weighted_exposure


@dataclass(frozen=True)
class InterventionParams:
    reference_lst_celsius: float = 24.0
    cooling_per_canopy_unit: float = 2.0
    preserve_loss_avoidance_fraction: float = 0.8
    preserve_immediacy_factor: float = 1.0
    restore_canopy_gain: float = 0.25
    restore_immediacy_factor: float = 0.6
    plant_canopy_gain: float = 0.15
    plant_immediacy_factor: float = 0.35
    preserve_cost: float = 1.0
    restore_cost: float = 2.0
    plant_cost: float = 3.0
    preserve_water_m3: float = 5.0
    restore_water_m3: float = 15.0
    plant_water_m3: float = 25.0
    preserve_maturity_threshold: float = 0.6
    preserve_canopy_threshold: float = 0.4
    plantable_canopy_max: float = 0.35
    restorable_canopy_max: float = 0.55

    @classmethod
    def from_config(cls, cfg: dict[str, Any]) -> InterventionParams:
        opt = cfg.get("optimization", {})
        iv = cfg.get("intervention", {})
        preserve = iv.get("preserve", {})
        restore = iv.get("restore", {})
        plant = iv.get("plant", {})
        heat = cfg.get("heat", {})
        return cls(
            reference_lst_celsius=float(heat.get("lst_reference_celsius", 24.0)),
            cooling_per_canopy_unit=float(iv.get("cooling_per_canopy_unit", 2.0)),
            preserve_loss_avoidance_fraction=float(
                preserve.get("loss_avoidance_fraction", 0.8)
            ),
            preserve_immediacy_factor=float(preserve.get("immediacy_factor", 1.0)),
            restore_canopy_gain=float(restore.get("canopy_gain", 0.25)),
            restore_immediacy_factor=float(restore.get("immediacy_factor", 0.6)),
            plant_canopy_gain=float(plant.get("canopy_gain", 0.15)),
            plant_immediacy_factor=float(plant.get("immediacy_factor", 0.35)),
            preserve_cost=float(preserve.get("cost", opt.get("preserve_cost", 1.0))),
            restore_cost=float(restore.get("cost", opt.get("restore_cost", 2.0))),
            plant_cost=float(plant.get("cost", opt.get("plant_cost", 3.0))),
            preserve_water_m3=float(preserve.get("water_m3", opt.get("preserve_water", 5.0))),
            restore_water_m3=float(restore.get("water_m3", opt.get("restore_water", 15.0))),
            plant_water_m3=float(plant.get("water_m3", opt.get("plant_water", 25.0))),
            preserve_maturity_threshold=float(
                iv.get("preserve_maturity_threshold", opt.get("preserve_maturity_threshold", 0.6))
            ),
            preserve_canopy_threshold=float(iv.get("preserve_canopy_threshold", 0.4)),
            plantable_canopy_max=float(iv.get("plantable_canopy_max", 0.35)),
            restorable_canopy_max=float(iv.get("restorable_canopy_max", 0.55)),
        )


@dataclass
class InterventionCell:
    cell_id: int
    row: int
    col: int
    lst: float
    canopy: float
    population: float
    building_density: float
    maturity: float
    exposure: float
    water_feasible: bool = True
    plantable: bool = True
    preserve_candidate: bool = False
    restorable: bool = False


@dataclass
class InterventionOutcome:
    action: str
    feasible: bool
    exposure_before: float
    exposure_after: float
    exposure_reduction: float
    canopy_after: float
    lst_after: float
    cost: float
    water_m3: float
    benefit_per_cost: float
    note: str = ""


def _current_exposure(cell: InterventionCell, params: InterventionParams) -> float:
    return float(
        population_weighted_exposure(
            np.array([cell.lst]),
            np.array([cell.population]),
            params.reference_lst_celsius,
        )[0]
    )


def _canopy_action_reduction(
    cell: InterventionCell,
    canopy_gain: float,
    immediacy_factor: float,
    params: InterventionParams,
) -> float:
    effective_gain = canopy_gain * immediacy_factor
    return float(
        exposure_reduction_from_canopy_gain(
            np.array([cell.canopy]),
            np.array([effective_gain]),
            np.array([cell.lst]),
            np.array([cell.population]),
            cooling_per_canopy_unit=params.cooling_per_canopy_unit,
            reference_lst=params.reference_lst_celsius,
        )[0]
    )


def simulate_action(
    cell: InterventionCell,
    action: str,
    params: InterventionParams | None = None,
) -> InterventionOutcome:
    params = params or InterventionParams()
    before = _current_exposure(cell, params)

    if action == "none":
        return InterventionOutcome(
            action="none",
            feasible=True,
            exposure_before=before,
            exposure_after=before,
            exposure_reduction=0.0,
            canopy_after=cell.canopy,
            lst_after=cell.lst,
            cost=0.0,
            water_m3=0.0,
            benefit_per_cost=0.0,
            note="baseline",
        )

    if action == "preserve":
        feasible = cell.preserve_candidate
        if not feasible:
            return InterventionOutcome(
                action="preserve",
                feasible=False,
                exposure_before=before,
                exposure_after=before,
                exposure_reduction=0.0,
                canopy_after=cell.canopy,
                lst_after=cell.lst,
                cost=params.preserve_cost,
                water_m3=params.preserve_water_m3,
                benefit_per_cost=0.0,
                note="not_mature_or_canopy_too_low",
            )
        reduction = before * params.preserve_loss_avoidance_fraction * params.preserve_immediacy_factor
        after = max(before - reduction, 0.0)
        return InterventionOutcome(
            action="preserve",
            feasible=True,
            exposure_before=before,
            exposure_after=after,
            exposure_reduction=reduction,
            canopy_after=cell.canopy,
            lst_after=cell.lst,
            cost=params.preserve_cost,
            water_m3=params.preserve_water_m3,
            benefit_per_cost=reduction / max(params.preserve_cost, 1e-9),
            note="avoided_canopy_loss",
        )

    if action == "restore":
        feasible = cell.restorable and cell.water_feasible
        if not feasible:
            return InterventionOutcome(
                action="restore",
                feasible=False,
                exposure_before=before,
                exposure_after=before,
                exposure_reduction=0.0,
                canopy_after=cell.canopy,
                lst_after=cell.lst,
                cost=params.restore_cost,
                water_m3=params.restore_water_m3,
                benefit_per_cost=0.0,
                note="not_restorable_or_no_water",
            )
        reduction = _canopy_action_reduction(
            cell,
            params.restore_canopy_gain,
            params.restore_immediacy_factor,
            params,
        )
        cooling = (
            params.cooling_per_canopy_unit
            * params.restore_canopy_gain
            * params.restore_immediacy_factor
        )
        return InterventionOutcome(
            action="restore",
            feasible=True,
            exposure_before=before,
            exposure_after=max(before - reduction, 0.0),
            exposure_reduction=reduction,
            canopy_after=min(cell.canopy + params.restore_canopy_gain, 1.0),
            lst_after=max(cell.lst - cooling, 0.0),
            cost=params.restore_cost,
            water_m3=params.restore_water_m3,
            benefit_per_cost=reduction / max(params.restore_cost, 1e-9),
            note="canopy_restoration",
        )

    if action == "plant":
        feasible = cell.plantable and cell.water_feasible
        if not feasible:
            return InterventionOutcome(
                action="plant",
                feasible=False,
                exposure_before=before,
                exposure_after=before,
                exposure_reduction=0.0,
                canopy_after=cell.canopy,
                lst_after=cell.lst,
                cost=params.plant_cost,
                water_m3=params.plant_water_m3,
                benefit_per_cost=0.0,
                note="not_plantable_or_no_water",
            )
        reduction = _canopy_action_reduction(
            cell,
            params.plant_canopy_gain,
            params.plant_immediacy_factor,
            params,
        )
        cooling = (
            params.cooling_per_canopy_unit
            * params.plant_canopy_gain
            * params.plant_immediacy_factor
        )
        return InterventionOutcome(
            action="plant",
            feasible=True,
            exposure_before=before,
            exposure_after=max(before - reduction, 0.0),
            exposure_reduction=reduction,
            canopy_after=min(cell.canopy + params.plant_canopy_gain, 1.0),
            lst_after=max(cell.lst - cooling, 0.0),
            cost=params.plant_cost,
            water_m3=params.plant_water_m3,
            benefit_per_cost=reduction / max(params.plant_cost, 1e-9),
            note="new_planting",
        )

    raise ValueError(f"Unknown action: {action}")


def counterfactual_all_actions(
    cell: InterventionCell,
    params: InterventionParams | None = None,
) -> dict[str, InterventionOutcome]:
    params = params or InterventionParams()
    actions = ["none", "preserve", "restore", "plant"]
    return {action: simulate_action(cell, action, params) for action in actions}


def aggregate_action_outcomes(outcomes: list[InterventionOutcome]) -> dict[str, float]:
    feasible = [o for o in outcomes if o.feasible and o.action != "none"]
    if not feasible:
        return {
            "n_feasible": 0,
            "mean_exposure_reduction": float("nan"),
            "mean_benefit_per_cost": float("nan"),
        }
    reductions = np.array([o.exposure_reduction for o in feasible], dtype=float)
    bpc = np.array([o.benefit_per_cost for o in feasible], dtype=float)
    return {
        "n_feasible": len(feasible),
        "mean_exposure_reduction": float(np.mean(reductions)),
        "median_exposure_reduction": float(np.median(reductions)),
        "mean_benefit_per_cost": float(np.mean(bpc)),
        "median_benefit_per_cost": float(np.median(bpc)),
    }
