import pandas as pd
from shapely.geometry import Point, LineString, box
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import rasterio
from tueplots import bundles
from matplotlib.backends.backend_pdf import PdfPages



#### 00 read cleaned data
gdf_stations = pd.read_csv("../../dat/cleaned data/gdf_stations.csv", sep = ",")
path_delays = pd.read_csv("path_delays.csv", sep = ",")


# get the route with the least delay = most reliable route
path_delays = path_delays.sort_values(by = "Total Delay")
path_delays = path_delays.reset_index(drop = True)
rel_path = path_delays.loc[0, "Path"]

# get the paths in fastest_path, that are separated by ->
rel_path = rel_path.split("->")

# convert the strings to integers
rel_path = [int(i) for i in rel_path]

# filter the data for the rel_path
gdf_stations = gdf_stations[gdf_stations["route_ids"].isin(rel_path)]





#### 02 map of Germany
# Extract LineString coordinates and create LineString geometries & point geometries
geometry_points = [Point(xy) for xy in zip(gdf_stations["Coordinate Longitude"], gdf_stations["Coordinate Latitude"])]

# Create GeoDataFrame
geo_df_points = gpd.GeoDataFrame(gdf_stations, geometry = geometry_points, crs = "EPSG:4326")

# Get a map of Germany, save as tif
germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)

# Get the shape of Germany
with rasterio.open("tifs/germany_osm.tif") as r:
    west, south, east, north = tuple(r.bounds)
    germany_crs = r.crs
bb_poly = box(west, south, east, north)
bb_poly = gpd.GeoDataFrame({"geometry": [bb_poly]}, crs = germany_crs)

# Overlay with GeoDataFrame for linestrings
gdf_germany = gpd.overlay(geo_df_points, bb_poly.to_crs(geo_df_points.crs), how = "intersection")


# Ensure the data is in the proper geographic coordinate system
gdf_germany_points = gdf_germany.to_crs(epsg = 3395)




#### 03 plot (full Germany map)

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data
fig, ax = plt.subplots(figsize = (3, 4))

# add condition for the points
condition = gdf_germany_points["Minutes of delay"] >= 6
gdf_germany_points[condition].plot(ax = ax, color = "crimson", markersize = 1, label = '>= 6 min')
gdf_germany_points[~condition].plot(ax = ax, color = "#19a824", markersize = 1, label = '< 6 min')

# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_points.crs, source = "tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)


# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_points.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax, title = "Most reliable route")

# Add labels and legend
ax.legend(loc = "upper left", frameon = False)


# Save as PDF
pdf_filename = "maps_KI_05_most_reliable_route_points_full.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")



#### 04 plot (zoomed on route)

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data
fig, ax = plt.subplots(figsize = (3, 6))


# add condition for the points
condition = gdf_germany_points["Minutes of delay"] >= 6
gdf_germany_points[condition].plot(ax = ax, color = "crimson", markersize = 10, label = '>= 6 min')
gdf_germany_points[~condition].plot(ax = ax, color = "#19a824", markersize = 10, label = '< 6 min')

# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_points.crs, source = "tifs/germany_osm.tif", alpha = 0.7, reset_extent = True)


# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_points.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax, title = "Most reliable route")

# Add labels and legend
ax.legend(loc = "upper right", frameon = False)


# Save as PDF
pdf_filename = "maps_KI_05_most_reliable_route_points_zoomed.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")




#### 05 plot both

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (6, 4))



# add condition for the points
condition = gdf_germany_points["Minutes of delay"] >= 6
gdf_germany_points[condition].plot(ax = ax1, color = "crimson", markersize = 1, label = '>= 6 min')
gdf_germany_points[~condition].plot(ax = ax1, color = "#19a824", markersize = 1, label = '< 6 min')

# add condition for the points
condition = gdf_germany_points["Minutes of delay"] >= 6
gdf_germany_points[condition].plot(ax = ax2, color = "crimson", markersize = 10, label = '>= 6 min')
gdf_germany_points[~condition].plot(ax = ax2, color = "#19a824", markersize = 10, label = '< 6 min')

# Add the base map
cx.add_basemap(ax = ax1, crs = gdf_germany_points.crs, source = "tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)
cx.add_basemap(ax = ax2, crs = gdf_germany_points.crs, source = "tifs/germany_osm.tif", alpha = 0.7, reset_extent = True, zoom = 100)


# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_points.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax1, title = "Most reliable route")
cx.plot_map(im2, bbox, ax = ax2, title = "Most reliable route (zoomed)")

# Add labels and legend
ax1.legend(loc = "upper left", frameon = False)
ax2.legend(loc = "upper right", frameon = False)


# Save as PDF
pdf_filename = "maps_KI_05_most_reliable_route_points.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")




#### 06 mean delay of most reliable route

# get the mean delay of the fastest route
print("The mean delay of the most reliable route is", gdf_stations["Minutes of delay"].mean())