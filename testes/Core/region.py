import json
import os


def load_capture_region(region_file):
    if not os.path.exists(region_file):
        return None

    try:
        with open(region_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return (data["x"], data["y"], data["width"], data["height"])
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return None


def save_capture_region(x, y, width, height, region_file):
    data = {"x": x, "y": y, "width": width, "height": height}

    with open(region_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
