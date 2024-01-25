import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString, box
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib as mpl
import contextily as cx
import rasterio
from tueplots import bundles
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.colors import SymLogNorm



#### 00 read cleaned data
from ipynb.fs.full.exploration_cleaning import get_data
from ipynb.fs.full.exploration_cleaning import get_paths
data = get_data(which = "mean")
path_delays = get_paths()
gdf_stations = pd.read_csv("../dat/stations_with_nearest_routes.csv", sep = ",")
data_routes = gpd.read_file("../dat/geo-strecke/strecken_polyline.shp")




#### 01 Routes

## 1.1 Most reliable route
# get the route with the least delay = most reliable route
paths_sorted = sorted(path_delays.items(), key = lambda x: x[1]["mean_delay"])
rel_path = paths_sorted[0][1]["routes"]
print(paths_sorted[0][1]["mean_delay"])

# filter the data for the rel_path
gdf_stations_rel = gdf_stations[gdf_stations["Route"].isin(rel_path)]

# merge with data
gdf_stations_rel = gdf_stations_rel.merge(data, on = "Station or stop")


## 1.2 Fastest route
# Fastest route that Deutsche Bahn offers
fastest_route = [80290288, #Stuttgart
                 80290270, 80297853, 80297846,
                 80196212, 80297788, 80297770, 80145615,
                 80142620, 80183079, 80142786, 80142877,
                 80145649, 80144147, 80140640, 80180919,
                 80140624, 80140616, 80147124, 80182576, 80042408,
                 80143909, 80140236, 80140137, #Mannheim
                 80140186, 80113324, 80113316, 80113308,
                 80113118, 80113092, 80113084,
                 80113076, 80104711, 80113043, 80113035, 80112995, 80112987, 80105767, 80112953, 80113365, # Darmstadt
                 80112813, 80112839, 80112854, 80105098, 80108555, 80107995 # Frankfurt Main
]

# filter the data for the fastest route
gdf_stations_fast = gdf_stations[gdf_stations["Station or stop"].isin(fastest_route)]

# merge with data
gdf_stations_fast = gdf_stations_fast.merge(data, on = "Station or stop")




#### FASTEST ROUTE BY DB (POINTS) ####

#### 01 map of Germany
# Extract LineString coordinates and create LineString geometries & point geometries
geometry_points = [Point(xy) for xy in zip(gdf_stations_fast["Coordinate Longitude"], gdf_stations_fast["Coordinate Latitude"])]

# Create GeoDataFrame
geo_df_points = gpd.GeoDataFrame(gdf_stations_fast, geometry = geometry_points, crs = "EPSG:4326")

# Get a map of Germany, save as tif
germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)

# Get the shape of Germany
with rasterio.open("../doc/fig/tifs/germany_osm.tif") as r:
    west, south, east, north = tuple(r.bounds)
    germany_crs = r.crs
bb_poly = box(west, south, east, north)
bb_poly = gpd.GeoDataFrame({"geometry": [bb_poly]}, crs = germany_crs)

# Overlay with GeoDataFrame for linestrings
gdf_germany = gpd.overlay(geo_df_points, bb_poly.to_crs(geo_df_points.crs), how = "intersection")


# Ensure the data is in the proper geographic coordinate system
gdf_germany_points = gdf_germany.to_crs(epsg = 3395)



#### 02 plot (full Germany map)

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data
fig, ax = plt.subplots(figsize = (3, 4))

# add condition for the points
condition = gdf_germany_points["Minutes of delay"] >= 6
gdf_germany_points[condition].plot(ax = ax, color = "crimson", markersize = 1, label = '>= 6 min')
gdf_germany_points[~condition].plot(ax = ax, color = "#19a824", markersize = 1, label = '< 6 min')

# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_points.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)


# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_points.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax, title = "Fastest route")

# Add labels and legend
ax.legend(loc = "upper left", frameon = False)


