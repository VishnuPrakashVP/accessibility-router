# run_r5_routing.py
from r5py import TransportNetwork, TravelTimeMatrixComputer
from datetime import datetime


def run_r5_for_profile(profile_name, origins, destinations, osm_pbf, gtfs_zip):
    print(f"\n🚦 Running R5 routing for: {profile_name}")

    tn = TransportNetwork(
        osm_pbf=osm_pbf,
        gtfs=gtfs_zip
    )


    ttm = TravelTimeMatrixComputer(
        transport_network=tn,
        origins=origins,
        destinations=destinations,
        departure=datetime(2023, 7, 1, 8, 0, 0),
        transport_modes=["WALK", "TRANSIT"]
    )

    result = ttm.compute_travel_times()
    result.to_csv(f"outputs/travel_times_{profile_name}.csv", index=False)
    print(f"📄 Saved travel times for {profile_name} to outputs/travel_times_{profile_name}.csv")
    return result