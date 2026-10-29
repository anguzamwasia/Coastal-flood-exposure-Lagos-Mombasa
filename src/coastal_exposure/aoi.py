"""Area-of-interest handling. Every layer is clipped to the city AOI."""

from __future__ import annotations

import geopandas as gpd

from . import config


def load_aoi(city: str, metric: bool = False) -> gpd.GeoDataFrame:
    """Read the city AOI (KML/GeoJSON/GPKG) as a single dissolved polygon."""
    cfg = config.load_city(city)
    aoi_path = config.ROOT / cfg["aoi"]
    if not aoi_path.exists():
        raise FileNotFoundError(
            f"AOI for {city} not found at {aoi_path}. Add the boundary file before running."
        )
    gdf = gpd.read_file(aoi_path)
    gdf = gdf.set_crs("EPSG:4326") if gdf.crs is None else gdf.to_crs("EPSG:4326")
    gdf = gdf[["geometry"]].dissolve().reset_index(drop=True)
    gdf["city"] = city
    return gdf.to_crs(cfg["crs_metric"]) if metric else gdf


def bbox(city: str) -> tuple[float, float, float, float]:
    """(lon_min, lat_min, lon_max, lat_max) of the AOI in EPSG:4326."""
    return tuple(load_aoi(city).total_bounds)


def area_km2(city: str) -> float:
    return float(load_aoi(city, metric=True).area.sum() / 1e6)
