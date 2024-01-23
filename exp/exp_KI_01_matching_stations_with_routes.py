import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString


#### 00 read data
data_routes = gpd.read_file("../dat/geo-strecke/strecken_polyline.shp")
data_mean = pd.read_csv("../doc/fig/data_mean.csv", sep = ";")

# Create GeoDataFrame for routes
gdf_routes = gpd.GeoDataFrame(data_routes, geometry = 'geometry')

# Create GeoDataFrame for stations with coordinates
gdf_stations = gpd.GeoDataFrame(data_mean, geometry = gpd.points_from_xy(data_mean["Coordinate Longitude"], data_mean["Coordinate Latitude"]))

# add an empty column that will save the routes later on
gdf_stations["route_ids"] = None



#### 01 get the route ids for each station

# define a function that gets the distance from the point (= station or stop that measured the delay) to the polyline (that is a section of a route)
def is_point_on_line(point_coords, line_coords):
    # get the distance from the point to the line
    distance = point_coords.distance(line_coords)
    return distance

# Example usage
point_coordinates = Point(9.38343, 54.74377)  # Example point coordinates
line_coordinates = LineString([(9.38321, 54.74343), (9.38343, 54.74377), (9.38390, 54.74458), (9.38390, 54.74459)])  # Example line coordinates

result = is_point_on_line(point_coordinates, line_coordinates)

if result < 0.01:
    print("In this example, the point is close to the line.")
else:
    print("In this example, the point is not close to the line.")


#### THE FOLLOWING LINES (CURRENTLY A COMMENT) TAKE A LONG TIME TO RUN, SO I SAVED THE RESULT AS CSV
# # apply on the real data:
# # check the distance of every station to every route
# for row_route in gdf_routes["geometry"]:
#     for row_point in gdf_stations["geometry"]:
#         dist = is_point_on_line(row_point, row_route)
#
#         # if the distance is less than our threshold of 0.01 (which should translate to 0.7 to 1.11 km, depending on the latitude or longitude), we assume that the station is on the route
#         if dist < 0.01:
#             # get the indices of the rows
#             index_point = gdf_stations.index.get_loc(gdf_stations[gdf_stations['geometry'] == row_point].index[0])
#             index_route = gdf_routes.index.get_loc(gdf_routes[gdf_routes['geometry'] == row_route].index[0])
#
#             # only add the corresponding "strecken_nr" (that we get from the route-dataset) to the column, if it's a match
#             gdf_stations["route_ids"].loc[index_point] = gdf_routes["strecke_nr"].loc[index_route]
#
#
# # fill NaN values with 0
# gdf_stations["route_ids"] = gdf_stations["route_ids"].fillna(0)
# # save the dataframe as csv
# gdf_stations.to_csv("../dat/cleaned data/gdf_stations.csv", index = False, header = True)



# to safe time: load the dataset
gdf_stations = pd.read_csv("../dat/cleaned data/gdf_stations.csv")




#### 02 Look at the data

# sanity check
print(len(data_mean))
print(len(gdf_stations))

# -> this matches



# how many routes do we have?
print(len(gdf_stations["route_ids"].unique()))
print(len(data_routes["strecke_nr"].unique()))

# -> there are some routes that have no data for the delay...



def get_data_gdf():
    return gdf_stations