def filter_by_profile(gdf, profile):
    for key, value in profile.get("required_tags", {}).items():
        if key in gdf.columns:
            if isinstance(value, list):
                gdf = gdf[gdf[key].isin(value)]
            else:
                gdf = gdf[gdf[key] == value]
        else:
            print(f"⚠️ Required tag '{key}' not found — skipping.")

    for key, value in profile.get("avoid_tags", {}).items():
        if key in gdf.columns:
            if isinstance(value, list):
                gdf = gdf[~gdf[key].isin(value)]
            else:
                gdf = gdf[gdf[key] != value]
        else:
            print(f"⚠️ Avoid tag '{key}' not found — skipping.")

    return gdf