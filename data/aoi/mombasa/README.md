# Mombasa AOI

| Item | Value |
|---|---|
| File | `mombasa_aoi.geojson` |
| Extent | Mombasa County administrative boundary (incl. creek and harbour water) |
| Source | OpenStreetMap relation [3495554](https://www.openstreetmap.org/relation/3495554), via Nominatim |
| Licence | ODbL — © OpenStreetMap contributors |
| CRS | EPSG:4326 (reproject to EPSG:32737 for analysis) |
| Bbox | `[39.5631, -4.1548, 39.7643, -3.9227]` (lon_min, lat_min, lon_max, lat_max) |
| Area | ~289 km² (published planning area: 287.9 km²) |
| Retrieved | 2026-11-03 |

Referenced by `aoi:` in `config/cities/mombasa.yaml`.

## TODO
- Split land vs water area (compute water km² for the config)
- Add IEBC ward boundaries for exposure aggregation
