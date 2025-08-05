import sys
import os
import pandas as pd
import geopandas as gpd
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from fetch_osm import fetch_osm_data
from process_osm import parse_osm_json
from visualize import plot_with_stops, plot_profile_comparison_map
from profiles import profiles
from filter_by_profile import filter_by_profile
from parse_gtfs import load_gtfs, stops_to_geodf
from run_r5_routing import run_r5_for_profile

# Load GTFS data
gtfs_path = "r5_inputs/gtfs/gtfs-london.zip"
osm_pbf_path = "r5_inputs/osm/greater-london-latest.osm.pbf"
feed = load_gtfs(gtfs_path)
stops_gdf = stops_to_geodf(feed)

print("\n📍 GTFS Stops Loaded:", len(stops_gdf))
print(stops_gdf[["stop_id", "stop_name"]].head())

def calculate_metrics(gdf, filtered_gdf, profile_name):
    total = len(gdf)
    filtered = len(filtered_gdf)
    pct = round((filtered / total) * 100, 2) if total > 0 else 0
    print(f"\n📊 Metrics for '{profile_name}':")
    print(f"🔹 Total paths: {total}")
    print(f"🔹 Accessible paths: {filtered}")
    print(f"🔹 Coverage: {pct}%")
    try:
        length_km = filtered_gdf.to_crs(epsg=3857).length.sum() / 1000
        print(f"🔹 Approx. accessible path length: {round(length_km, 2)} km")
    except Exception as e:
        print("⚠️ Could not compute path length:", e)

def find_accessible_stops(filtered_paths_gdf, stops_gdf, distance_m=150):
    # Project to metric CRS for distance-based buffering
    filtered_paths_gdf = filtered_paths_gdf.to_crs(epsg=3857)
    stops_gdf_proj = stops_gdf.to_crs(epsg=3857)

    # Buffer the stops (not the paths)
    stops_buffered = stops_gdf_proj.copy()
    stops_buffered["geometry"] = stops_buffered.buffer(distance_m)

    # Check intersection
    intersection = gpd.sjoin(stops_buffered, filtered_paths_gdf, how="inner", predicate="intersects")

    # Return matched original stops
    reachable = stops_gdf_proj.loc[stops_gdf_proj.index.isin(intersection.index)].to_crs(epsg=4326)
    return reachable

# Fetch OSM data
bbox = (51.5072, -0.1276, 51.5090, -0.1240)
base_filters = {"highway": "footway"}
print("\n📡 Fetching OSM data...")
raw_osm_data = fetch_osm_data(bbox, base_filters)
gdf = parse_osm_json(raw_osm_data)
print(f"✅ Total OSM paths fetched: {len(gdf)}")
print("\n📦 Available tags in GeoDataFrame:")
print(gdf.columns.tolist())
print("\n🔍 surface values:")
print(gdf["surface"].value_counts(dropna=False))

# Store reachable stops
reachable_dict = {}

# Simulate per profile
for profile_name in profiles:
    print(f"\n🔧 Filtering for profile: {profile_name}")
    profile = profiles[profile_name]
    filtered_gdf = filter_by_profile(gdf.copy(), profile)
    calculate_metrics(gdf, filtered_gdf, profile_name)
    output_file = f"outputs/map_{profile_name}.html"

    reachable_stops = find_accessible_stops(filtered_gdf, stops_gdf)
    reachable_dict[profile_name] = reachable_stops

    plot_with_stops(filtered_gdf, stops_gdf, reachable_stops, output_file)
    print(f"🗺️  Map saved to: {output_file}")

    # R5 routing with dummy origins and destinations
    dummy = gpd.GeoDataFrame({"id": ["origin_1", "dest_1"]},
                             geometry=gpd.points_from_xy([-0.1277, -0.125], [51.5074, 51.508]),
                             crs="EPSG:4326")
    run_r5_for_profile(profile_name, dummy.iloc[[0]], dummy.iloc[[1]], osm_pbf_path, gtfs_path)

# Compare profiles if more than 1
if len(reachable_dict) >= 2:
    keys = list(reachable_dict.keys())
    ids_sets = {k: set(df["stop_id"]) for k, df in reachable_dict.items()}
    shared = set.intersection(*ids_sets.values())

    extras = {k: ids_sets[k] - shared for k in keys}

    stops_common = reachable_dict[keys[0]][reachable_dict[keys[0]]["stop_id"].isin(shared)]
    stops_common.to_file("outputs/stops_common.geojson", driver="GeoJSON")

    for k in keys:
        extra_stops = reachable_dict[k][reachable_dict[k]["stop_id"].isin(extras[k])]
        extra_stops.to_file(f"outputs/stops_only_{k}.geojson", driver="GeoJSON")

    # Final CSV for comparison
    df_compare = []

    # Shared
    df_common = stops_common[["stop_id", "stop_name"]].copy()
    df_common["category"] = "shared"
    for k in keys:
        df_common[f"{k}_accessible"] = True
    df_compare.append(df_common)

    # Exclusives
    for k in keys:
        exclusive = reachable_dict[k][reachable_dict[k]["stop_id"].isin(extras[k])]
        d = exclusive[["stop_id", "stop_name"]].copy()
        d["category"] = f"only_{k}"
        for key in keys:
            d[f"{key}_accessible"] = (key == k)
        df_compare.append(d)

    pd.concat(df_compare).drop_duplicates().to_csv("outputs/accessibility_stop_comparison.csv", index=False)
    print("\n📄 Accessibility comparison table saved to: outputs/accessibility_stop_comparison.csv")