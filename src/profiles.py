profiles = {
    "wheelchair": {
        "walk_speed": 0.5,
        "avoid_tags": {
            "surface": ["paving_stones"]  # May be bumpy for some wheelchair users
        }
    },
    "elderly": {
        "walk_speed": 0.75,
        "avoid_tags": {
            "surface": ["paving_stones", "concrete"]  # May be uneven or hard
        }
    }
}