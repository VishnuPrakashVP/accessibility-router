import folium


def plot_with_stops(gdf, stops_gdf, reachable_stops, output_file):
    import folium
    m = folium.Map(location=[gdf.geometry.unary_union.centroid.y, gdf.geometry.unary_union.centroid.x], zoom_start=15)

    folium.GeoJson(gdf).add_to(m)

    for _, row in stops_gdf.iterrows():
        folium.CircleMarker(
            location=[row['stop_lat'], row['stop_lon']],
            radius=2,
            color='red',
            fill=True,
            fill_opacity=0.8
        ).add_to(m)


    for _, row in reachable_stops.iterrows():
        folium.CircleMarker(
            location=[row['stop_lat'], row['stop_lon']],
            radius=2,
            color='blue',
            fill=True,
            fill_opacity=0.8
        ).add_to(m)

    m.save(output_file)
    print(f"🗺️ Map with stops saved to: {output_file}")



def plot_profile_comparison_map(stops_common, stops_only_wheelchair, stops_only_elderly, output_file="outputs/map_comparison.html"):
    import folium
    import pandas as pd

    # Determine center point for the map
    all_points = pd.concat([stops_common, stops_only_wheelchair, stops_only_elderly])
    center = all_points.geometry.unary_union.centroid
    m = folium.Map(location=[center.y, center.x], zoom_start=15)

    # Common: green
    for _, row in stops_common.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=4,
            color='green',
            fill=True,
            fill_opacity=0.9,
            popup="Common"
        ).add_to(m)

    # Wheelchair only: blue
    for _, row in stops_only_wheelchair.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=4,
            color='blue',
            fill=True,
            fill_opacity=0.9,
            popup="Wheelchair only"
        ).add_to(m)

    # Elderly only: orange
    for _, row in stops_only_elderly.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=4,
            color='orange',
            fill=True,
            fill_opacity=0.9,
            popup="Elderly only"
        ).add_to(m)

    m.save(output_file)
    print(f"🗺️ Comparison map saved to: {output_file}")
