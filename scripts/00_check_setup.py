"""Print the configured epochs/scenarios and AOI status for each city."""

from coastal_exposure import aoi, config

proj = config.load_project()
print("Baseline epochs :", proj["baseline"]["epochs"])
print("Scenarios       :", config.scenario_grid())
for city in proj["project"]["cities"]:
    try:
        print(f"{city:8s} AOI area: {aoi.area_km2(city):,.1f} km2  bbox: {aoi.bbox(city)}")
    except FileNotFoundError as e:
        print(f"{city:8s} AOI missing -> {e}")
