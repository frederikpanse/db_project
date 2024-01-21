import pandas as pd
from shapely.geometry import Point, box
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import rasterio
from tueplots import bundles




#### 00 get cleaned data
data = pd.read_csv("data_mean.csv", sep = ";")

# create geometry column with a point object of the coordinates
geometry = [Point(xy) for xy in zip(data["Coordinate Longitude"], data["Coordinate Latitude"])]

# create GeoDataFrame
geo_df = gpd.GeoDataFrame(data, geometry = geometry, crs = "EPSG:4326")  # Use the correct CRS




#### 01 map of Germany

# Get a map of Germany, save as tif
germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)


# Get the shape of Germany
with rasterio.open("tifs/germany_osm.tif") as r:
    west, south, east, north = tuple(r.bounds)
    germany_crs = r.crs
bb_poly = box(west, south, east, north)
bb_poly = gpd.GeoDataFrame({"geometry": [bb_poly]}, crs = germany_crs)

gdf_germany = gpd.overlay(geo_df, bb_poly.to_crs(geo_df.crs), how = "intersection")

# Ensure the data is in the proper geographic coordinate system
gdf_germany = gdf_germany.to_crs(epsg = 3395)




#### 02 plot

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data
fig, ax = plt.subplots(figsize = (4, 4))
gdf_germany.plot(ax = ax, markersize = 0, color = "k")

# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany.crs, source = "tifs/germany_osm.tif", alpha = 0.7)

# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany.total_bounds
west, south, east, north = bounds

# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax, title = "Mean delay of trains in 2016 in Germany")

# Add condition for the markers
# green means no delay (less than 6 minutes), red means delay (more or equal to 6 minutes)
condition = gdf_germany["Minutes of delay"] < 6
gdf_germany[condition].plot(ax = ax, markersize = 1, marker = "o", color = "#19a824", alpha = 0.9, label = "< 6 min")
gdf_germany[~condition].plot(ax = ax, markersize = 1, marker = "o", color = "crimson", alpha = 0.7, label = ">= 6 min")

# Add labels and legend
ax.legend(loc = "upper left", frameon = False)




#### 03 Save as PDF
# plt.savefig("maps_KI_01_XXX.pdf", bbox_inches = 'tight')