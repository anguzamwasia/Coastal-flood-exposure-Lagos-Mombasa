"""Build scenario-adjusted DEMs (SLR + subsidence) for every SSP x horizon x quantile.

Inputs : data/processed/<city>/baseline/<ref_epoch>/dem.tif
         data/processed/<city>/subsidence/vertical_velocity_mm_yr.tif (optional)
         data/external/ipcc_ar6_slr/<city>_ar6.csv
Output : data/processed/<city>/projections/<ssp>/<horizon>/dem_adjusted/dem_rsl_q<q>.tif
"""

import argparse

import numpy as np
import rasterio

from coastal_exposure import config
from coastal_exposure.scenarios.sea_level import relative_sea_level_dem, slr

p = argparse.ArgumentParser()
p.add_argument("--city", required=True)
args = p.parse_args()

proj = config.load_project()
ref = proj["baseline"]["reference_epoch"]
dem_path = config.baseline_dir(args.city, ref) / "dem.tif"
vlm_path = config.path("processed") / args.city / "subsidence" / "vertical_velocity_mm_yr.tif"

with rasterio.open(dem_path) as src:
    dem, meta = src.read(1).astype("float32"), src.meta | {"dtype": "float32"}
vlm = 0.0
if proj["scenarios"]["include_subsidence"] and vlm_path.exists():
    with rasterio.open(vlm_path) as src:
        vlm = src.read(1).astype("float32")

for ssp, horizon in config.scenario_grid():
    for q in proj["scenarios"]["slr_quantiles"]:
        rise = slr(args.city, ssp, horizon, q)
        out = relative_sea_level_dem(dem, rise, vlm, ref, horizon)
        dst = config.projection_dir(args.city, ssp, horizon, "dem_adjusted") / f"dem_rsl_q{int(q*100)}.tif"
        dst.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(dst, "w", **meta) as f:
            f.write(np.asarray(out, dtype="float32"), 1)
        print(f"{ssp} {horizon} q{q}: SLR={rise:.2f} m -> {dst.relative_to(config.ROOT)}")