# Save as PDF
pdf_filename = "../doc/fig/other figs/maps_KI_03_fastest_route_points_full.pdf"
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
gdf_germany_points[condition].plot(ax = ax, color = "crimson", markersize = 12, label = '>= 6 min')
gdf_germany_points[~condition].plot(ax = ax, color = "#19a824", markersize = 12, label = '< 6 min')

# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_points.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = True)


# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_points.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax, title = "Fastest route")

# Add labels and legend
ax.legend(loc = "upper right", frameon = False)


# Save as PDF
pdf_filename = "../doc/fig/other figs/maps_KI_03_fastest_route_points_zoomed.pdf"
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
gdf_germany_points[condition].plot(ax = ax2, color = "crimson", markersize = 12, label = '>= 6 min')
gdf_germany_points[~condition].plot(ax = ax2, color = "#19a824", markersize = 12, label = '< 6 min')

# Add the base map
cx.add_basemap(ax = ax1, crs = gdf_germany_points.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)
cx.add_basemap(ax = ax2, crs = gdf_germany_points.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = True, zoom = 100)


# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_points.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax1, title = "Fastest route")
cx.plot_map(im2, bbox, ax = ax2, title = "Fastest route (zoomed)")

# Add labels and legend
ax1.legend(loc = "upper left", frameon = False)
ax2.legend(loc = "upper right", frameon = False)


# Save as PDF
pdf_filename = "../doc/fig/other figs/maps_KI_03_fastest_route_points.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")
    
    


#### MOST RELIABLE ROUTE BY OUR MODEL (POINTS) ####


#### 02 map of Germany
# Extract LineString coordinates and create LineString geometries & point geometries
geometry_points = [Point(xy) for xy in zip(gdf_stations_rel["Coordinate Longitude"], gdf_stations_rel["Coordinate Latitude"])]

# Create GeoDataFrame
geo_df_points = gpd.GeoDataFrame(gdf_stations_rel, geometry = geometry_points, crs = "EPSG:4326")

# Get a map of Germany, save as tif
germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)

# Get the shape of Germany
with rasterio.open("../doc/fig/tifs/germany_osm.tif") as r:
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
cx.add_basemap(ax = ax, crs = gdf_germany_points.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)


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
pdf_filename = "../doc/fig/other figs/maps_KI_03_most_reliable_route_points_full.pdf"
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
gdf_germany_points[condition].plot(ax = ax, color = "crimson", markersize = 12, label = '>= 6 min')
gdf_germany_points[~condition].plot(ax = ax, color = "#19a824", markersize = 12, label = '< 6 min')

# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_points.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = True)


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
pdf_filename = "../doc/fig/other figs/maps_KI_03_most_reliable_route_points_zoomed.pdf"
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
gdf_germany_points[condition].plot(ax = ax2, color = "crimson", markersize = 12, label = '>= 6 min')
gdf_germany_points[~condition].plot(ax = ax2, color = "#19a824", markersize = 12, label = '< 6 min')

# Add the base map
cx.add_basemap(ax = ax1, crs = gdf_germany_points.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)
cx.add_basemap(ax = ax2, crs = gdf_germany_points.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = True, zoom = 100)


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
pdf_filename = "../doc/fig/other figs/maps_KI_03_most_reliable_route_points.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")





#### MOST RELIABLE ROUTE BY OUR MODEL (LINESTRINGS) ####

## 1.1 Most reliable route
# get the route with the least delay = most reliable route
paths_sorted = sorted(path_delays.items(), key = lambda x: x[1]["mean_delay"])
rel_path = paths_sorted[0][1]["routes"]

# filter the data for the rel_path
gdf_stations_rel = gdf_stations[gdf_stations["Route"].isin(rel_path)]

# merge with data
gdf_stations_rel = gdf_stations_rel.merge(data, on = "Station or stop")

# create geometry column with a point object of the coordinates
geometry = [Point(xy) for xy in zip(gdf_stations_rel["Coordinate Longitude"], gdf_stations_rel["Coordinate Latitude"])]

# create GeoDataFrame
geo_df = gpd.GeoDataFrame(gdf_stations_rel, geometry = geometry, crs = "EPSG:4326")  # Use the correct CRS

