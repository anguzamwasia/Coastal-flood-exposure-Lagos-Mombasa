"""Write LISFLOOD-FP inputs for a scenario run.

Layout: models/lisflood_fp/<city>/inputs/<ssp>_<horizon>_rp<rp>/
"""

from __future__ import annotations

from pathlib import Path

from .. import config


def run_dir(city: str, ssp: str, horizon: int, rp: int) -> Path:
    return config.path("models") / "lisflood_fp" / city / "inputs" / f"{ssp}_{horizon}_rp{rp}"


def write_bdy(path: Path, name: str, times_s: list[float], levels_m: list[float]) -> Path:
    """Time-varying water-level boundary (HVAR) file."""
    lines = ["LISFLOOD-FP boundary", name, f"{len(times_s)}\tseconds"]
    lines += [f"{lv:.3f}\t{t:.0f}" for t, lv in zip(times_s, levels_m)]
    path.write_text("\n".join(lines) + "\n")
    return path


def write_par(
    city: str, ssp: str, horizon: int, rp: int, dem_file: str, bci_file: str, bdy_file: str,
    sim_time_s: int = 3 * 24 * 3600, manning: float = 0.035, save_int_s: int = 3600,
) -> Path:
    """Minimal ACC-solver parameter file; the max-depth output (*.max) feeds hazard tiers."""
    d = run_dir(city, ssp, horizon, rp)
    d.mkdir(parents=True, exist_ok=True)
    resroot = f"{city}_{ssp}_{horizon}_rp{rp}"
    out_dir = config.path("models") / "lisflood_fp" / city / "outputs" / resroot
    par = f"""DEMfile        {dem_file}
resroot        {resroot}
dirroot        {out_dir.as_posix()}
sim_time       {sim_time_s}
initial_tstep  1
massint        {save_int_s}
saveint        {save_int_s}
fpfric         {manning}
bcifile        {bci_file}
bdyfile        {bdy_file}
acceleration
elevoff
"""
    p = d / f"{resroot}.par"
    p.write_text(par)
    return p
