# Methodology overview

## 1. Study areas
- **Lagos** – AOI `data/aoi/lagos/lagos_aoi.kml` (lon 2.70–4.35 E, lat 6.37–6.55 N, ~2,009 km²).
- **Mombasa** – AOI pending.

All layers are clipped to the AOI and reprojected to the city UTM zone before analysis.

## 2. Historical baseline (2000, 2010, 2020, 2025)
For each epoch build an analysis-ready stack in `data/processed/<city>/baseline/<epoch>/`:

| Layer | File | Notes |
|---|---|---|
| Bare-earth DEM | `dem.tif` | FABDEM (static, ~2011–2015 acquisition) used for all epochs |
| Annual optical composite | `landsat.tif`, `sentinel2.tif` | cloud-masked median; S2 only 2020/2025 |
| Land cover / water mask | `landcover.tif`, `water.tif` | NDWI/MNDWI from composites; Dynamic World 2020+ |
| Shoreline | `shoreline.gpkg` | extracted from water mask → shoreline change rates for CVI |
| Population | `population.tif` | WorldPop / GHS-POP at 100 m |
| Built-up | `built.tif`, `buildings.gpkg` | GHS-BUILT for 2000/2010; Open Buildings for 2020/2025 |
| Mangrove extent | `mangroves.gpkg` | GMW (to 2020), classified for 2025 |

The baseline series quantifies urban expansion into low-lying land, shoreline change and
mangrove loss — the drivers behind current exposure.

## 3. Subsidence (Sentinel-1 InSAR, 2015–2025)
LOS velocities → vertical (`subsidence/insar.py`), stored at
`data/processed/<city>/subsidence/vertical_velocity_mm_yr.tif`. Projected forward linearly
(or with exponential decay) from the 2025 reference epoch.

## 4. Enhanced CVI
Gornitz-type index extended with subsidence and biophysical-buffer variables
(`cvi/index.py`), computed per coastal segment.

## 5. Future scenarios
For each SSP (2-4.5, 5-8.5) × horizon (2030, 2050, 2100) × AR6 quantile:

```
DEM_future = DEM_2025 + VLM(2025→horizon) − SLR(ssp, horizon, q)
Boundary water level = SLR + surge(RP) + tide
```

Bathtub screening (`hydrodynamics/bathtub.py`) followed by LISFLOOD-FP (or HEC-RAS 2D) for compound
flooding. Max-depth rasters go to `projections/<ssp>/<horizon>/flood_depth/`.

## 6. Hazard tiers & exposure
Depth → Nuisance (0.1–0.5 m), Moderate (0.5–1.0 m), Severe (> 1.0 m). Exposure metrics:
- ward-level population per tier (WorldPop / GHSL),
- inundated floor area by residential / commercial / industrial / civic class (Open Buildings + OSM),
- submerged km of critical corridors (Lekki-Epe Expressway, Makupa Causeway) and civic assets.

## 7. Adaptation trade-offs
Re-run scenarios with a seawall (raised DEM crest), mangrove roughness (Manning's n) and reef
attenuation (reduced boundary level); report avoided exposure per tier.