# merge the two datasets
# rename the column "strecke_nr" to "Route"
data_routes = data_routes.rename(columns = {"strecke_nr": "Route"})
data_routes["Route"] = data_routes["Route"].astype(float)
data_delay_routes = pd.merge(data_routes, gdf_stations_rel, on = "Route", how = "right")


# create new dataset with colums Route, Minutes of delay
data_delay_routes = data_delay_routes[["Minutes of delay", "Route"]].copy()

# calculate mean per route, without index column
data_delay_routes = data_delay_routes.groupby(["Route"]).mean()

# again merge with data_routes to get the geometry
data_delay_routes = pd.merge(data_delay_routes, data_routes, on = "Route", how = "left")

# group the dataset by geometry
# data_delay_routes = data_delay_routes.groupby(["geometry"]).mean()

# only take columns Minutes of delay, Route, geometry
data_delay_routes = data_delay_routes[["Minutes of delay", "Route", "geometry"]].copy()
data_delay_routes = data_delay_routes.groupby(["geometry"], as_index = False).mean()



#### 02 map of Germany
# Extract LineString coordinates and create LineString geometries
geometry_linestrings = [LineString(x) for x in data_delay_routes["geometry"]]

# Create GeoDataFrame for linestrings
geo_df_linestrings = gpd.GeoDataFrame(data_delay_routes, geometry = geometry_linestrings, crs = "EPSG:4326")

# Get a map of Germany, save as tif
germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)

# Get the shape of Germany
with rasterio.open("../doc/fig/tifs/germany_osm.tif") as r:
    west, south, east, north = tuple(r.bounds)
    germany_crs = r.crs
bb_poly = box(west, south, east, north)
bb_poly = gpd.GeoDataFrame({"geometry": [bb_poly]}, crs = germany_crs)

# Overlay with GeoDataFrame for linestrings
gdf_germany_linestrings = gpd.overlay(geo_df_linestrings, bb_poly.to_crs(geo_df_linestrings.crs), how = "intersection")

# Ensure the data is in the proper geographic coordinate system
gdf_germany_linestrings = gdf_germany_linestrings.to_crs(epsg = 3395)




#### 03 plot (full Germany map)

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data
fig, ax = plt.subplots(figsize = (3, 4))

# add condition for the linestrings
condition = gdf_germany_linestrings["Minutes of delay"] < 6
gdf_germany_linestrings[condition].plot(ax = ax, color = "#19a824", linewidth = 1.5, label = '< 6 min')
gdf_germany_linestrings[~condition].plot(ax = ax, color = "crimson", linewidth = 1.5, label = '>= 6 min')


# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_linestrings.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)


# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_linestrings.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax, title = "Most reliable route")

# Add labels and legend
ax.legend(loc = "upper left", frameon = False)


# Save as PDF
pdf_filename = "../doc/fig/other figs/maps_KI_03_most_reliable_route_line_full.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")



#### 04 plot (zoomed on route)

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data
fig, ax = plt.subplots(figsize = (3, 6))


# add condition for the linestrings
condition = gdf_germany_linestrings["Minutes of delay"] < 6
gdf_germany_linestrings[condition].plot(ax = ax, color = "#19a824", linewidth = 2, label = '< 6 min')
gdf_germany_linestrings[~condition].plot(ax = ax, color = "crimson", linewidth = 2, label = '>= 6 min')


# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_linestrings.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = True)


# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_linestrings.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax, title = "Most reliable route")

# Add labels and legend
ax.legend(loc = "upper right", frameon = False)


# Save as PDF
pdf_filename = "../doc/fig/other figs/maps_KI_03_most_reliable_route_line_zoomed.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")


#### 05 plot both

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (6, 4))


# add condition for the linestrings
condition = gdf_germany_linestrings["Minutes of delay"] < 6
gdf_germany_linestrings[condition].plot(ax = ax1, color = "#19a824", linewidth = 1, label = '< 6 min')
gdf_germany_linestrings[~condition].plot(ax = ax1, color = "crimson", linewidth = 1, label = '>= 6 min')

