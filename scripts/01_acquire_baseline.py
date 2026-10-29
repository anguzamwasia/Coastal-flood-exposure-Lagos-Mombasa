"""Acquire baseline layers for every epoch (2000, 2010, 2020, 2025).

Usage: python scripts/01_acquire_baseline.py --city lagos [--epochs 2000 2010]
"""

import argparse

from coastal_exposure import config
from coastal_exposure.acquisition import gee, population

p = argparse.ArgumentParser()
p.add_argument("--city", required=True)
p.add_argument("--epochs", nargs="*", type=int)
args = p.parse_args()

epochs = args.epochs or config.load_project()["baseline"]["epochs"]
for epoch in epochs:
    print(f"[{args.city} {epoch}] Landsat composite -> Drive export")
    gee.export_to_drive(gee.landsat_composite(args.city, epoch), args.city, f"landsat_{epoch}")
    if epoch >= 2016:
        print(f"[{args.city} {epoch}] Sentinel-2 composite -> Drive export")
        gee.export_to_drive(gee.sentinel2_composite(args.city, epoch), args.city,
                            f"sentinel2_{epoch}", scale=10)
    if epoch <= 2020:
        print(f"[{args.city} {epoch}] WorldPop")
        population.fetch_worldpop(args.city, epoch)
