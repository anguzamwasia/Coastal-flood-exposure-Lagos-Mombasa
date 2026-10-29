"""OpenStreetMap transport networks and civic facilities via OSMnx."""

from __future__ import annotations

import geopandas as gpd

from .. import config
from ..aoi import load_aoi

CIVIC_TAGS = {
    "amenity": ["hospital", "clinic", "school", "university", "police", "fire_station"],
    "aeroway": ["aerodrome"],
    "landuse": ["port", "industrial"],
    "power": ["plant", "substation"],
}


def fetch_roads(city: str) -> gpd.GeoDataFrame:
    import osmnx as ox

    poly = load_aoi(city).geometry.iloc[0]
    graph = ox.graph_from_polygon(poly, network_type="drive", simplify=True)
    edges = ox.graph_to_gdfs(graph, nodes=False)
    out = config.raw_dir(city, "osm") / "roads.gpkg"
    edges.reset_index()[["highway", "name", "length", "geometry"]].astype(
        {"highway": str, "name": str}
    ).to_file(out, driver="GPKG")
    return edges


def fetch_civic(city: str) -> gpd.GeoDataFrame:
    import osmnx as ox

    poly = load_aoi(city).geometry.iloc[0]
    feats = ox.features_from_polygon(poly, tags=CIVIC_TAGS)
    keep = [c for c in ["amenity", "aeroway", "landuse", "power", "name", "geometry"] if c in feats]
    feats = feats[keep].reset_index(drop=True)
    feats.to_file(config.raw_dir(city, "osm") / "civic.gpkg", driver="GPKG")
    return feats
