import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from fetch_osm import fetch_osm_data
from process_osm import parse_osm_json
from visualize import plot_with_stops
from profiles import profiles
from filter_by_profile import filter_by_profile

from src.parse_gtfs import load_gtfs, stops_to_geodf

#loading gtfs data
gtfs_path = "data/gtfs-london.zip"
feed = load_gtfs(gtfs_path)

stops_gdf = stops_to_geodf(feed)

print("📍 GTFS Stops Loaded:", len(stops_gdf))
print(stops_gdf[["stop_id", "stop_name"]].head())


def calculate_metrics(gdf, filtered_gdf, profile_name):
    total = len(gdf)
    filtered = len(filtered_gdf)
    pct = round((filtered / total) * 100, 2) if total > 0 else 0

    print(f"\n📊 Metrics for '{profile_name}':")
    print(f"🔹 Total paths: {total}")
    print(f"🔹 Accessible paths: {filtered}")
    print(f"🔹 Coverage: {pct}%")

    # Optional: estimate length if geometries are valid
    try:
        length_km = filtered_gdf.to_crs(epsg=3857).length.sum() / 1000
        print(f"🔹 Approx. accessible path length: {round(length_km, 2)} km")
    except Exception as e:
        print("⚠️ Could not compute path length:", e)


def find_accessible_stops(filtered_paths_gdf, stops_gdf, distance_m=150):
    import geopandas as gpd

    paths_proj = filtered_paths_gdf.to_crs(epsg=3857)
    stops_proj = stops_gdf.to_crs(epsg=3857)

 
    buffer_gdf = gpd.GeoDataFrame(geometry=paths_proj.buffer(distance_m), crs=paths_proj.crs)

    matched = gpd.sjoin(stops_proj, buffer_gdf, how="inner", predicate="intersects")


    return matched.to_crs(epsg=4326)

bbox = (51.5072, -0.1276, 51.5090, -0.1240)  
base_filters = {"highway": "footway"}


print("📡 Fetching OSM data...")
raw_osm_data = fetch_osm_data(bbox, base_filters)
gdf = parse_osm_json(raw_osm_data)
print(f"✅ Total OSM paths fetched: {len(gdf)}\n")


print("📦 Available tags in GeoDataFrame:")
print(gdf.columns.tolist())
print("\n🔍 surface values:")
print(gdf["surface"].value_counts(dropna=False))
if "wheelchair" in gdf.columns:
    print("\n🔍 wheelchair values:")
    print(gdf["wheelchair"].value_counts(dropna=False))
if "incline" in gdf.columns:
    print("\n🔍 incline values:")
    print(gdf["incline"].value_counts(dropna=False))


for profile_name in ["wheelchair", "elderly"]:
    print(f"\n🔧 Filtering for profile: {profile_name}")
    profile = profiles[profile_name]
    filtered_gdf = filter_by_profile(gdf.copy(), profile)

    calculate_metrics(gdf, filtered_gdf, profile_name)

    output_file = f"outputs/map_{profile_name}.html"

    reachable_stops = find_accessible_stops(filtered_gdf, stops_gdf)
    print(f"✅ GTFS stops reachable by '{profile_name}': {len(reachable_stops)}")

    plot_with_stops(filtered_gdf, stops_gdf, reachable_stops, output_file)
    print(f"🗺️  Map saved to: {output_file}")