import requests


def fetch_osm_data(bbox, tag_filters):
    tag_str = "".join([f'["{k}"="{v}"]' for k, v in tag_filters.items()])
    query = f"""
    [out:json][timeout:25];
(
  way{tag_str}({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
);
out geom;
    """

    print("Running Overpass query:\n", query)
    res = requests.post("https://overpass-api.de/api/interpreter", data=query)
    res.raise_for_status()
    return res.json()
