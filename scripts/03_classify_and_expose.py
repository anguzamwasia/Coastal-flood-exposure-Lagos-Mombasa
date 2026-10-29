"""Classify flood-depth rasters into hazard tiers and compute exposure tables.

Expects: data/processed/<city>/projections/<ssp>/<horizon>/flood_depth/*.tif
"""

import argparse

import pandas as pd
import rasterio

from coastal_exposure import config
from coastal_exposure.exposure.hazard import classify_depth, tier_areas_km2

p = argparse.ArgumentParser()
p.add_argument("--city", required=True)
args = p.parse_args()

rows = []
for ssp, horizon in config.scenario_grid():
    for depth_path in sorted(config.projection_dir(args.city, ssp, horizon, "flood_depth").glob("*.tif")):
        with rasterio.open(depth_path) as src:
            depth, meta = src.read(1), src.meta | {"dtype": "uint8", "nodata": 255}
            px = abs(src.transform.a * src.transform.e)
        tiers = classify_depth(depth)
        dst = config.projection_dir(args.city, ssp, horizon, "hazard_tiers") / depth_path.name
        with rasterio.open(dst, "w", **meta) as f:
            f.write(tiers, 1)
        rows.append({"ssp": ssp, "horizon": horizon, "run": depth_path.stem,
                     **{f"{k}_km2": v for k, v in tier_areas_km2(tiers, px).items()}})

out = config.path("outputs") / "tables" / args.city / "hazard_area_summary.csv"
pd.DataFrame(rows).to_csv(out, index=False)
print(f"wrote {out}")
