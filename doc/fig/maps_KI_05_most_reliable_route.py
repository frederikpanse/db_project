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
data_routes = gpd.read_file("../../dat/geo-strecke/strecken_polyline.shp")
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


# create geometry column with a point object of the coordinates
geometry = [Point(xy) for xy in zip(gdf_stations["Coordinate Longitude"], gdf_stations["Coordinate Latitude"])]

# create GeoDataFrame
geo_df = gpd.GeoDataFrame(gdf_stations, geometry = geometry, crs = "EPSG:4326")  # Use the correct CRS

# merge the two datasets
# rename the column "strecke_nr" to "route_ids"
data_routes = data_routes.rename(columns = {"strecke_nr": "route_ids"})
data_routes["route_ids"] = data_routes["route_ids"].astype(float)
data_delay_routes = pd.merge(data_routes, gdf_stations, on = "route_ids", how = "right")



# create new dataset with colums routes_id, geometry_x, geometry_y, Minutes of delay
data_delay_routes = data_delay_routes[["Minutes of delay", "route_ids"]].copy()

# calculate mean per route, without index column
data_delay_routes = data_delay_routes.groupby(["route_ids"]).mean()

# again merge with data_routes to get the geometry
data_delay_routes = pd.merge(data_delay_routes, data_routes, on = "route_ids", how = "left")

# group the dataset by geometry
# data_delay_routes = data_delay_routes.groupby(["geometry"]).mean()

# only take columns Minutes of delay, route_ids, geometry
data_delay_routes = data_delay_routes[["Minutes of delay", "route_ids", "geometry"]].copy()
data_delay_routes = data_delay_routes.groupby(["geometry"], as_index = False).mean()



#### 02 map of Germany
# Extract LineString coordinates and create LineString geometries
geometry_linestrings = [LineString(x) for x in data_delay_routes["geometry"]]

# Create GeoDataFrame for linestrings
geo_df_linestrings = gpd.GeoDataFrame(data_delay_routes, geometry = geometry_linestrings, crs = "EPSG:4326")

# Get a map of Germany, save as tif
germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)

# Get the shape of Germany
with rasterio.open("tifs/germany_osm.tif") as r:
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
cx.add_basemap(ax = ax, crs = gdf_germany_linestrings.crs, source = "tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)


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
pdf_filename = "maps_KI_05_most_reliable_route_full.pdf"
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
cx.add_basemap(ax = ax, crs = gdf_germany_linestrings.crs, source = "tifs/germany_osm.tif", alpha = 0.7, reset_extent = True)


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
pdf_filename = "maps_KI_05_most_reliable_route_zoomed.pdf"
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
cx.add_basemap(ax = ax1, crs = gdf_germany_linestrings.crs, source = "tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)
cx.add_basemap(ax = ax2, crs = gdf_germany_linestrings.crs, source = "tifs/germany_osm.tif", alpha = 0.7, reset_extent = True, zoom = 100)


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
pdf_filename = "maps_KI_05_most_reliable_route.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")



#### 06 mean delay of most reliable route

# get the mean delay of the fastest route
print("The mean delay of the 'fastest' route (according to DB) is", data_delay_routes["Minutes of delay"].mean())