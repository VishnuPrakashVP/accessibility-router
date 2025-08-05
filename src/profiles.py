# profiles.py

profiles = {
    "normal": {},  # No restrictions

    "wheelchair": {
        "wheelchair": "yes",
        "incline": ["up", "down", None],
        "surface": [
            "asphalt", "paving_stones", "concrete", "paved"
        ],
        "smoothness": ["excellent", "good", "intermediate"]
    },

    "elderly": {
        "incline": ["up", "down", None],
        "surface": [
            "asphalt", "paving_stones", "concrete", "paved"
        ],
        "smoothness": ["good", "intermediate"]
    }
}