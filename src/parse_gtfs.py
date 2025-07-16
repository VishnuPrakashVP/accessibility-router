import gtfs_kit as gk
import geopandas as gpd
from shapely.geometry import Point
import os

def load_gtfs(gtfs_path):
    abs_path = os.path.abspath(gtfs_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"GTFS file not found: {abs_path}")
    feed = gk.read_feed(abs_path, dist_units="km")
    return feed

def stops_to_geodf(feed):
    stops = feed.stops
    geometry = [Point(xy) for xy in zip(stops.stop_lon, stops.stop_lat)]
    return gpd.GeoDataFrame(stops, geometry=geometry, crs="EPSG:4326")