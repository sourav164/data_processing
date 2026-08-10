import os
import arcpy
import pandas as pd

# --- Configuration ---
INPUT_FILE = r"C:/path/to/your/input.csv"  # Set your file path here

LON_COL = "Longitude (NAD83(2011))"
LAT_COL = "Latitude (NAD83(2011))"
SR_NAD83 = arcpy.SpatialReference(6318)
SR_WGS84 = arcpy.SpatialReference(4326)
TRANSFORMATION = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

# Automatically derive output CSV path in the same directory
base_dir, base_name = os.path.split(os.path.abspath(INPUT_FILE))
file_stem = os.path.splitext(base_name)[0]
output_csv = os.path.join(base_dir, f"{file_stem}_output.csv")

# --- Convert Coordinates ---
df = pd.read_csv(INPUT_FILE)
pts = [
    arcpy.PointGeometry(arcpy.Point(row[LON_COL], row[LAT_COL]), SR_NAD83).projectAs(SR_WGS84, TRANSFORMATION)
    for _, row in df.iterrows()
]
df["Longitude_WGS84"] = [pt.firstPoint.X for pt in pts]
df["Latitude_WGS84"] = [pt.firstPoint.Y for pt in pts]
df.to_csv(output_csv, index=False)
