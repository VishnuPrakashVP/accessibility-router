def filter_by_profile(gdf, profile):
    print(f"📊 Initial path count: {len(gdf)}")
    for key, condition in profile.items():
        if key not in gdf.columns:
            print(f"⚠️ Required tag '{key}' not found in data — skipping.")
            continue

        print(f"🔍 Filtering by '{key}' with condition: {condition}")
        print(f"   Unique values in '{key}': {gdf[key].dropna().unique()}")

        before = len(gdf)
        if isinstance(condition, list):
            gdf = gdf[gdf[key].isin(condition)]
        else:
            gdf = gdf[gdf[key] == condition]
        after = len(gdf)

        print(f"✅ Paths remaining after filtering by '{key}': {after} (filtered out {before - after})")

    print(f"🎯 Final accessible paths: {len(gdf)}")
    return gdf