import geopandas as gpd
from shapely.geometry import LineString

def parse_osm_json(json_data):
    features = []
    for element in json_data.get("elements", []):
        if element.get("type") == "way" and "geometry" in element:
            coords = [(pt["lon"], pt["lat"]) for pt in element["geometry"]]
            tags = element.get("tags", {})
            features.append({
                "geometry": LineString(coords),
                **tags
            })

    if not features:
        print("⚠️ No features found. Returning empty GeoDataFrame.")
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")

    return gpd.GeoDataFrame(features, geometry="geometry", crs="EPSG:4326")