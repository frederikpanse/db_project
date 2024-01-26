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
from matplotlib.colors import LinearSegmentedColormap
from tueplots.constants.color import rgb


rb = LinearSegmentedColormap.from_list(
    "rb", [rgb.tue_blue, rgb.tue_lightgold, rgb.tue_ocre], N=500
)


# show the colormap for testing
fig, ax = plt.subplots(figsize=(6, 1))
fig.subplots_adjust(bottom=0.5)
cb1 = mpl.colorbar.ColorbarBase(ax, cmap=rb,
                                orientation='horizontal')
plt.show()


#### 00 read cleaned data
from ipynb.fs.full.exploration_cleaning import get_data
from ipynb.fs.full.exploration_cleaning import get_paths

data = get_data(which="mean")
path_delays = get_paths()
gdf_stations = pd.read_csv("../dat/stations_with_nearest_routes.csv", sep=",")
data_routes = gpd.read_file("../dat/geo-strecke/strecken_polyline.shp")

print("There are {} unique routes we found.".format(len(path_delays)))

#### 01 Routes

## 1.1 Most reliable route
# get the route with the least delay = most reliable route
paths_sorted = sorted(path_delays.items(), key=lambda x: x[1]["mean_delay"])
rel_path = paths_sorted[0][1]["routes"]
print("The optimal route is: {}".format(rel_path))
print(paths_sorted[0][1]["mean_delay"])

# filter the data for the rel_path
gdf_stations_rel = gdf_stations[gdf_stations["Route"].isin(rel_path)]

# merge with data
gdf_stations_rel = gdf_stations_rel.merge(data, on="Station or stop")


geometry_points = [Point(xy) for xy in
                   zip(gdf_stations_rel["Coordinate Longitude"], gdf_stations_rel["Coordinate Latitude"])]


# Create GeoDataFrame
geo_df = gpd.GeoDataFrame(gdf_stations_rel, geometry=geometry_points, crs="EPSG:4326")

map = cx.Place("Baden", source = cx.providers.CartoDB.Positron, path = "map_Carto.tif")


#
# Frankfurt = cx.Place("Heidelberg", source = cx.providers.CartoDB.Positron, path = "Frankfurt_Carto.tif")
#
#
# # Get the shape of Germany
# with rasterio.open("Frankfurt_Carto.tif") as r:
#     west, south, east, north = tuple(r.bounds)
#     Frankfurt_crs = r.crs
# bb_poly = box(west, south, east, north)
# bb_poly = gpd.GeoDataFrame({"geometry": [bb_poly]}, crs = Frankfurt_crs)
#
#
# gdf_Frankfurt = gpd.overlay(geo_df, bb_poly.to_crs(geo_df.crs), how = "intersection")
#
# # Ensure the data is in the proper geographic coordinate system
# gdf_Frankfurt = gdf_Frankfurt.to_crs(epsg = 3395)
#
#
#
#
# #### 02 plot
#
# # set plotting stylesheet
# plt.rcParams.update(bundles.icml2022(column = "half", nrows = 1, ncols = 2, usetex = False))
#
# # Plot the data
# fig, ax = plt.subplots(figsize = (4, 4))
# geo_df.plot(ax = ax, markersize = 0, color = "k")
#
# # Add the base map
# cx.add_basemap(ax = ax, crs = geo_df.crs, source = "Frankfurt_Carto.tif", alpha = 1)
#
# # Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
# bounds = geo_df.total_bounds
# west, south, east, north = bounds
#
# # Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
# im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = Frankfurt.zoom)
#
# # Plot the map with the aspect ratio fixed
# cx.plot_map(im2, bbox, ax = ax) # title = "Mean delay of trains in 2016 in Germany"
#
# plt.show()