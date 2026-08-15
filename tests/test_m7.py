import numpy as np
import pytest

from canopy.heat.evaluation import (
    compute_exposure_surfaces,
    population_scale_sensitivity,
    spatial_pearson,
    top_k_jaccard,
)
from canopy.heat.exposure import population_weighted_exposure, total_exposure
from canopy.heat.layers import derive_pilot_heat_layers, mean_canopy_from_stack


def _grid():
    rng = np.random.default_rng(0)
    canopy = rng.uniform(0.1, 0.8, size=(20, 20))
    layers = derive_pilot_heat_layers(canopy, seed=0)
    return canopy, layers


def test_mean_canopy_from_stack():
    cube = np.linspace(0.2, 0.8, 60).reshape(3, 4, 5)
    mean = mean_canopy_from_stack(cube)
    assert mean.shape == (4, 5)
    assert np.all(mean >= 0.2)


def test_derive_pilot_layers_shapes():
    canopy = np.full((10, 12), 0.5)
    layers = derive_pilot_heat_layers(canopy, seed=1)
    assert layers["lst"].shape == canopy.shape
    assert layers["population"].shape == canopy.shape
    assert layers["building_density"].shape == canopy.shape


def test_population_weighted_exposure():
    lst = np.array([30.0, 26.0, 20.0])
    pop = np.array([100.0, 50.0, 10.0])
    out = population_weighted_exposure(lst, pop, reference_lst=24.0)
    assert out[0] == pytest.approx(600.0)
    assert out[2] == pytest.approx(0.0)


def test_compute_exposure_surfaces():
    canopy, layers = _grid()
    surfaces = compute_exposure_surfaces(
        layers["lst"],
        layers["population"],
        canopy,
        layers["building_density"],
    )
    assert set(surfaces) == {
        "raw_lst",
        "lst_x_population",
        "downscaled_lst_proxy",
        "population_weighted_exposure",
    }
    assert np.isfinite(surfaces["population_weighted_exposure"]).all()


def test_top_k_jaccard_differs_for_pop_weighting():
    canopy, layers = _grid()
    surfaces = compute_exposure_surfaces(
        layers["lst"],
        layers["population"],
        canopy,
        layers["building_density"],
    )
    j = top_k_jaccard(surfaces["raw_lst"], surfaces["population_weighted_exposure"], k=20)
    assert 0.0 <= j <= 1.0
    assert j < 1.0


def test_spatial_pearson_identity():
    x = np.arange(10, dtype=float)
    assert spatial_pearson(x, x) == pytest.approx(1.0)


def test_population_scale_sensitivity():
    canopy, layers = _grid()
    out = population_scale_sensitivity(
        layers["lst"],
        layers["population"],
        canopy,
        layers["building_density"],
        scales=[0.5, 1.0, 2.0],
        top_k=10,
    )
    assert len(out["scales"]) == 3
    assert out["scales"][1]["scale"] == pytest.approx(1.0)
    assert out["scales"][1]["top_k_jaccard_vs_base"] == pytest.approx(1.0)


def test_total_exposure():
    surface = np.array([1.0, 2.0, np.nan])
    assert total_exposure(surface) == pytest.approx(3.0)
