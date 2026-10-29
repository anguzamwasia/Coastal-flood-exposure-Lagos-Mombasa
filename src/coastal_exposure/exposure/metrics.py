"""Exposure metrics: population, building floor area, and submerged network length."""

from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import shapes
from rasterstats import zonal_stats
from shapely.geometry import shape

from .hazard import TIER_CODES


def population_by_tier(pop: np.ndarray, tiers: np.ndarray) -> dict[str, float]:
    """Total population per hazard tier (pop and tiers on the same grid)."""
    pop = np.nan_to_num(pop, nan=0.0)
    return {name: float(pop[tiers == code].sum()) for name, code in TIER_CODES.items()}


def population_by_ward(pop_path, tier_path, wards: gpd.GeoDataFrame, ward_col: str) -> pd.DataFrame:
    """Ward-level exposed population for each hazard tier."""
    with rasterio.open(pop_path) as p, rasterio.open(tier_path) as t:
        pop, tiers = p.read(1, masked=True).filled(0), t.read(1)
        affine, crs = p.transform, p.crs
    wards = wards.to_crs(crs)
    rows = {}
    for name, code in TIER_CODES.items():
        layer = np.where(tiers == code, pop, 0.0)
        stats = zonal_stats(wards, layer, affine=affine, stats=["sum"], nodata=-1)
        rows[f"pop_{name}"] = [s["sum"] or 0.0 for s in stats]
    out = pd.DataFrame(rows, index=wards[ward_col])
    out["pop_exposed_total"] = out.sum(axis=1)
    return out


def buildings_by_tier(
    buildings: gpd.GeoDataFrame, tier_path, class_col: str = "class", storeys_col: str | None = None
) -> pd.DataFrame:
    """Inundated floor area (m2) by building class and hazard tier, sampled at footprint centroids."""
    with rasterio.open(tier_path) as src:
        b = buildings.to_crs(src.crs)
        pts = [(g.x, g.y) for g in b.geometry.centroid]
        b["tier"] = [v[0] for v in src.sample(pts)]
    storeys = b[storeys_col] if storeys_col else 1
    b["floor_area_m2"] = b.geometry.area * storeys
    inv = {v: k for k, v in TIER_CODES.items()}
    b = b[b.tier.isin(inv)].assign(tier=lambda d: d.tier.map(inv))
    return b.pivot_table(index=class_col, columns="tier", values="floor_area_m2", aggfunc="sum",
                         fill_value=0.0)


def network_km_by_tier(lines: gpd.GeoDataFrame, tier_path) -> dict[str, float]:
    """Kilometres of a line network (e.g. Lekki-Epe Expressway) inside each hazard tier."""
    with rasterio.open(tier_path) as src:
        tiers, transform, crs = src.read(1), src.transform, src.crs
    lines = lines.to_crs(crs)
    out = {}
    for name, code in TIER_CODES.items():
        hit = tiers == code
        polys = [shape(s) for s, _ in shapes(hit.astype("uint8"), mask=hit, transform=transform)]
        if not polys:
            out[name] = 0.0
            continue
        zone = gpd.GeoSeries(polys, crs=crs).union_all()
        out[name] = float(lines.clip(zone).length.sum() / 1000)
    return out
