"""Enhanced Coastal Vulnerability Index (Gornitz-style, extended with subsidence + exposure).

Each variable is ranked 1 (very low) - 5 (very high) per coastal segment, then
CVI = sqrt(product(ranks) / n).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# variable -> (bin edges, higher_is_more_vulnerable)
DEFAULT_RANKING = {
    "elevation_m": ([2, 5, 10, 20], False),
    "slope_pct": ([0.2, 0.5, 1.0, 2.0], False),
    "shoreline_change_m_yr": ([-2, -1, 1, 2], False),   # erosion (negative) = vulnerable
    "tidal_range_m": ([1, 2, 4, 6], False),             # micro-tidal more vulnerable to surge
    "wave_height_m": ([0.5, 1.0, 1.5, 2.0], True),
    "rslr_mm_yr": ([1.8, 2.5, 3.0, 3.4], True),
    "subsidence_mm_yr": ([1, 3, 5, 10], True),          # magnitude of downward VLM
    "geomorphology_rank": (None, True),                 # already ranked 1-5
    "buffer_rank": (None, True),                        # mangrove/coral absence, ranked 1-5
}


def rank(values: pd.Series, edges: list[float] | None, ascending: bool) -> pd.Series:
    if edges is None:
        return values.clip(1, 5).astype(int)
    r = np.digitize(values, edges) + 1  # 1..5
    return pd.Series(r if ascending else 6 - r, index=values.index)


def compute_cvi(segments: pd.DataFrame, ranking: dict = DEFAULT_RANKING) -> pd.DataFrame:
    """Add rank_<var> columns, `cvi` and `cvi_class` (quartiles) to a segments table."""
    out = segments.copy()
    used = [v for v in ranking if v in out]
    for v in used:
        edges, asc = ranking[v]
        out[f"rank_{v}"] = rank(out[v], edges, asc)
    ranks = out[[f"rank_{v}" for v in used]].to_numpy(dtype=float)
    out["cvi"] = np.sqrt(ranks.prod(axis=1) / len(used))
    out["cvi_class"] = pd.qcut(out["cvi"], 4, labels=["low", "moderate", "high", "very_high"],
                               duplicates="drop")
    return out
