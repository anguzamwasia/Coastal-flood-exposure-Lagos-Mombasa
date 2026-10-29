"""Classify flood depth into operational hazard tiers."""

from __future__ import annotations

import numpy as np

from .. import config

# raster codes
DRY, NUISANCE, MODERATE, SEVERE = 0, 1, 2, 3
TIER_CODES = {"nuisance": NUISANCE, "moderate": MODERATE, "severe": SEVERE}


def classify_depth(depth: np.ndarray, tiers: dict | None = None) -> np.ndarray:
    """0 = dry/<0.1 m, 1 = Nuisance 0.1-0.5, 2 = Moderate 0.5-1.0, 3 = Severe >1.0 m."""
    tiers = tiers or config.load_project()["hazard_tiers"]
    out = np.full(depth.shape, DRY, dtype="uint8")
    for name, (lo, hi) in tiers.items():
        out[(depth >= lo) & (depth < hi)] = TIER_CODES[name]
    return out


def tier_areas_km2(tiers: np.ndarray, pixel_area_m2: float) -> dict[str, float]:
    return {
        name: float((tiers == code).sum() * pixel_area_m2 / 1e6) for name, code in TIER_CODES.items()
    }
