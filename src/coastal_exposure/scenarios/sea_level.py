"""IPCC AR6 sea-level rise and scenario-adjusted terrain.

Expected AR6 table: data/external/ipcc_ar6_slr/<city>_ar6.csv with columns
    scenario, quantile, year, slr_m
(export from the NASA Sea Level Projection Tool for the nearest grid point / tide gauge;
values relative to the 1995-2014 baseline).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .. import config
from ..subsidence.insar import cumulative_subsidence_m


def load_ar6(city: str) -> pd.DataFrame:
    f = config.path("external") / "ipcc_ar6_slr" / f"{city}_ar6.csv"
    df = pd.read_csv(f)
    df["scenario"] = df["scenario"].str.lower().str.replace("-", "").str.replace(".", "")
    return df


def slr(city: str, ssp: str, horizon: int, quantile: float = 0.5) -> float:
    """Regional SLR (m) for scenario/horizon/quantile, interpolated linearly in time."""
    df = load_ar6(city)
    sel = df[(df.scenario == ssp) & np.isclose(df["quantile"], quantile)].sort_values("year")
    if sel.empty:
        raise KeyError(f"No AR6 data for {city} {ssp} q={quantile}")
    return float(np.interp(horizon, sel.year, sel.slr_m))


def relative_sea_level_dem(
    dem: np.ndarray,
    slr_m: float,
    subsidence_mm_yr: np.ndarray | float = 0.0,
    base_year: int | None = None,
    horizon: int = 2050,
) -> np.ndarray:
    """Terrain relative to future mean sea level.

    Future ground = DEM + cumulative vertical land motion (negative when subsiding);
    subtracting SLR expresses elevations relative to the raised sea surface, so any
    cell <= 0 sits below future mean sea level before surge/tide are added.
    """
    base_year = base_year or config.load_project()["baseline"]["reference_epoch"]
    vlm = cumulative_subsidence_m(np.asarray(subsidence_mm_yr, dtype=float), base_year, horizon)
    return dem + vlm - slr_m


def extreme_water_level(slr_m: float, surge_m: float, tide_m: float = 0.0) -> float:
    """Still water level boundary condition = SLR + storm surge + tide (MHWS / HAT)."""
    return slr_m + surge_m + tide_m
