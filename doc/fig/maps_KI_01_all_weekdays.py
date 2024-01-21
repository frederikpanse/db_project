import pandas as pd
from shapely.geometry import Point, box
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import rasterio
from tueplots import bundles
from matplotlib.backends.backend_pdf import PdfPages




#### 00 get cleaned data
data = pd.read_csv("data.csv", sep = ";")

# Turn strings in to pandas date.
data["Date"] = pd.to_datetime(data["Date"], yearfirst = True)

# Get the day of the week for each date.
data["dayofweek"] = data["Date"].dt.dayofweek

# create seperate dataframes for every weekday
data_monday = data[data["dayofweek"] == 0]
data_tuesday = data[data["dayofweek"] == 1]
data_wednesday = data[data["dayofweek"] == 2]
data_thursday = data[data["dayofweek"] == 3]
data_friday = data[data["dayofweek"] == 4]
data_saturday = data[data["dayofweek"] == 5]
data_sunday = data[data["dayofweek"] == 6]

# drop unnecessary columns
data_monday = data_monday.drop(["Date", "dayofweek", "Name", "Country"], axis = 1)
data_tuesday = data_tuesday.drop(["Date", "dayofweek", "Name", "Country"], axis = 1)
data_wednesday = data_wednesday.drop(["Date", "dayofweek", "Name", "Country"], axis = 1)
data_thursday = data_thursday.drop(["Date", "dayofweek", "Name", "Country"], axis = 1)
data_friday = data_friday.drop(["Date", "dayofweek", "Name", "Country"], axis = 1)
data_saturday = data_saturday.drop(["Date", "dayofweek", "Name", "Country"], axis = 1)
data_sunday = data_sunday.drop(["Date", "dayofweek", "Name", "Country"], axis = 1)

# get the mean of the minutes of delay for each station
data_monday = data_monday.groupby("Station or stop").mean()
data_tuesday = data_tuesday.groupby("Station or stop").mean()
data_wednesday = data_wednesday.groupby("Station or stop").mean()
data_thursday = data_thursday.groupby("Station or stop").mean()
data_friday = data_friday.groupby("Station or stop").mean()
data_saturday = data_saturday.groupby("Station or stop").mean()
data_sunday = data_sunday.groupby("Station or stop").mean()

# only include rows that are included in all dataframes
# data_monday = data_monday[data_monday.index.isin(data_sunday.index)]
# data_tuesday = data_tuesday[data_tuesday.index.isin(data_sunday.index)]
# data_wednesday = data_wednesday[data_wednesday.index.isin(data_sunday.index)]
# data_thursday = data_thursday[data_thursday.index.isin(data_sunday.index)]
# data_friday = data_friday[data_friday.index.isin(data_sunday.index)]
# data_saturday = data_saturday[data_saturday.index.isin(data_sunday.index)]

# create geometry with a point object of the coordinates
geometry_monday = [Point(xy) for xy in zip(data_monday["Coordinate Longitude"], data_monday["Coordinate Latitude"])]
geometry_tuesday = [Point(xy) for xy in zip(data_tuesday["Coordinate Longitude"], data_tuesday["Coordinate Latitude"])]
geometry_wednesday = [Point(xy) for xy in zip(data_wednesday["Coordinate Longitude"], data_wednesday["Coordinate Latitude"])]
geometry_thursday = [Point(xy) for xy in zip(data_thursday["Coordinate Longitude"], data_thursday["Coordinate Latitude"])]
geometry_friday = [Point(xy) for xy in zip(data_friday["Coordinate Longitude"], data_friday["Coordinate Latitude"])]
geometry_saturday = [Point(xy) for xy in zip(data_saturday["Coordinate Longitude"], data_saturday["Coordinate Latitude"])]
geometry_sunday = [Point(xy) for xy in zip(data_sunday["Coordinate Longitude"], data_sunday["Coordinate Latitude"])]

