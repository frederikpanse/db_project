import pandas as pd
from shapely.geometry import Point, box
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import rasterio
from tueplots import bundles
#
#
#
# #### 00 read cleaned data
# gdf_stations = pd.read_csv("../../dat/cleaned data/gdf_stations.csv", sep = ",")
# data_routes = gpd.read_file("../../dat/geo-strecke/strecken_polyline.shp")
#
#
#
# #### 01 Routes
#
# # Fastest route that Deutsche Bahn offers
# fastest_route = [80290288, #Stuttgart
#                  80290270, 80297853, 80297846, 80196212, 80297788, 80297770, 80145615, 80142620,
#                  80183079, 80142786, 80142877, 80145649, 80144147, 80140640, 80180919, 80140624,
#                  80140616, 80147124, 80182576, 80042408, 80143909, 80140236, 80140137, #Mannheim
#                  80140186, 80113324, 80113316, 80113308, 80113118, 80113092, 80113084, 80113076,
#                  80104711, 80113043, 80113035, 80112995, 80112987, 80105767, 80112953, 80113365, # Darmstadt
#                  80112813, 80112839, 80112854, 80105098, 80108555, 80107995, 80117002, 80106179 # Frankfurt Main
#                  ]
#
# # filter the data for the fastest route
# gdf_stations = gdf_stations[gdf_stations["Station or stop"].isin(fastest_route)]
#
# # create geometry column with a point object of the coordinates
# geometry = [Point(xy) for xy in zip(gdf_stations["Coordinate Longitude"], gdf_stations["Coordinate Latitude"])]
#
# # create GeoDataFrame
# geo_df = gpd.GeoDataFrame(gdf_stations, geometry = geometry, crs = "EPSG:4326")  # Use the correct CRS
#
# # merge the two datasets
# # rename the column "strecke_nr" to "route_ids"
# data_routes = data_routes.rename(columns = {"strecke_nr": "route_ids"})
# data_routes["route_ids"] = data_routes["route_ids"].astype(float)
# data_delay_routes = pd.merge(data_routes, gdf_stations, on = "route_ids", how = "right")
#
#
#
# # create new dataset with colums routes_id, geometry_x, geometry_y, Minutes of delay
# data_delay_routes = data_delay_routes[["Minutes of delay", "route_ids"]].copy()
#
# # calculate mean per route, without index column
# data_delay_routes = data_delay_routes.groupby(["route_ids"]).mean()
#
# # again merge with data_routes to get the geometry
# data_delay_routes = pd.merge(data_delay_routes, data_routes, on = "route_ids", how = "left")
#
# # group the dataset by geometry
# # data_delay_routes = data_delay_routes.groupby(["geometry"]).mean()
#
# # only take columns Minutes of delay, route_ids, geometry
# data_delay_routes = data_delay_routes[["Minutes of delay", "route_ids", "geometry"]].copy()
# data_delay_routes = data_delay_routes.groupby(["geometry"]).mean()
#
#
#
#
#
#
#
# #### 01 map of Germany
#
# # Get a map of Germany, save as tif
# germany = cx.Place("Deutschland", source = cx.providers.OpenStreetMap.Mapnik)
#
#
# # Get the shape of Germany
# with rasterio.open("tifs/germany_osm.tif") as r:
#     west, south, east, north = tuple(r.bounds)
#     germany_crs = r.crs
# bb_poly = box(west, south, east, north)
# bb_poly = gpd.GeoDataFrame({"geometry": [bb_poly]}, crs = germany_crs)
#
# gdf_germany = gpd.overlay(geo_df, bb_poly.to_crs(geo_df.crs), how = "intersection")
#
# # Ensure the data is in the proper geographic coordinate system
# gdf_germany = gdf_germany.to_crs(epsg = 3395)
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
# gdf_germany.plot(ax = ax, markersize = 0, color = "k")
#
# # Add the base map
# cx.add_basemap(ax = ax, crs = gdf_germany.crs, source = "tifs/germany_osm.tif", alpha = 0.7)
#
# # Get the bounds of the geodataframe, converted to the same CRS as the contextily basemap
# bounds = gdf_germany.total_bounds
# west, south, east, north = bounds
#
# # Get base map image for the bounds with the correct zoom level. 'll' signifies long-lat bounds
# im2, bbox = cx.bounds2img(west, south, east, north, ll = True, zoom = germany.zoom)
#
# # Plot the map with the aspect ratio fixed
# cx.plot_map(im2, bbox, ax = ax, title = "Fastest route")
#
#
# # add condition for the ploylines
# # green means no delay in mean delay per polyline (less than 6 minutes), red means delay in mean per polyline (more or equal to 6 minutes)
# condition = data_delay_routes["Minutes of delay"] < 6
# data_delay_routes[condition].plot(ax = ax, color = "#19a824", alpha = 0.9, label = "< 6 min")
# data_delay_routes[~condition].plot(ax = ax, color = "crimson", alpha = 0.7, label = ">= 6 min")
#
#
# # Add labels and legend
# ax.legend(loc = "upper left", frameon = False)
#
#
# plt.show()
#
# # #### 03 Save as PDF
# # plt.savefig("maps_KI_01_all_data_osm.pdf", bbox_inches = 'tight')