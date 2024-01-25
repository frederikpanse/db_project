import pandas as pd
from shapely.geometry import Point, box
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import rasterio
from tueplots import bundles
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import numpy as np




#### 00 get cleaned data
from ipynb.fs.full.exploration_cleaning import get_data
data = get_data(which = "mean")


# create geometry column with a point object of the coordinates
geometry = [Point(xy) for xy in zip(data["Coordinate Longitude"], data["Coordinate Latitude"])]

# create GeoDataFrame
geo_df = gpd.GeoDataFrame(data, geometry = geometry, crs = "EPSG:4326")  # Use the correct CRS




#### 01 map of Germany

# Get a map of Germany, save as tif
germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)


# Get the shape of Germany
with rasterio.open("../doc/fig/tifs/germany_osm.tif") as r:
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
cx.add_basemap(ax = ax, crs = gdf_germany.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7)

# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany.total_bounds
west, south, east, north = bounds

# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax) # title = "Mean delay of trains in 2016 in Germany"

# Add condition for the markers
# green means no delay (less than 6 minutes), red means delay (more or equal to 6 minutes)
condition = gdf_germany["Minutes of delay"] < 6
gdf_germany[condition].plot(ax = ax, markersize = 1, marker = "o", color = "#19a824", alpha = 0.9, label = "< 6 min")
gdf_germany[~condition].plot(ax = ax, markersize = 1, marker = "o", color = "crimson", alpha = 0.7, label = ">= 6 min")

# Add labels and legend
ax.legend(loc = "upper left", frameon = False)




#### 03 Save as PDF
pdf_filename = "../doc/fig/maps_KI_01_all_data.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")



#### 02 plot

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data
fig, ax = plt.subplots(figsize = (4, 3))
gdf_germany.plot(ax = ax, markersize = 0, color = "k")


# Apply log scaling to min & max values
log_min_delay = np.log1p(gdf_germany["Minutes of delay"].min())
log_max_delay = np.log1p(gdf_germany["Minutes of delay"].max())

# Create ScalarMappable with common normalization
norm = Normalize(vmin = log_min_delay, vmax = log_max_delay)
sm = ScalarMappable(norm = norm, cmap = "coolwarm")
sm.set_array([])

# Plot the points, create a colorbar for the points
gdf_germany["color"] = gdf_germany["Minutes of delay"].apply(lambda x: sm.to_rgba(np.log1p(x)))
gdf_germany[gdf_germany["Minutes of delay"] >= 0].plot(ax = ax, color = gdf_germany.loc[gdf_germany["Minutes of delay"] >= 0, "color"], markersize = 1, marker = "o")


# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany.crs, source = "../doc/fig/tifs/germany_Carto.tif", alpha = 1)

# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany.total_bounds
west, south, east, north = bounds

# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax) # title = "Mean delay of trains in 2016 in Germany"

# Add colorbar for the points
cbar = plt.colorbar(sm, ax = ax, label = "Minutes of delay (log scale)", orientation = "vertical", pad = 0.02, ticks = [1, 2, 3, 4, 5, 6, 7])

# Convert log-scaled ticks back to original scale for display
cbar_ticks_original_scale = np.expm1(cbar.get_ticks())
rounded_ticks = [round(tick) if tick % 1 else int(tick) for tick in cbar_ticks_original_scale]
cbar.set_ticklabels([f"{int(original_scale)} min" for original_scale in rounded_ticks])
cbar.set_label("Minutes of delay (log scaled)")

# Remove border color
cbar.outline.set_edgecolor("none")




#### 03 Save as PDF
pdf_filename = "../doc/fig/maps_KI_01_all_data_cmap.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")


print("The mean delay of all Germany in 2016 was", round(gdf_germany["Minutes of delay"].mean(), 2), "minutes.")
