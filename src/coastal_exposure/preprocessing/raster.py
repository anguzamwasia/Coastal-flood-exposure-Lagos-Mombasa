"""Clip / reproject rasters to the AOI on a common grid."""

from __future__ import annotations

from pathlib import Path

import rasterio
from rasterio.mask import mask
from rasterio.warp import Resampling, calculate_default_transform, reproject

from ..aoi import load_aoi


def clip_to_aoi(src_path: Path, dst_path: Path, city: str) -> Path:
    """Clip a raster to the city AOI (keeps source CRS)."""
    with rasterio.open(src_path) as src:
        geoms = load_aoi(city).to_crs(src.crs).geometry
        data, transform = mask(src, geoms, crop=True)
        meta = src.meta | {"height": data.shape[1], "width": data.shape[2], "transform": transform}
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(dst_path, "w", **meta) as dst:
        dst.write(data)
    return dst_path


def reproject_raster(
    src_path: Path, dst_path: Path, dst_crs: str, res: float | None = None,
    resampling: Resampling = Resampling.bilinear,
) -> Path:
    """Reproject a raster to dst_crs (e.g. the city's UTM zone) at an optional resolution."""
    with rasterio.open(src_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds, resolution=res
        )
        meta = src.meta | {"crs": dst_crs, "transform": transform, "width": width, "height": height}
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(dst_path, "w", **meta) as dst:
            for b in range(1, src.count + 1):
                reproject(
                    rasterio.band(src, b), rasterio.band(dst, b),
                    src_transform=src.transform, src_crs=src.crs,
                    dst_transform=transform, dst_crs=dst_crs, resampling=resampling,
                )
    return dst_path
