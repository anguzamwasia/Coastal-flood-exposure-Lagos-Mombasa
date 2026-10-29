"""Hydrologically-connected 'bathtub' inundation - fast screening before LISFLOOD-FP runs."""

from __future__ import annotations

import numpy as np
from scipy import ndimage


def connected_inundation(dem: np.ndarray, water_level_m: float, sea_mask: np.ndarray) -> np.ndarray:
    """Flood depth (m) for cells below water_level that connect (8-neighbour) to the sea."""
    below = np.isfinite(dem) & (dem < water_level_m)
    labels, _ = ndimage.label(below | sea_mask, structure=np.ones((3, 3)))
    connected = np.isin(labels, np.unique(labels[sea_mask & (labels > 0)]))
    depth = np.where(connected & below & ~sea_mask, water_level_m - dem, 0.0)
    return depth.astype("float32")
