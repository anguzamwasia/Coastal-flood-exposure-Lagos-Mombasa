"""Compare hard defences (seawalls) with biophysical buffers (mangroves, coral reefs).

Both are represented as modifications of the hydrodynamic inputs so the same exposure
workflow can be re-run per adaptation option:
  - seawall: raise DEM cells along a defence line to crest height
  - mangrove: increase Manning's n within the mangrove extent (wave/surge attenuation)
  - coral reef: reduce the offshore extreme water level by a wave-setup reduction
"""

from __future__ import annotations

import numpy as np

MANNING_MANGROVE = 0.14
MANNING_DEFAULT = 0.035


def apply_seawall(dem: np.ndarray, wall_mask: np.ndarray, crest_m: float) -> np.ndarray:
    return np.where(wall_mask, np.maximum(dem, crest_m), dem)


def manning_grid(shape: tuple[int, int], mangrove_mask: np.ndarray | None = None) -> np.ndarray:
    n = np.full(shape, MANNING_DEFAULT, dtype="float32")
    if mangrove_mask is not None:
        n[mangrove_mask] = MANNING_MANGROVE
    return n


def reef_attenuated_level(water_level_m: float, setup_reduction_m: float) -> float:
    return water_level_m - setup_reduction_m


def avoided_exposure(baseline: dict[str, float], option: dict[str, float]) -> dict[str, float]:
    """Exposure avoided per tier (positive = benefit) for a given adaptation option."""
    return {k: baseline[k] - option.get(k, 0.0) for k in baseline}