# add condition for the linestrings
condition = gdf_germany_linestrings["Minutes of delay"] < 6
gdf_germany_linestrings[condition].plot(ax = ax2, color = "#19a824", linewidth = 2, label = '< 6 min')
gdf_germany_linestrings[~condition].plot(ax = ax2, color = "crimson", linewidth = 2, label = '>= 6 min')


# Add the base map
cx.add_basemap(ax = ax1, crs = gdf_germany_linestrings.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)
cx.add_basemap(ax = ax2, crs = gdf_germany_linestrings.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = True, zoom = 100)


# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_linestrings.total_bounds
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
pdf_filename = "../doc/fig/other figs/maps_KI_03_most_reliable_route_line.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")
    
    
    
    







#### MOST RELIABLE ROUTE VS FASTEST ROUTE ####

### without colormap ####

#### 02 map of Germany
# Extract LineString coordinates and create LineString geometries & point geometries
geometry_rel = [Point(xy) for xy in zip(gdf_stations_rel["Coordinate Longitude"], gdf_stations_rel["Coordinate Latitude"])]
geometry_fast = [Point(xy) for xy in zip(gdf_stations_fast["Coordinate Longitude"], gdf_stations_fast["Coordinate Latitude"])]


# Create GeoDataFrame
geo_df_rel = gpd.GeoDataFrame(gdf_stations_rel, geometry = geometry_rel, crs = "EPSG:4326")
geo_df_fast = gpd.GeoDataFrame(gdf_stations_fast, geometry = geometry_fast, crs = "EPSG:4326")


# Get a map of Germany, save as tif
germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)

# Get the shape of Germany
with rasterio.open("../doc/fig/tifs/germany_osm.tif") as r:
    west, south, east, north = tuple(r.bounds)
    germany_crs = r.crs
bb_poly = box(west, south, east, north)
bb_poly = gpd.GeoDataFrame({"geometry": [bb_poly]}, crs = germany_crs)

# Overlay with GeoDataFrame for linestrings
gdf_germany_rel = gpd.overlay(geo_df_rel, bb_poly.to_crs(geo_df_rel.crs), how = "intersection")
gdf_germany_fast = gpd.overlay(geo_df_fast, bb_poly.to_crs(geo_df_fast.crs), how = "intersection")


# Ensure the data is in the proper geographic coordinate system
gdf_germany_rel = gdf_germany_rel.to_crs(epsg = 3395)
gdf_germany_fast = gdf_germany_fast.to_crs(epsg = 3395)



#### 03 plot (full Germany map)

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data
fig, ax = plt.subplots(figsize = (4, 4))


# add condition for the points
condition = gdf_germany_rel["Minutes of delay"] >= 6
gdf_germany_rel[condition].plot(ax = ax, color = "crimson", markersize = 1, marker = "o")
gdf_germany_rel[~condition].plot(ax = ax, color = "#19a824", markersize = 1, marker = "o", label = 'Most reliable route')

condition = gdf_germany_fast["Minutes of delay"] >= 6
gdf_germany_fast[condition].plot(ax = ax, color = "crimson", markersize = 1, marker = "v")
gdf_germany_fast[~condition].plot(ax = ax, color = "#19a824", markersize = 1, marker = "v", label = 'Fastest route')


# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_rel.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)

# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_rel.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax, title = "Most reliable route vs. fastest route")

# Add labels and legend
ax.legend(loc = "upper left", frameon = False)


# Save as PDF
pdf_filename = "../doc/fig/other figs/maps_KI_03_reliable_vs_fastest_binary.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")


#### 03 plot (zoomed)

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data
fig, ax = plt.subplots(figsize = (4, 4))


# add condition for the points
condition = gdf_germany_rel["Minutes of delay"] >= 6
gdf_germany_rel[condition].plot(ax = ax, color = "crimson", markersize = 12, marker = "o")
gdf_germany_rel[~condition].plot(ax = ax, color = "#19a824", markersize = 12, marker = "o", label = 'Most reliable route')

