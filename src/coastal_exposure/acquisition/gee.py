"""Google Earth Engine annual composites for each baseline epoch.

Requires `earthengine-api` and an authenticated account (`earthengine authenticate`).
"""

from __future__ import annotations

from .. import config
from ..aoi import load_aoi

LANDSAT_SCALE = 0.0000275
LANDSAT_OFFSET = -0.2


def _ee():
    import ee  # imported lazily so the rest of the package works without GEE

    ee.Initialize()
    return ee


def aoi_geometry(city: str):
    ee = _ee()
    return ee.Geometry(load_aoi(city).geometry.iloc[0].__geo_interface__)


def epoch_window(epoch: int) -> tuple[str, str]:
    """Date window centred on the epoch (default 12 months = calendar year)."""
    months = config.load_project()["baseline"]["composite_window_months"]
    if months == 12:
        return f"{epoch}-01-01", f"{epoch}-12-31"
    half = months // 2
    return f"{epoch - 1}-{12 - half + 1:02d}-01", f"{epoch}-{half:02d}-28"


def _mask_landsat(img):
    qa = img.select("QA_PIXEL")
    clear = qa.bitwiseAnd(0b11111).eq(0)  # fill, dilated cloud, cirrus, cloud, shadow
    optical = img.select("SR_B.").multiply(LANDSAT_SCALE).add(LANDSAT_OFFSET)
    return img.addBands(optical, None, True).updateMask(clear)


def landsat_composite(city: str, epoch: int):
    """Median cloud-masked Landsat composite using every sensor configured for the epoch."""
    ee = _ee()
    geom = aoi_geometry(city)
    start, end = epoch_window(epoch)
    ids = config.load_sources()["optical"]["landsat"]["gee_ids"]
    sensors = [s for s in config.load_project()["baseline"]["sensors"][epoch] if s in ids]
    col = None
    for s in sensors:
        c = ee.ImageCollection(ids[s]).filterBounds(geom).filterDate(start, end).map(_mask_landsat)
        col = c if col is None else col.merge(c)
    return col.median().clip(geom)


def sentinel2_composite(city: str, epoch: int, max_cloud: int = 30):
    ee = _ee()
    geom = aoi_geometry(city)
    start, end = epoch_window(epoch)
    col = (
        ee.ImageCollection(config.load_sources()["optical"]["sentinel2"]["gee_id"])
        .filterBounds(geom).filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud))
    )
    return col.median().divide(10000).clip(geom)


def export_to_drive(image, city: str, name: str, scale: int = 30, folder: str = "coastal_exposure"):
    """Start a Drive export task; download into data/raw/<city>/... afterwards."""
    ee = _ee()
    task = ee.batch.Export.image.toDrive(
        image=image, description=f"{city}_{name}", folder=folder,
        fileNamePrefix=f"{city}_{name}", region=aoi_geometry(city), scale=scale,
        crs=config.load_city(city)["crs_metric"], maxPixels=1e13,
    )
    task.start()
    return task
