import argparse
import os
import arcpy
import pandas as pd

LON_COL = "Longitude (NAD83(2011))"
LAT_COL = "Latitude (NAD83(2011))"

SR_NAD83_2011 = arcpy.SpatialReference(6318)
SR_WGS84 = arcpy.SpatialReference(4326)
TRANSFORMATION = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

parser = argparse.ArgumentParser()
parser.add_argument("--input", "-i", required=True)
parser.add_argument("--output", "-o", default=None)
parser.add_argument("--shapefile", "-s", default=None)
args = parser.parse_args()

input_base = os.path.splitext(args.input)[0]
output_csv = args.output or input_base + "_wgs84.csv"
shapefile_path = args.shapefile or os.path.splitext(output_csv)[0] + ".shp"
args.output = output_csv

# --- Convert coordinates ---
df = pd.read_csv(args.input)

lons, lats = [], []
for _, row in df.iterrows():
    pt = arcpy.PointGeometry(arcpy.Point(row[LON_COL], row[LAT_COL]), SR_NAD83_2011)
    pt_wgs84 = pt.projectAs(SR_WGS84, TRANSFORMATION)
    lons.append(pt_wgs84.firstPoint.X)
    lats.append(pt_wgs84.firstPoint.Y)

df["Longitude_WGS84"] = lons
df["Latitude_WGS84"] = lats
df.to_csv(args.output, index=False)
print(f"Saved CSV: {args.output}")

# --- Create shapefile ---
out_dir, out_name = os.path.split(os.path.abspath(shapefile_path))
out_dir = out_dir or os.getcwd()
out_path = os.path.join(out_dir, out_name)

if arcpy.Exists(out_path):
    arcpy.management.Delete(out_path)

arcpy.management.CreateFeatureclass(out_dir, out_name, "POINT", spatial_reference=SR_WGS84)

for col in df.columns:
    field_type = "DOUBLE" if pd.api.types.is_numeric_dtype(df[col]) else "TEXT"
    arcpy.management.AddField(out_path, col[:10], field_type)

fields = ["SHAPE@XY"] + [col[:10] for col in df.columns]
with arcpy.da.InsertCursor(out_path, fields) as cursor:
    for _, row in df.iterrows():
        values = [(row["Longitude_WGS84"], row["Latitude_WGS84"])] + [row[col] for col in df.columns]
        cursor.insertRow(values)

print(f"Saved shapefile: {out_path}")