condition = gdf_germany_fast["Minutes of delay"] >= 6
gdf_germany_fast[condition].plot(ax = ax, color = "crimson", markersize = 12, marker = "v")
gdf_germany_fast[~condition].plot(ax = ax, color = "#19a824", markersize = 12, marker = "v", label = 'Fastest route')


# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_rel.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = True)

# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_rel.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax, title = "Most reliable route vs. fastest route")

# Add labels and legend
ax.legend(loc = "lower left", frameon = False)


# Save as PDF
pdf_filename = "../doc/fig/other figs/maps_KI_03_reliable_vs_fastest_binary_zoomed.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")







#### with colormap ####


#### 02 map of Germany
# Extract LineString coordinates and create LineString geometries & point geometries
geometry_rel = [Point(xy) for xy in zip(gdf_stations_rel["Coordinate Longitude"], gdf_stations_rel["Coordinate Latitude"])]
geometry_fast = [Point(xy) for xy in zip(gdf_stations_fast["Coordinate Longitude"], gdf_stations_fast["Coordinate Latitude"])]


# Create GeoDataFrame
geo_df_rel = gpd.GeoDataFrame(gdf_stations_rel, geometry = geometry_rel, crs = "EPSG:4326")
geo_df_fast = gpd.GeoDataFrame(gdf_stations_fast, geometry = geometry_fast, crs = "EPSG:4326")


# Get a map of Germany, save as tif
germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)

# Get the shape of Germany
with rasterio.open("../doc/fig/tifs/germany_osm.tif") as r:
    west, south, east, north = tuple(r.bounds)
    germany_crs = r.crs
bb_poly = box(west, south, east, north)
bb_poly = gpd.GeoDataFrame({"geometry": [bb_poly]}, crs = germany_crs)

# Overlay with GeoDataFrame for linestrings
gdf_germany_rel = gpd.overlay(geo_df_rel, bb_poly.to_crs(geo_df_rel.crs), how = "intersection")
gdf_germany_fast = gpd.overlay(geo_df_fast, bb_poly.to_crs(geo_df_fast.crs), how = "intersection")


# Ensure the data is in the proper geographic coordinate system
gdf_germany_rel = gdf_germany_rel.to_crs(epsg = 3395)
gdf_germany_fast = gdf_germany_fast.to_crs(epsg = 3395)




#### 03 plot (zoomed)

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data
fig, ax = plt.subplots(figsize = (4, 4))


# connect both dataframes to get min / max values of both
gdf_germany_both = pd.concat([gdf_germany_rel, gdf_germany_fast])

# Apply log scaling to min & max values
log_min_delay = np.log1p(gdf_germany_both["Minutes of delay"].min())
log_max_delay = np.log1p(gdf_germany_both["Minutes of delay"].max())

# Create ScalarMappable with common normalization
norm = Normalize(vmin = log_min_delay, vmax = log_max_delay)
sm = ScalarMappable(norm = norm, cmap = "coolwarm")
sm.set_array([])

# Plot the points, create a colorbar for the points
gdf_germany_rel["color"] = gdf_germany_rel["Minutes of delay"].apply(lambda x: sm.to_rgba(np.log1p(x)))
gdf_germany_rel[gdf_germany_rel["Minutes of delay"] >= 0].plot(ax = ax, color = gdf_germany_rel.loc[gdf_germany_rel["Minutes of delay"] >= 0, "color"], markersize = 12, marker = "o", label = "Most reliable route")
gdf_germany_fast["color"] = gdf_germany_fast["Minutes of delay"].apply(lambda x: sm.to_rgba(np.log1p(x)))
gdf_germany_fast[gdf_germany_fast["Minutes of delay"] >= 0].plot(ax = ax, color = gdf_germany_fast.loc[gdf_germany_fast["Minutes of delay"] >= 0, "color"], markersize = 12, marker = "v", label = "Fastest route")


# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_rel.crs, source = "../doc/fig/tifs/germany_osm.tif", alpha = 0.7, reset_extent = True)

# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_rel.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax, title = "Most reliable route vs. fastest route")

# Add labels and legend
ax.legend(loc = "lower left", frameon = False)

# Add colorbar for the points
cbar = plt.colorbar(sm, ax = ax, label = "Minutes of delay (log scale)", orientation = "vertical", pad = 0.02, ticks = [1, 2, 3, 4, 5])

# Convert log-scaled ticks back to original scale for display
cbar_ticks_original_scale = np.expm1(cbar.get_ticks())
cbar.set_ticklabels([f"$e^{{{int(tick)}}} = {original_scale:.2f}$ minutes" for tick, original_scale in zip(cbar.get_ticks(), cbar_ticks_original_scale)])
cbar.set_label("Minutes of delay (log scaled)")

# Remove border color
cbar.outline.set_edgecolor("none")

# Save as PDF
pdf_filename = "../doc/fig/maps_KI_03_reliable_vs_fastest_zoomed.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")



#### 03 plot (zoomed) CARTO

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))

# Plot the data
fig, ax = plt.subplots(figsize = (4, 4))


# connect both dataframes to get min / max values of both
gdf_germany_both = pd.concat([gdf_germany_rel, gdf_germany_fast])

# Apply log scaling to min & max values
log_min_delay = np.log1p(gdf_germany_both["Minutes of delay"].min())
log_max_delay = np.log1p(gdf_germany_both["Minutes of delay"].max())

# Create ScalarMappable with common normalization
norm = Normalize(vmin = log_min_delay, vmax = log_max_delay)
sm = ScalarMappable(norm = norm, cmap = "coolwarm")
sm.set_array([])

# Plot the points, create a colorbar for the points
gdf_germany_rel["color"] = gdf_germany_rel["Minutes of delay"].apply(lambda x: sm.to_rgba(np.log1p(x)))
gdf_germany_rel[gdf_germany_rel["Minutes of delay"] >= 0].plot(ax = ax, color = gdf_germany_rel.loc[gdf_germany_rel["Minutes of delay"] >= 0, "color"], markersize = 12, marker = "o", label = "Most reliable route")
gdf_germany_fast["color"] = gdf_germany_fast["Minutes of delay"].apply(lambda x: sm.to_rgba(np.log1p(x)))
gdf_germany_fast[gdf_germany_fast["Minutes of delay"] >= 0].plot(ax = ax, color = gdf_germany_fast.loc[gdf_germany_fast["Minutes of delay"] >= 0, "color"], markersize = 12, marker = "v", label = "Fastest route")


# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_rel.crs, source = "../doc/fig/tifs/germany_Carto.tif", alpha = 1, reset_extent = True)

# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = gdf_germany_rel.total_bounds
west, south, east, north = bounds


# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax = ax, title = "Most reliable route vs. fastest route")

# Add labels and legend
ax.legend(loc = "lower left", frameon = False)

# Add colorbar for the points
cbar = plt.colorbar(sm, ax = ax, label = "Minutes of delay (log scale)", orientation = "vertical", pad = 0.02, ticks = [1, 2, 3, 4, 5])

# Convert log-scaled ticks back to original scale for display
cbar_ticks_original_scale = np.expm1(cbar.get_ticks())
cbar.set_ticklabels([f"$e^{{{int(tick)}}} = {original_scale:.2f}$ minutes" for tick, original_scale in zip(cbar.get_ticks(), cbar_ticks_original_scale)])
cbar.set_label("Minutes of delay (log scaled)")

# Remove border color
cbar.outline.set_edgecolor("none")

# Save as PDF
pdf_filename = "../doc/fig/maps_KI_03_reliable_vs_fastest_zoomed_Carto.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")


#### 06 mean delay of most reliable route

# get the mean delay of the fastest route
print("The mean delay of the most reliable route is", gdf_stations_rel["Minutes of delay"].mean())
print("The mean delay of the 'fastest' route (according to DB) is", gdf_stations_fast["Minutes of delay"].mean())
