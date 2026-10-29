"""WorldPop / GHSL population grids for each baseline epoch."""

from __future__ import annotations

from pathlib import Path

import requests

from .. import config

WORLDPOP_URL = (
    "https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/{year}/{ISO3}/"
    "{iso3}_ppp_{year}_constrained.tif"
)
WORLDPOP_UNCONSTRAINED_URL = (
    "https://data.worldpop.org/GIS/Population/Global_2000_2020/{year}/{ISO3}/{iso3}_ppp_{year}.tif"
)


def worldpop_url(city: str, year: int, constrained: bool = False) -> str:
    """Constrained grids exist from 2020; earlier epochs use the unconstrained series.

    For 2025 use the WorldPop Global2 (2015-2030) release or GHSL R2023A.
    """
    iso3 = config.load_city(city)["iso3"]
    tpl = WORLDPOP_URL if constrained and year >= 2020 else WORLDPOP_UNCONSTRAINED_URL
    return tpl.format(year=year, ISO3=iso3, iso3=iso3.lower())


def download(url: str, dst: Path, chunk: int = 1 << 20) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dst, "wb") as f:
            for block in r.iter_content(chunk):
                f.write(block)
    return dst


def fetch_worldpop(city: str, year: int) -> Path:
    url = worldpop_url(city, year, constrained=year >= 2020)
    return download(url, config.raw_dir(city, "population/worldpop") / Path(url).name)
