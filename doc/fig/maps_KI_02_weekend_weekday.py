import pandas as pd
from shapely.geometry import Point, box
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import rasterio
from tueplots import bundles




#### 00 get cleaned data
data = pd.read_csv("data.csv", sep = ";")

# Turn strings in to pandas date.
data["Date"] = pd.to_datetime(data["Date"], yearfirst = True)

# Get the day of the week for each date.
data["dayofweek"] = data["Date"].dt.dayofweek

# filter the data for weekend and weekday
condition = data["dayofweek"] >= 5
data_weekend = data[condition]
data_weekday = data[~condition]

# drop unnecessary columns
data_weekend = data_weekend.drop(["Date", "dayofweek", "Name", "Country"], axis = 1)
data_weekday = data_weekday.drop(["Date", "dayofweek", "Name", "Country"], axis = 1)

# get the mean of the minutes of delay for each station
data_weekend = data_weekend.groupby("Station or stop").mean()
data_weekday = data_weekday.groupby("Station or stop").mean()

# only include rows that are included in both dataframes
data_weekend = data_weekend[data_weekend.index.isin(data_weekday.index)]
data_weekday = data_weekday[data_weekday.index.isin(data_weekend.index)]

# create geometry with a point object of the coordinates
geometry_weekend = [Point(xy) for xy in zip(data_weekend["Coordinate Longitude"], data_weekend["Coordinate Latitude"])]
geometry_weekday = [Point(xy) for xy in zip(data_weekday["Coordinate Longitude"], data_weekday["Coordinate Latitude"])]

# create GeoDataFrame
geo_df_weekend = gpd.GeoDataFrame(data_weekend, geometry = geometry_weekend, crs = "EPSG:4326")
geo_df_weekday = gpd.GeoDataFrame(data_weekday, geometry = geometry_weekday, crs = "EPSG:4326")




#### 01 map of Germany

# Get a map of Germany, save as tif
germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)


# Get the shape of Germany
with rasterio.open("tifs/germany_osm.tif") as r:
    west, south, east, north = tuple(r.bounds)
    germany_crs = r.crs
bb_poly = box(west, south, east, north)
bb_poly = gpd.GeoDataFrame({"geometry": [bb_poly]}, crs = germany_crs)

gdf_germany_weekday = gpd.overlay(geo_df_weekday, bb_poly.to_crs(geo_df_weekend.crs), how = "intersection")
gdf_germany_weekend = gpd.overlay(geo_df_weekend, bb_poly.to_crs(geo_df_weekend.crs), how = "intersection")


# Ensure the data is in the proper geographic coordinate system
gdf_germany_weekday = gdf_germany_weekday.to_crs(epsg = 3395)
gdf_germany_weekend = gdf_germany_weekend.to_crs(epsg = 3395)




#### 02 plot

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "full", nrows = 1, ncols = 2, usetex = False))

# Plot the data
# plot two plots next to each other
fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (7, 4))
gdf_germany_weekday.plot(ax = ax1, markersize = 0, color = "k")
gdf_germany_weekend.plot(ax = ax2, markersize = 0, color = "k")


# Add the base map
cx.add_basemap(ax = ax1, crs = gdf_germany_weekday.crs, source = "tifs/germany_osm.tif", alpha = 0.7)
cx.add_basemap(ax = ax2, crs = gdf_germany_weekend.crs, source = "tifs/germany_osm.tif", alpha = 0.7)


# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_weekend.total_bounds
west, south, east, north = bounds

# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax1, title = "Weekdays")
cx.plot_map(im2, bbox, ax = ax2, title = "Weekends")


# Add condition for the markers
# green means no delay (less than 6 minutes), red means delay (more or equal to 6 minutes)
condition = gdf_germany_weekend["Minutes of delay"] < 6
gdf_germany_weekend[condition].plot(ax = ax2, markersize = 1, marker = "o", color = "#19a824", alpha = 0.9, label = "< 6 min")
gdf_germany_weekend[~condition].plot(ax = ax2, markersize = 1, marker = "o", color = "crimson", alpha = 0.7, label = ">= 6 min")

condition = gdf_germany_weekday["Minutes of delay"] < 6
gdf_germany_weekday[condition].plot(ax = ax1, markersize = 1, marker = "o", color = "#19a824", alpha = 0.9, label = "< 6 min")
gdf_germany_weekday[~condition].plot(ax = ax1, markersize = 1, marker = "o", color = "crimson", alpha = 0.7, label = ">= 6 min")


# Add labels and legend
ax1.legend(loc = "upper left", frameon = False)
ax2.legend(loc = "upper left", frameon = False)

# add title
fig.suptitle("Mean delay of trains in 2016 in Germany")



#### 03 Save as PDF
plt.savefig("maps_KI_02_weekend_weekday.pdf", bbox_inches = "tight")