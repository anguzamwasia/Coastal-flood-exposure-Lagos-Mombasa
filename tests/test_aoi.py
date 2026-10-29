from coastal_exposure import aoi


def test_lagos_aoi_loads():
    gdf = aoi.load_aoi("lagos")
    lon_min, lat_min, lon_max, lat_max = gdf.total_bounds
    assert 2.6 < lon_min < lon_max < 4.4 and 6.3 < lat_min < lat_max < 6.6
    assert aoi.area_km2("lagos") > 0
