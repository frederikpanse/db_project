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

map = cx.Place("Rhein", source = cx.providers.CartoDB.Positron, path = "map_Carto.tif")


#### 03 plot (zoomed) CARTO

# set plotting stylesheet
plt.rcParams.update(bundles.icml2022(column="half", nrows=1, ncols=2, usetex=False))

# Plot the data
fig, ax = plt.subplots(figsize=(3, 3))

# connect both dataframes to get min / max values of both

# Apply log scaling to min & max values
log_min_delay = np.log1p(geo_df["Minutes of delay"].min())
log_max_delay = np.log1p(geo_df["Minutes of delay"].max())

# create colormap
colorscheme = LinearSegmentedColormap.from_list(
    "colorscheme", [rgb.tue_blue, rgb.tue_mauve, rgb.tue_ocre], N = 500)

# Create ScalarMappable with common normalization
norm = Normalize(vmin=log_min_delay, vmax=log_max_delay)
sm = ScalarMappable(norm=norm, cmap=colorscheme)
sm.set_array([])

# Plot the points, create a colorbar for the points
geo_df["color"] = geo_df["Minutes of delay"].apply(lambda x: sm.to_rgba(np.log1p(x)))
geo_df[geo_df["Minutes of delay"] >= 0].plot(ax=ax, color=geo_df.loc[
    geo_df["Minutes of delay"] >= 0, "color"],
                                                               markersize=12, marker="o",
                                                               label="Most reliable route, \nmean delay = {}".format(
                                                                   round(gdf_stations_rel["Minutes of delay"].mean(),
                                                                         2)))

# Add the base map
cx.add_basemap(ax=ax, crs=geo_df.crs, source="map_Carto.tif", alpha=1, reset_extent=True)

# Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
bounds = geo_df.total_bounds
west, south, east, north = bounds

# Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
im2, bbox = cx.bounds2img(west, south, east, north)

# Plot the map with the aspect ratio fixed
cx.plot_map(im2, bbox, ax=ax)  # title = "Most reliable route vs. fastest route"

# Add labels and legend
ax.legend(loc="lower left", frameon=False)

# Add colorbar for the points
cbar = plt.colorbar(sm, ax=ax, label="Minutes of delay (log scale)", orientation="vertical", pad=0.02,
                    ticks=[1, 2, 3, 4, 5])

# Convert log-scaled ticks back to original scale for display
cbar_ticks_original_scale = np.expm1(cbar.get_ticks())
rounded_ticks = [round(tick) if tick % 1 else int(tick) for tick in cbar_ticks_original_scale]
cbar.set_ticklabels([f"{int(original_scale)} min" for original_scale in rounded_ticks])
cbar.set_label("Minutes of delay (log scaled)")

# Remove border color
cbar.outline.set_edgecolor("none")

# Save as PDF
pdf_filename = "maps_KI_03_reliable_vs_fastest_zoomed_Carto.pdf"
with PdfPages(pdf_filename) as pdf:
    pdf.savefig(fig, bbox_inches="tight")
    print(f"Plot saved as {pdf_filename}")

#### 06 mean delay of most reliable route

# get the mean delay of the fastest route
print("The mean delay of the most reliable route is", geo_df["Minutes of delay"].mean())

