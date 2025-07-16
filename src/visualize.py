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