"""Standard map figures for hazard tiers and exposure."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap

TIER_COLORS = ["#ffffff00", "#fde725", "#f98e09", "#bc3754"]  # dry, nuisance, moderate, severe
TIER_LABELS = ["Dry / <0.1 m", "Nuisance 0.1-0.5 m", "Moderate 0.5-1.0 m", "Severe >1.0 m"]


def plot_hazard_tiers(tiers: np.ndarray, extent=None, title: str = "", ax=None):
    ax = ax or plt.subplots(figsize=(10, 6))[1]
    cmap = ListedColormap(TIER_COLORS)
    im = ax.imshow(tiers, cmap=cmap, norm=BoundaryNorm([0, 1, 2, 3, 4], cmap.N), extent=extent)
    cbar = plt.colorbar(im, ax=ax, ticks=[0.5, 1.5, 2.5, 3.5], shrink=0.7)
    cbar.ax.set_yticklabels(TIER_LABELS)
    ax.set_title(title)
    return ax