# create GeoDataFrames
geo_df_monday = gpd.GeoDataFrame(data_monday, geometry = geometry_monday, crs = "EPSG:4326")
geo_df_tuesday = gpd.GeoDataFrame(data_tuesday, geometry = geometry_tuesday, crs = "EPSG:4326")
geo_df_wednesday = gpd.GeoDataFrame(data_wednesday, geometry = geometry_wednesday, crs = "EPSG:4326")
geo_df_thursday = gpd.GeoDataFrame(data_thursday, geometry = geometry_thursday, crs = "EPSG:4326")
geo_df_friday = gpd.GeoDataFrame(data_friday, geometry = geometry_friday, crs = "EPSG:4326")
geo_df_saturday = gpd.GeoDataFrame(data_saturday, geometry = geometry_saturday, crs = "EPSG:4326")
geo_df_sunday = gpd.GeoDataFrame(data_sunday, geometry = geometry_sunday, crs = "EPSG:4326")



#### 01 map of Germany

# Get a map of Germany, save as tif
germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)


# Get the shape of Germany
with rasterio.open("tifs/germany_osm.tif") as r:
    west, south, east, north = tuple(r.bounds)
    germany_crs = r.crs
bb_poly = box(west, south, east, north)
bb_poly = gpd.GeoDataFrame({"geometry": [bb_poly]}, crs = germany_crs)


gdf_germany_monday = gpd.overlay(geo_df_monday, bb_poly.to_crs(geo_df_monday.crs), how = "intersection")
gdf_germany_tuesday = gpd.overlay(geo_df_tuesday, bb_poly.to_crs(geo_df_tuesday.crs), how = "intersection")
gdf_germany_wednesday = gpd.overlay(geo_df_wednesday, bb_poly.to_crs(geo_df_wednesday.crs), how = "intersection")
gdf_germany_thursday = gpd.overlay(geo_df_thursday, bb_poly.to_crs(geo_df_thursday.crs), how = "intersection")
gdf_germany_friday = gpd.overlay(geo_df_friday, bb_poly.to_crs(geo_df_friday.crs), how = "intersection")
gdf_germany_saturday = gpd.overlay(geo_df_saturday, bb_poly.to_crs(geo_df_saturday.crs), how = "intersection")
gdf_germany_sunday = gpd.overlay(geo_df_sunday, bb_poly.to_crs(geo_df_sunday.crs), how = "intersection")



# Ensure the data is in the proper geographic coordinate system
gdf_germany_monday = gdf_germany_monday.to_crs(epsg = 3395)
gdf_germany_tuesday = gdf_germany_tuesday.to_crs(epsg = 3395)
gdf_germany_wednesday = gdf_germany_wednesday.to_crs(epsg = 3395)
gdf_germany_thursday = gdf_germany_thursday.to_crs(epsg = 3395)
gdf_germany_friday = gdf_germany_friday.to_crs(epsg = 3395)
gdf_germany_saturday = gdf_germany_saturday.to_crs(epsg = 3395)
gdf_germany_sunday = gdf_germany_sunday.to_crs(epsg = 3395)




#### 02 plot

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "full", nrows = 1, ncols = 2, usetex = False))

# Plot the data
# plot seven plots
fig, ((ax1, ax2, ax3, ax4), (ax5, ax6, ax7, ax8)) = plt.subplots(2, 4, figsize = (10, 5))
gdf_germany_monday.plot(ax = ax1, markersize = 0, color = "white")
gdf_germany_tuesday.plot(ax = ax2, markersize = 0, color = "white")
gdf_germany_wednesday.plot(ax = ax3, markersize = 0, color = "white")
gdf_germany_thursday.plot(ax = ax4, markersize = 0, color = "white")
gdf_germany_friday.plot(ax = ax5, markersize = 0, color = "white")
gdf_germany_saturday.plot(ax = ax6, markersize = 0, color = "white")
gdf_germany_sunday.plot(ax = ax7, markersize = 0, color = "white")


# Add the base map
cx.add_basemap(ax = ax1, crs = gdf_germany_monday.crs, source = "tifs/germany_osm.tif", alpha = 0.7)
cx.add_basemap(ax = ax2, crs = gdf_germany_tuesday.crs, source = "tifs/germany_osm.tif", alpha = 0.7)
cx.add_basemap(ax = ax3, crs = gdf_germany_wednesday.crs, source = "tifs/germany_osm.tif", alpha = 0.7)
cx.add_basemap(ax = ax4, crs = gdf_germany_thursday.crs, source = "tifs/germany_osm.tif", alpha = 0.7)
cx.add_basemap(ax = ax5, crs = gdf_germany_friday.crs, source = "tifs/germany_osm.tif", alpha = 0.7)
cx.add_basemap(ax = ax6, crs = gdf_germany_saturday.crs, source = "tifs/germany_osm.tif", alpha = 0.7)
cx.add_basemap(ax = ax7, crs = gdf_germany_sunday.crs, source = "tifs/germany_osm.tif", alpha = 0.7)


# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_monday.total_bounds
west, south, east, north = bounds

# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax1, title = "Monday")
cx.plot_map(im2, bbox, ax = ax2, title = "Tuesday")
cx.plot_map(im2, bbox, ax = ax3, title = "Wednesday")
cx.plot_map(im2, bbox, ax = ax4, title = "Thursday")
cx.plot_map(im2, bbox, ax = ax5, title = "Friday")
cx.plot_map(im2, bbox, ax = ax6, title = "Saturday")
cx.plot_map(im2, bbox, ax = ax7, title = "Sunday")

# add an empty plot for ax8
ax8.axis("off")

# add title
fig.suptitle("Mean delay of trains in 2016 in Germany")


# Add condition for the markers
# green means no delay (less than 6 minutes), red means delay (more or equal to 6 minutes)
condition = gdf_germany_monday["Minutes of delay"] < 6
gdf_germany_monday[condition].plot(ax = ax1, markersize = 0.5, marker = "o", color = "#19a824", alpha = 0.9, label = "< 6 min")
gdf_germany_monday[~condition].plot(ax = ax1, markersize = 0.5, marker = "o", color = "crimson", alpha = 0.7, label = ">= 6 min")

condition = gdf_germany_tuesday["Minutes of delay"] < 6
gdf_germany_tuesday[condition].plot(ax = ax2, markersize = 0.5, marker = "o", color = "#19a824", alpha = 0.9, label = "< 6 min")
gdf_germany_tuesday[~condition].plot(ax = ax2, markersize = 0.5, marker = "o", color = "crimson", alpha = 0.7, label = ">= 6 min")

condition = gdf_germany_wednesday["Minutes of delay"] < 6
gdf_germany_wednesday[condition].plot(ax = ax3, markersize = 0.5, marker = "o", color = "#19a824", alpha = 0.9, label = "< 6 min")
gdf_germany_wednesday[~condition].plot(ax = ax3, markersize = 0.5, marker = "o", color = "crimson", alpha = 0.7, label = ">= 6 min")

condition = gdf_germany_thursday["Minutes of delay"] < 6
gdf_germany_thursday[condition].plot(ax = ax4, markersize = 0.5, marker = "o", color = "#19a824", alpha = 0.9, label = "< 6 min")
gdf_germany_thursday[~condition].plot(ax = ax4, markersize = 0.5, marker = "o", color = "crimson", alpha = 0.7, label = ">= 6 min")

condition = gdf_germany_friday["Minutes of delay"] < 6
gdf_germany_friday[condition].plot(ax = ax5, markersize = 0.5, marker = "o", color = "#19a824", alpha = 0.9, label = "< 6 min")
gdf_germany_friday[~condition].plot(ax = ax5, markersize = 0.5, marker = "o", color = "crimson", alpha = 0.7, label = ">= 6 min")

condition = gdf_germany_saturday["Minutes of delay"] < 6
gdf_germany_saturday[condition].plot(ax = ax6, markersize = 0.5, marker = "o", color = "#19a824", alpha = 0.9, label = "< 6 min")
gdf_germany_saturday[~condition].plot(ax = ax6, markersize = 0.5, marker = "o", color = "crimson", alpha = 0.7, label = ">= 6 min")

condition = gdf_germany_sunday["Minutes of delay"] < 6
gdf_germany_sunday[condition].plot(ax = ax7, markersize = 0.5, marker = "o", color = "#19a824", alpha = 0.9, label = "< 6 min")
gdf_germany_sunday[~condition].plot(ax = ax7, markersize = 0.5, marker = "o", color = "crimson", alpha = 0.7, label = ">= 6 min")


# Add labels and legend
ax1.legend(loc = "upper left", frameon = False)
ax2.legend(loc = "upper left", frameon = False)
ax3.legend(loc = "upper left", frameon = False)
ax4.legend(loc = "upper left", frameon = False)
ax5.legend(loc = "upper left", frameon = False)
ax6.legend(loc = "upper left", frameon = False)
ax7.legend(loc = "upper left", frameon = False)

#### 03 Save as PDF
pdf_filename = "maps_KI_01_all_weekdays.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")