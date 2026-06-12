import os
import arcpy
import pandas as pd

LON_COL = "Longitude (NAD83(2011))"
LAT_COL = "Latitude (NAD83(2011))"

SR_NAD83_2011 = arcpy.SpatialReference(6318)
SR_WGS84 = arcpy.SpatialReference(4326)
TRANSFORMATION = "WGS_1984_(ITRF08)_To_NAD_1983_2011"


class Toolbox(object):
    def __init__(self):
        self.label = "Coordinate Conversion Toolbox"
        self.alias = "coordconv"
        self.tools = [ConvertToWGS84]


class ConvertToWGS84(object):
    def __init__(self):
        self.label = "Convert NAD83(2011) CSV to WGS84"
        self.description = (
            "Converts NAD83(2011) coordinates in a CSV to WGS84, "
            "writing both a CSV and a point shapefile."
        )

    def getParameterInfo(self):
        params = []

        in_csv = arcpy.Parameter(
            displayName="Input CSV",
            name="in_csv",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")
        in_csv.filter.list = ["csv"]

        out_csv = arcpy.Parameter(
            displayName="Output CSV (optional)",
            name="out_csv",
            datatype="DEFile",
            parameterType="Optional",
            direction="Output")
        out_csv.filter.list = ["csv"]

        out_shp = arcpy.Parameter(
            displayName="Output Shapefile (optional)",
            name="out_shp",
            datatype="DEShapefile",
            parameterType="Optional",
            direction="Output")

        params += [in_csv, out_csv, out_shp]
        return params

    def execute(self, parameters, messages):
        in_csv = parameters[0].valueAsText
        out_csv = parameters[1].valueAsText
        out_shp = parameters[2].valueAsText

        input_base = os.path.splitext(in_csv)[0]
        out_csv = out_csv or input_base + "_wgs84.csv"
        out_shp = out_shp or os.path.splitext(out_csv)[0] + ".shp"

        # --- Convert coordinates ---
        df = pd.read_csv(in_csv)

        lons, lats = [], []
        for _, row in df.iterrows():
            pt = arcpy.PointGeometry(arcpy.Point(row[LON_COL], row[LAT_COL]), SR_NAD83_2011)
            pt_wgs84 = pt.projectAs(SR_WGS84, TRANSFORMATION)
            lons.append(pt_wgs84.firstPoint.X)
            lats.append(pt_wgs84.firstPoint.Y)

        df["Longitude_WGS84"] = lons
        df["Latitude_WGS84"] = lats
        df.to_csv(out_csv, index=False)
        messages.addMessage(f"Saved CSV: {out_csv}")

        # --- Create shapefile ---
        out_dir, out_name = os.path.split(os.path.abspath(out_shp))
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

        messages.addMessage(f"Saved shapefile: {out_path}")
