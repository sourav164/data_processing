"""
Filter a bridge inventory GeoJSON file based on specified criteria.

Filters applied:
  - COUNTY in [85, 8, 40, 42, 64, 50, 77, 25, 91, 61, 39, 37, 94, 99, 35, 12, 38, 86, 79, 63]
  - NBI107 == 1
  - NBI58 <= 5
  - NBI59 <= 5
  - NBI60 <= 5
  - NBI49 > 100

Usage:
    python filter_bridges.py input.geojson output.geojson
"""

import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TARGET_COUNTIES = {85, 8, 40, 42, 64, 50, 77, 25, 91, 61, 39, 37, 94, 99, 35, 12, 38, 86, 79, 63}


def safe_int(value):
    """Convert a value to int, returning None if conversion fails or value is None."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def passes_filters(props: dict) -> bool:
    """Return True if a feature's properties satisfy all filter criteria."""

    # --- COUNTY ---
    county = safe_int(props.get("COUNTY"))
    if county is None or county not in TARGET_COUNTIES:
        return False

    # --- NBI107 == 1 ---
    nbi107 = safe_int(props.get("NBI107"))
    if nbi107 != 1:
        return False

    # --- NBI58, NBI59, NBI60 <= 5 ---
    for field in ("NBI58", "NBI59", "NBI60"):
        val = safe_int(props.get(field))
        if val is None or val > 5:
            return False

    # --- NBI49 > 100 ---
    nbi49 = safe_int(props.get("NBI49"))
    if nbi49 is None or nbi49 <= 100:
        return False

    return True


def filter_geojson(input_path: str, output_path: str) -> None:
    print(f"Reading: {input_path}")
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    if data.get("type") != "FeatureCollection":
        raise ValueError(f"Expected a FeatureCollection, got: {data.get('type')}")

    features = data.get("features", [])
    total = len(features)
    print(f"Total features in input: {total:,}")

    filtered = [feat for feat in features if passes_filters(feat["properties"])]
    kept = len(filtered)
    print(f"Features passing all filters: {kept:,}  ({kept/total*100:.1f}%)")

    output = {
        "type": "FeatureCollection",
        "name": data.get("name", "filtered_bridges"),
        "crs": data.get("crs"),
        "features": filtered,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f)

    size_kb = Path(output_path).stat().st_size / 1024
    print(f"Output written to: {output_path}  ({size_kb:.1f} KB)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python filter_bridges.py <input.geojson> <output.geojson>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    filter_geojson(input_path, output_path)
