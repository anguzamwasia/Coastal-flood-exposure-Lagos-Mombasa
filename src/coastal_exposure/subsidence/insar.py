"""Convert Sentinel-1 InSAR velocities to vertical land motion and project it forward."""

from __future__ import annotations

import numpy as np


def los_to_vertical(v_los: np.ndarray, incidence_deg: np.ndarray | float) -> np.ndarray:
    """Project line-of-sight velocity onto the vertical (assumes negligible horizontal motion)."""
    return v_los / np.cos(np.deg2rad(incidence_deg))


def cumulative_subsidence_m(
    velocity_mm_yr: np.ndarray, from_year: int, to_year: int, decay: float = 0.0
) -> np.ndarray:
    """Cumulative vertical displacement in metres between two years.

    Negative velocity = subsidence. With decay > 0 the rate decreases exponentially
    (rate * exp(-decay * t)), a simple way to represent consolidation slowing down.
    """
    dt = to_year - from_year
    if decay == 0:
        return velocity_mm_yr * dt / 1000.0
    return velocity_mm_yr * (1 - np.exp(-decay * dt)) / decay / 1000.0
