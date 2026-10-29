"""Load project / city configuration and resolve the standard directory layout."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"


@lru_cache
def load_project() -> dict:
    with open(CONFIG_DIR / "project.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def load_city(city: str) -> dict:
    path = CONFIG_DIR / "cities" / f"{city.lower()}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"No city config at {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def load_sources() -> dict:
    with open(CONFIG_DIR / "data_sources.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def path(key: str) -> Path:
    """Absolute path for a key in project.yaml `paths` (e.g. 'raw', 'processed')."""
    return ROOT / load_project()["paths"][key]


def raw_dir(city: str, layer: str) -> Path:
    return path("raw") / city / layer


def baseline_dir(city: str, epoch: int) -> Path:
    epochs = load_project()["baseline"]["epochs"]
    if epoch not in epochs:
        raise ValueError(f"Epoch {epoch} not in configured baseline epochs {epochs}")
    return path("processed") / city / "baseline" / str(epoch)


def projection_dir(city: str, ssp: str, horizon: int, product: str | None = None) -> Path:
    """data/processed/<city>/projections/<ssp>/<horizon>/[<product>]

    product: dem_adjusted | flood_depth | hazard_tiers | exposure
    """
    d = path("processed") / city / "projections" / ssp / str(horizon)
    return d / product if product else d


def scenario_grid() -> list[tuple[str, int]]:
    """All (ssp, horizon) combinations to run."""
    sc = load_project()["scenarios"]
    return [(s, h) for s in sc["ssp"] for h in sc["horizons"]]
