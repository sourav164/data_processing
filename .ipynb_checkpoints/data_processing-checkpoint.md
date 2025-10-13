
# GCP Data Processing 
Process the collected AP data using propeller network. It will take a few mins to a few hours for the data to be corrected and processed. Download the data in CSV format. If you check the data, you will find the coordinate systems information. Often, it is EPSG: 6319 for the latitude and longitude. Our goal is to convert them to EPSG: 4326 (World Geodetic System 1984). Thus, we need to convert them. The process is provided below -

 1. Create a new copy of the CSV file and delete all info on the coordinate systems and only keep the raw data for further formatting. The data should be look like this 
 ![enter image description here](https://prnt.sc/eIlAZHTc4XI4)
 2. Open a fresh ArcGIS Pro map on your current workspace. Drag and drop the CSV file.
 3. Select the "Map" > "XY Point to Table" and import the data. Latitudes, Longitudes, and Altitudes (Orthometric height) need to be selected. For coordinate systems, use  **EPSG: 6318** (not EPSG: 6319) for data import.
 4. Once the data is imported, "Analysis" > "Tools" > search and use "Project" tools.
 5. Input your point shapefile, provide names for the possible output file (assume **Project_XY**), and select output coordinate systems EPSG: 4326 and run the tools. The location information has been updated but the data is not viewable as of right now.
 6. Right-click on the **Project_XY** and view the attribute table
 7. On the attribute table, bottom of the last row, click there to add new columns. You will add two columns, "WGS_84_Lat" and "WGS_84_Lon", one by one. The data type will be double.
 8. Right-click on one of the columns and select "Calculate Geometry". In the geometry attribute, select "WGS_84_Lat" and "WGS_84_Lon", and their property would be "Point Y-coordinate" and "Point X-coordinate", respectively. For the coordinate system, select **Project_XY**.
 9. Run the tools, then the location information is shown on the attribute table. Select all data, copy, and paste them into a new or existing CSV file to be used for using in Agisoft Metashape.
 
# Agisoft Metashape Processing
 1. Align - HIgh accuracy, Reference Preselection (if geotagging exists), default key and tie point limits (40,000, 4,000)
 2. Aeropoints data integration -
	 - Add Markers  
    - Import or manually enter the coordinates from the ground control fille
    - Open "Camera Calibration" tool and uncheck all of the fiex parameters
    - In the referencing tab of Metashape, uncheck all of the imagery (select all images and then uncheck one of the check boxes will uncheck all) and make sure all of the markers are checked.
    - Click "Optimize Cameras" in the reference tab and make sure all checkboxes are checked in the general section of the "Optimize Camera Alignment" popup and click Ok.
3.  Dense Cloud - Medium quality, mild depth filtering
4.  Mesh - Dense cloud, Height Field, High Face Count, Interpolation is Disabled
5.  DEM - all default
6.  Ortho - all default
