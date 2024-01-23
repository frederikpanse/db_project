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
gdf_stations_rel = gdf_stations[gdf_stations["route_ids"].isin(rel_path)]




#### 01 Routes

# Fastest route that Deutsche Bahn offers
fastest_route = [80290288, #Stuttgart
                 80290270, 80297853, 80297846,
                 80297788, 80297770, 80145615,
                 80142620,
                 80183079, 80142786, 80142877,
                 80144147, 80140640, 80180919,
                 80143909, 80140236, 80140137, #Mannheim
                 80140186, 80113324, 80113316, 80113308,
                 80113092, 80113084, 80113076,
                 80104711, 80113043, 80113035, 80112995, 80112987, 80105767, 80112953, 80113365, # Darmstadt
                 80112813, 80112839, 80112854, 80105098, 80108555, 80107995 # Frankfurt Main
                 ]

# filter the data for the fastest route
gdf_stations_fast = gdf_stations[gdf_stations["Station or stop"].isin(fastest_route)]



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
with rasterio.open("tifs/germany_osm.tif") as r:
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
cx.add_basemap(ax = ax, crs = gdf_germany_rel.crs, source = "tifs/germany_osm.tif", alpha = 0.7, reset_extent = False)

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
pdf_filename = "maps_KI_06_reliable_vs_fastest.pdf"
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
gdf_germany_rel[condition].plot(ax = ax, color = "crimson", markersize = 10, marker = "o")
gdf_germany_rel[~condition].plot(ax = ax, color = "#19a824", markersize = 10, marker = "o", label = 'Most reliable route')

condition = gdf_germany_fast["Minutes of delay"] >= 6
gdf_germany_fast[condition].plot(ax = ax, color = "crimson", markersize = 10, marker = "v")
gdf_germany_fast[~condition].plot(ax = ax, color = "#19a824", markersize = 10, marker = "v", label = 'Fastest route')


# Add the base map
cx.add_basemap(ax = ax, crs = gdf_germany_rel.crs, source = "tifs/germany_osm.tif", alpha = 0.7, reset_extent = True)

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
pdf_filename = "maps_KI_06_reliable_vs_fastest_zoomed.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches = "tight")
    print(f"Plot saved as {pdf_filename}")





#### 06 mean delay of most reliable route

# get the mean delay of the fastest route
print("The mean delay of the most reliable route is", gdf_stations_rel["Minutes of delay"].mean())
print("The mean delay of the 'fastest' route (according to DB) is", gdf_stations_fast["Minutes of delay"].mean())