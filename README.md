# Coastal-flood-exposure-Lagos-Mombasa

**Divergent Coastal Vulnerability Under Accelerating Sea-Level Rise: A Comparative Inundation and
Critical Infrastructure Exposure Framework for Lagos and Mombasa**
- Mercy Akintola, Cynthia Anguza

Comparative compound-flood and critical-infrastructure exposure framework for Lagos and Mombasa.
Uses Sentinel-1 InSAR subsidence, IPCC AR6 SSP2-4.5/5-8.5 sea-level rise (2030/2050/2100), an
enhanced CVI, LISFLOOD-FP modelling on FABDEM, and GeoPandas/Rasterio exposure analysis with OSM,
building footprints and WorldPop.

| | Lagos (Nigeria) | Mombasa (Kenya) |
|---|---|---|
| Setting | Low-lying micro-tidal megacity, barrier-lagoon | Coralline macro-tidal island/estuary |
| AOI | `data/aoi/lagos/lagos_aoi.kml` (~2,009 km²) | *pending* → `data/aoi/mombasa/` |
| Metric CRS | EPSG:32631 (UTM 31N) | EPSG:32737 (UTM 37S) |
| Key corridor | Lekki-Epe Expressway | Makupa Causeway |

## Temporal design

**Historical baseline epochs:** `2000 · 2010 · 2020 · 2025` (2025 is the reference "present";
switch to 2026 in `config/project.yaml` once full-year 2026 composites exist).

| Epoch | Optical | SAR / InSAR | Population | Built-up |
|---|---|---|---|---|
| 2000 | Landsat 5/7 | – | WorldPop, GHS-POP | GHS-BUILT |
| 2010 | Landsat 5/7 | – | WorldPop, GHS-POP | GHS-BUILT |
| 2020 | Landsat 8, Sentinel-2 | Sentinel-1 | WorldPop, GHS-POP | GHS-BUILT, Open Buildings Temporal |
| 2025 | Landsat 8/9, Sentinel-2 | Sentinel-1 (InSAR 2015–2025) | WorldPop Global2, GHS-POP | Google Open Buildings v3, OSM |

**Future projections:** `SSP2-4.5`, `SSP5-8.5` × horizons `2030` (municipal response),
`2050` (infrastructure lifespan), `2100` (climate benchmark) × AR6 quantiles (17/50/83 %)
× surge return periods (1, 10, 100 yr). Relative sea level = AR6 SLR + InSAR vertical land motion.

**Hazard tiers (flood depth):** Nuisance 0.1–0.5 m · Moderate 0.5–1.0 m · Severe > 1.0 m.

## Repository layout

```
config/
  project.yaml            epochs, scenarios, horizons, hazard tiers, resolutions
  data_sources.yaml       catalogue of every dataset + which epochs it serves
  cities/{lagos,mombasa}.yaml   AOI path, CRS, tidal regime, corridors
data/                     (contents git-ignored except AOIs; folders kept with .gitkeep)
  aoi/{lagos,mombasa}/    study-area boundaries
  raw/<city>/             dem, optical/{landsat,sentinel2}, sar/sentinel1, insar,
                          population/{worldpop,ghsl}, buildings/{google_open_buildings,ghsl_built},
                          osm, landcover, coastline, tides_surge, mangroves_coral, admin_boundaries
  interim/<city>/         clipped / reprojected intermediates
  processed/<city>/
    baseline/{2000,2010,2020,2025}/       analysis-ready layers per epoch
    subsidence/                           InSAR vertical velocity (mm/yr)
    cvi/                                  coastal vulnerability index segments
    projections/{ssp245,ssp585}/{2030,2050,2100}/
        dem_adjusted/ flood_depth/ hazard_tiers/ exposure/
  external/               ipcc_ar6_slr, fabdem, gtsm_surge, tide_gauges
models/
  lisflood_fp/<city>/{inputs,outputs}/    one sub-folder per <ssp>_<horizon>_rp<rp>
  hec_ras/<city>/
src/coastal_exposure/     python package
  config.py  aoi.py
  acquisition/   gee.py (Landsat/S2 epoch composites), osm.py, population.py
  preprocessing/ raster.py (clip to AOI, reproject)
  subsidence/    insar.py (LOS→vertical, cumulative VLM)
  scenarios/     sea_level.py (AR6 SLR, relative-sea-level DEM, extreme water level)
  hydrodynamics/ bathtub.py (connected screening), lisflood.py (par/bdy writer)
  cvi/           index.py (enhanced CVI)
  exposure/      hazard.py (depth→tiers), metrics.py (population, floor area, network km)
  adaptation/    tradeoffs.py (seawall vs mangrove/coral)
  viz/           maps.py
scripts/                  numbered pipeline steps
notebooks/                exploration only
outputs/{figures,maps,tables}/{lagos,mombasa,comparative}/  outputs/reports/
docs/methodology.md
tests/
```

## Getting started

```bash
conda env create -f environment.yml
conda activate coastal-exposure
earthengine authenticate          # only for acquisition steps
python scripts/00_check_setup.py  # prints epochs, scenarios, AOI status
pytest
```

## Pipeline

| Step | Script | Output |
|---|---|---|
| 0 | `00_check_setup.py` | config / AOI sanity check |
| 1 | `01_acquire_baseline.py --city lagos` | `data/raw/<city>/…` per epoch |
| 2 | `02_build_scenarios.py --city lagos` | `projections/<ssp>/<horizon>/dem_adjusted/` |
| 3 | run LISFLOOD-FP (`hydrodynamics/lisflood.py` writes inputs) | `projections/…/flood_depth/` |
| 4 | `03_classify_and_expose.py --city lagos` | `hazard_tiers/`, `outputs/tables/<city>/` |

## Adding Mombasa

1. Save the boundary as `data/aoi/mombasa/mombasa_aoi.kml`.
2. Run `python scripts/00_check_setup.py` and copy the printed bbox into `config/cities/mombasa.yaml`.
3. Run the pipeline with `--city mombasa`.

## Data policy

Raw and processed geodata are **not** committed (see `.gitignore`); only AOIs, configs and code.
Document the provenance of every downloaded file in `config/data_sources.yaml`.
