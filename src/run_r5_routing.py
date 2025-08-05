# run_r5_routing.py
import os
import pandas as pd
import shutil
import zipfile
from r5py import TransportNetwork, TravelTimeMatrixComputer
from datetime import datetime



def filter_gtfs_for_profile(gtfs_zip_path, profile_name):
    compare_df = pd.read_csv("outputs/accessibility_stop_comparison.csv")
    accessible_stops = compare_df[compare_df[f"{profile_name}_accessible"] == True]["stop_id"].tolist()

    # Step 1: Unzip GTFS zip to temp folder
    temp_extract_dir = f"temp_extracted_gtfs_{profile_name}"
    if os.path.exists(temp_extract_dir):
        shutil.rmtree(temp_extract_dir)
    os.makedirs(temp_extract_dir, exist_ok=True)
    with zipfile.ZipFile(gtfs_zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_dir)

    # Step 2: Copy and filter stops
    stops_file = os.path.join(temp_extract_dir, "stops.txt")
    stops_df = pd.read_csv(stops_file)
    stops_df = stops_df[stops_df["stop_id"].isin(accessible_stops)]
    stops_df.to_csv(stops_file, index=False)

    # Step 2.1: Also filter stop_times.txt based on remaining stop_ids
    stop_times_file = os.path.join(temp_extract_dir, "stop_times.txt")
    if os.path.exists(stop_times_file):
        stop_times_df = pd.read_csv(stop_times_file)
        stop_times_df = stop_times_df[stop_times_df["stop_id"].isin(stops_df["stop_id"])]
        stop_times_df.to_csv(stop_times_file, index=False)

    # Step 3: Re-zip
    filtered_zip_path = f"temp_gtfs_{profile_name}.zip"
    with zipfile.ZipFile(filtered_zip_path, "w") as zipf:
        for root, _, files in os.walk(temp_extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_extract_dir)
                zipf.write(file_path, arcname)

    return filtered_zip_path


def run_r5_for_profile(profile_name, origins, destinations, osm_pbf, gtfs_folder):
    print(f"\n🚦 Running R5 routing for: {profile_name}")

    walk_speeds = {
        "normal": 1.4,       # meters/second
        "wheelchair": 0.9,
        "elderly": 0.8
    }

    filtered_gtfs_zip = filter_gtfs_for_profile(gtfs_folder, profile_name)

    tn = TransportNetwork(
        osm_pbf=osm_pbf,
        gtfs=filtered_gtfs_zip
    )

    ttm = TravelTimeMatrixComputer(
        transport_network=tn,
        origins=origins,
        destinations=destinations,
        departure=datetime(2023, 7, 1, 8, 0, 0),
        transport_modes=["WALK", "TRANSIT"]
    )

    result = ttm.compute_travel_times()
    default_speed = 1.4  # R5 default walking speed in m/s
    actual_speed = walk_speeds.get(profile_name, default_speed)
    adjustment_factor = default_speed / actual_speed
    result["adjusted_travel_time"] = (result["travel_time"] * adjustment_factor).round(2)
    result.to_csv(f"outputs/travel_times_{profile_name}.csv", index=False)
    print(f"📄 Saved travel times for {profile_name} to outputs/travel_times_{profile_name}.csv")
    return result