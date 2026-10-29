import numpy as np
import pandas as pd

from coastal_exposure import config
from coastal_exposure.cvi.index import compute_cvi
from coastal_exposure.exposure.hazard import classify_depth, tier_areas_km2
from coastal_exposure.hydrodynamics.bathtub import connected_inundation
from coastal_exposure.scenarios.sea_level import relative_sea_level_dem
from coastal_exposure.subsidence.insar import cumulative_subsidence_m


def test_config_epochs_and_scenarios():
    proj = config.load_project()
    assert proj["baseline"]["epochs"] == [2000, 2010, 2020, 2025]
    assert len(config.scenario_grid()) == 6
    assert config.baseline_dir("lagos", 2010).parts[-3:] == ("lagos", "baseline", "2010")


def test_hazard_tiers():
    depth = np.array([0.05, 0.2, 0.7, 1.5])
    assert classify_depth(depth).tolist() == [0, 1, 2, 3]
    assert tier_areas_km2(classify_depth(depth), 1e6)["severe"] == 1.0


def test_relative_sea_level_dem():
    dem = np.array([1.0, 2.0])
    out = relative_sea_level_dem(dem, slr_m=0.5, subsidence_mm_yr=-10, base_year=2025, horizon=2050)
    np.testing.assert_allclose(out, dem - 0.25 - 0.5)
    assert cumulative_subsidence_m(np.array(-10.0), 2025, 2035) == -0.1


def test_bathtub_connectivity():
    dem = np.array([[0, 0.5, 3, 0.2]], dtype=float)
    sea = np.array([[True, False, False, False]])
    depth = connected_inundation(dem, 1.0, sea)
    assert depth[0, 1] == 0.5 and depth[0, 3] == 0  # isolated depression stays dry


def test_cvi():
    seg = pd.DataFrame({"elevation_m": [1, 30], "subsidence_mm_yr": [12, 0.5],
                        "slope_pct": [0.1, 3], "wave_height_m": [2.5, 0.3]})
    out = compute_cvi(seg)
    assert out.cvi.iloc[0] > out.cvi.iloc[1]
