#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 16:45:37 2024

@author: Sumitrra Bala Subramaniam
"""

import geopandas as gpd
import shapely
from shapely.geometry import MultiLineString, Point, LineString
import matplotlib.pyplot as plt
import networkx as nx
import os

# Print the current working directory
print("Current working directory: {0}".format(os.getcwd()))

# Change the working directory
os.chdir('/Users/User2/Desktop/Data Literacy/Data Literacy Project')

# Confirm the change
print("Working directory changed to: {0}".format(os.getcwd()))


# Load the data
gdf = gpd.read_file('/Users/User2/Downloads/geo-strecke/strecken_polyline.shp')

# Define coordinates for Stuttgart and Frankfurt am Main
x_stuttgart, y_stuttgart = 9.18389001053732, 48.78312377049059
x_frankfurt, y_frankfurt = 8.6637837, 50.107288400393465

# Create Point objects for Stuttgart and Frankfurt am Main (without Z=0)
stuttgart_point = Point(x_stuttgart, y_stuttgart)
frankfurt_point = Point(x_frankfurt, y_frankfurt)

# Group by 'strecke_nr' and create a MultiLineString for each unique 'strecke_nr'
continuous_routes = gdf.groupby('strecke_nr')['geometry'].apply(lambda x: MultiLineString(x.tolist()))
continuous_gdf = gpd.GeoDataFrame(continuous_routes, columns=['geometry'])
continuous_gdf['strecke_nr'] = continuous_gdf.index

def find_route_connections(start_route, other_routes, threshold=50):
    connections = []
    start_route_num = start_route['strecke_nr']
    for idx, other_route in other_routes.iterrows():
        other_route_num = other_route['strecke_nr']
        # Check and handle LineString and MultiLineString for start route
        if isinstance(start_route['geometry'], LineString):
            start_geoms = [start_route['geometry']]
        elif isinstance(start_route['geometry'], MultiLineString):
            start_geoms = list(start_route['geometry'])
        
        # Check and handle LineString and MultiLineString for other route
        if isinstance(other_route['geometry'], LineString):
            other_geoms = [other_route['geometry']]
        elif isinstance(other_route['geometry'], MultiLineString):
            other_geoms = list(other_route['geometry'])

        # Check distances between all parts of start_geoms and other_geoms
        for part_start in start_geoms:
            for part_other in other_geoms:
                if part_start.distance(part_other) < threshold:
                    connections.append((start_route_num, other_route_num))
                    break
            if connections:
                break
    return connections


# Create the graph
G = nx.Graph()
for idx, route in continuous_gdf.iterrows():
    # Add each route as a node
    route_num = route['strecke_nr']
    G.add_node(route_num, pos=route['geometry'].coords[:])
    
    # Find connections to nearby routes
    connections = find_route_connections(route['geometry'], continuous_gdf, threshold=50)
    for conn in connections:
        if conn[0] != conn[1]:  # Avoid self-loops
            G.add_edge(conn[0], conn[1])

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(ax=ax, color='lightgrey', linewidth=0.5)
continuous_gdf.plot(ax=ax, color='blue', label='Continuous Routes')
ax.set_aspect('equal')
ax.legend()
plt.savefig('routes.png', dpi=300)  # Save the figure
plt.show()



"Checking how many Linestring and how many Multiline string objects we have"
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString

# Assuming gdf is your GeoDataFrame
line_count = 0
multiline_count = 0

for geometry in continuous_gdf['geometry']:
    if isinstance(geometry, LineString):
        line_count += 1
    elif isinstance(geometry, MultiLineString):
        multiline_count += 1

print("Number of LineString objects:", line_count)
print("Number of MultiLineString objects:", multiline_count)




"Plotting all continuous routes"
import folium
from shapely.geometry import MultiLineString, LineString

# Assuming continuous_gdf is your GeoDataFrame with MultiLineString geometries

# Initialize a map centered around the first geometry in your GeoDataFrame
first_geometry = continuous_gdf['geometry'].iloc[0]
x, y = first_geometry.centroid.x, first_geometry.centroid.y
m = folium.Map(location=[y, x], zoom_start=12)

# Extract only the latitude and longitude for the map's center
x, y = first_geometry.centroid.x, first_geometry.centroid.y
m = folium.Map(location=[y, x], zoom_start=12)  # No Z-coordinate


# Function to add a LineString or MultiLineString to the map
# Function to add a LineString or MultiLineString to the map
def add_line_to_map(geometry, line_map, line_color='blue'):
    if isinstance(geometry, LineString):
        # Extract only the latitude and longitude
        coords = [(lat, lon) for lon, lat, _ in geometry.coords]
        folium.PolyLine(coords, color=line_color).add_to(line_map)
    elif isinstance(geometry, MultiLineString):
        for line in geometry.geoms:
            # Extract only the latitude and longitude for each LineString
            coords = [(lat, lon) for lon, lat, _ in line.coords]
            folium.PolyLine(coords, color=line_color).add_to(line_map)


# Generate a unique color for each route
import random
def random_color():
    return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

# Iterate through the GeoDataFrame and add each route to the map
for _, row in continuous_gdf.iterrows():
    add_line_to_map(row['geometry'], m, random_color())

# Show the map
m

# Save the map to an HTML file
m.save('my_folium_map.html')

"Just two routes for each starting route in Stuttgart"
import geopandas as gpd
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import nearest_points
import folium

def get_furthest_point(geometry, reference_point):
    # ... (same as before)
    if isinstance(geometry, LineString):
        # Directly access the first and last coordinates
        coords = list(geometry.coords)
        start, end = Point(coords[0]), Point(coords[-1])
        return end if start.distance(reference_point) > end.distance(reference_point) else start
    elif isinstance(geometry, MultiLineString):
        furthest_point = None
        max_distance = 0
        for line in geometry.geoms:
            coords = list(line.coords)
            start, end = Point(coords[0]), Point(coords[-1])
            for point in [start, end]:
                distance = point.distance(reference_point)
                if distance > max_distance:
                    max_distance = distance
                    furthest_point = point
        return furthest_point
    else:
        raise TypeError("Geometry must be a LineString or MultiLineString")


def find_nearest_route(point, continuous_gdf):
    # ... (same as before)
    nearest_route = None
    min_dist = float('inf')
    for _, route in continuous_gdf.iterrows():
        nearest_pt_on_route = nearest_points(point, route['geometry'])[1]
        dist = point.distance(nearest_pt_on_route)
        if dist < min_dist:
            min_dist = dist
            nearest_route = route
    return nearest_route


def random_color():
    # ... (same as before)
    import random
    return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])


# Define Stuttgart Hbf and Frankfurt am Main Hbf points (replace with actual coordinates)
stuttgart_point = Point(9.18389001053732, 48.78312377049059)  # Replace with actual Stuttgart Hbf coordinates
frankfurt_point = Point(8.6637837, 50.107288400393465)    # Replace with actual Frankfurt am Main Hbf coordinates


stuttgart_buffer = stuttgart_point.buffer(0.01)

# Find routes within Stuttgart Hbf
stuttgart_routes = continuous_gdf[continuous_gdf.intersects(stuttgart_buffer)]  # Adjust buffer size as needed
stuttgart_routes = stuttgart_routes[stuttgart_routes.apply(lambda x: not get_furthest_point(x['geometry'], stuttgart_point).within(stuttgart_buffer), axis=1)]


# Initialize the map centered around Stuttgart
m = folium.Map(location=[stuttgart_point.y, stuttgart_point.x], zoom_start=12)

# For each route that starts within Stuttgart, find its adjacent route
for _, start_route in stuttgart_routes.iterrows():
    # Get the furthest endpoint of the starting route
    end_point = get_furthest_point(start_route['geometry'], stuttgart_point)
    
    # Find the nearest route to this endpoint
    adjacent_route = find_nearest_route(end_point, continuous_gdf)
    
    # Visualize the starting route
    add_line_to_map(start_route['geometry'], m, 'blue')
    
    # Visualize the adjacent route
    if adjacent_route is not None:  # Ensure an adjacent route was found
        add_line_to_map(adjacent_route['geometry'], m, 'red')

# Show the map
m.save('stuttgart_adjacent_routes.html')
m

print(stuttgart_routes)


# Initialize the list for overlapping routes
overlapping_routes = []

# For each route that starts within Stuttgart, find its adjacent route
for _, start_route in stuttgart_routes.iterrows():
    start_route_num = start_route['strecke_nr']
    print(f"Stuttgart Route: {start_route_num}")

    # Get the furthest endpoint of the starting route
    end_point = get_furthest_point(start_route['geometry'], stuttgart_point)
    
    # Find the nearest route to this endpoint
    adjacent_route = find_nearest_route(end_point, continuous_gdf)
    adjacent_route_num = adjacent_route['strecke_nr'] if adjacent_route is not None else None
    print(f"Adjacent Route: {adjacent_route_num}")

    # Check if the adjacent route is the same as the starting route
    if adjacent_route_num == start_route_num:
        print(f"Overlap found for route: {start_route_num}")
        overlapping_routes.append(start_route_num)

# Print all overlapping routes
if overlapping_routes:
    print("Overlapping Routes (Stuttgart route is the same as its adjacent route):")
    for route_num in overlapping_routes:
        print(route_num)
else:
    print("No overlapping routes found.")
 
   
"Third Adjacent Route"
import geopandas as gpd
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import nearest_points
import folium

# ... [Your existing functions like get_furthest_point, random_color here] ...

def find_nearest_route(point, continuous_gdf):
    nearest_route = None
    min_dist = float('inf')
    for _, route in continuous_gdf.iterrows():
        nearest_pt_on_route = nearest_points(point, route['geometry'])[1]
        dist = point.distance(nearest_pt_on_route)
        if dist < min_dist:
            min_dist = dist
            nearest_route = route
    return nearest_route

stuttgart_buffer = stuttgart_point.buffer(0.01)  # Define the buffer around Stuttgart

# Initialize the map centered around Stuttgart
m = folium.Map(location=[stuttgart_point.y, stuttgart_point.x], zoom_start=12)

# For each route that starts within Stuttgart, find its adjacent routes
for _, start_route in stuttgart_routes.iterrows():
    current_route = start_route
    end_point = get_furthest_point(current_route['geometry'], stuttgart_point)
    adjacent_route = find_nearest_route(end_point, continuous_gdf)
    
    # Visualize the starting route
    add_line_to_map(current_route['geometry'], m, 'blue')
    
    if adjacent_route is not None and not end_point.within(stuttgart_buffer):
        # Visualize the first adjacent route
        add_line_to_map(adjacent_route['geometry'], m, 'red')
        
        # Find the next adjacent route (adjacent_route_2)
        end_point_2 = get_furthest_point(adjacent_route['geometry'], end_point)
        adjacent_route_2 = find_nearest_route(end_point_2, continuous_gdf)
        
        if adjacent_route_2 is not None and not end_point_2.within(stuttgart_buffer):
            # Visualize the second adjacent route
            add_line_to_map(adjacent_route_2['geometry'], m, 'purple')

# Show the map
m.save('stuttgart_extended_routes_with_next_adjacent.html')
m



"Third Adjacent Route - Show All Route Numbers"
import geopandas as gpd
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import nearest_points
import folium

# ... [Your existing functions like get_furthest_point, random_color here] ...
def add_line_to_map(geometry, line_map, line_color, route_num):
    if isinstance(geometry, LineString):
        coords = [(lat, lon) for lon, lat, _ in geometry.coords]
        folium.PolyLine(coords, color=line_color).add_to(line_map)
        # Add a marker at the midpoint of the LineString with the route number
        mid_index = len(coords) // 2
        folium.Marker(location=coords[mid_index], 
                      popup=str(route_num),
                      icon=folium.Icon(icon_color='white', color=line_color)).add_to(line_map)
    elif isinstance(geometry, MultiLineString):
        for line in geometry.geoms:
            coords = [(lat, lon) for lon, lat, _ in line.coords]
            folium.PolyLine(coords, color=line_color).add_to(line_map)
        # Add a marker at the midpoint of the first LineString with the route number
        mid_index = len(coords) // 2
        folium.Marker(location=coords[mid_index], 
                      popup=str(route_num),
                      icon=folium.Icon(icon_color='white', color=line_color)).add_to(line_map)


def find_nearest_route(point, continuous_gdf):
    nearest_route = None
    min_dist = float('inf')
    for _, route in continuous_gdf.iterrows():
        nearest_pt_on_route = nearest_points(point, route['geometry'])[1]
        dist = point.distance(nearest_pt_on_route)
        if dist < min_dist:
            min_dist = dist
            nearest_route = route
    return nearest_route

stuttgart_buffer = stuttgart_point.buffer(0.01)  # Define the buffer around Stuttgart

# Initialize the map centered around Stuttgart
m = folium.Map(location=[stuttgart_point.y, stuttgart_point.x], zoom_start=12)

# For each route that starts within Stuttgart, find its adjacent routes
for _, start_route in stuttgart_routes.iterrows():
    current_route = start_route
    end_point = get_furthest_point(current_route['geometry'], stuttgart_point)
    adjacent_route = find_nearest_route(end_point, continuous_gdf)
    
    # Visualize the starting route with route number
    add_line_to_map(current_route['geometry'], m, 'blue', start_route['strecke_nr'])
    
    if adjacent_route is not None and not end_point.within(stuttgart_buffer):
        # Visualize the first adjacent route with route number
        add_line_to_map(adjacent_route['geometry'], m, 'red', adjacent_route['strecke_nr'])
        
        # Find the next adjacent route (adjacent_route_2)
        end_point_2 = get_furthest_point(adjacent_route['geometry'], end_point)
        adjacent_route_2 = find_nearest_route(end_point_2, continuous_gdf)
        
        if adjacent_route_2 is not None and not end_point_2.within(stuttgart_buffer):
            # Visualize the second adjacent route with route number
            add_line_to_map(adjacent_route_2['geometry'], m, 'purple', adjacent_route_2['strecke_nr'])

# Show the map
m.save('stuttgart_extended_routes_with_next_adjacent.html')
m




"Strecke 4801 - from Bietigheim"
#We choose this route as the start route from Stuttgart as it seems the most likely to move in the direction of Frankfurt
# Find the endpoint of "strecke 4801"
strecke_4801 = continuous_gdf[continuous_gdf['strecke_nr'] == 4801]
endpoint_4801 = get_furthest_point(strecke_4801.iloc[0]['geometry'], stuttgart_point)

# Find all routes and their distances to the endpoint of "strecke 4801"
distances = []
for _, route in continuous_gdf.iterrows():
    if route['strecke_nr'] != 4801:  # Exclude "strecke 4801" itself
        nearest_pt_on_route = nearest_points(endpoint_4801, route['geometry'])[1]
        distance = endpoint_4801.distance(nearest_pt_on_route)
        distances.append((route['strecke_nr'], distance, route['geometry']))

# Select the nearest 5 routes to the endpoint of "strecke 4801"
nearest_routes = sorted(distances, key=lambda x: x[1])[:5]

# Determine which route is closest to Frankfurt am Main
min_distance_to_frankfurt = float('inf')
route_closest_to_frankfurt = None
for strecke_nr, _, geometry in nearest_routes:
    nearest_pt_to_frankfurt = nearest_points(geometry, frankfurt_point)[0]
    distance_to_frankfurt = nearest_pt_to_frankfurt.distance(frankfurt_point)
    if distance_to_frankfurt < min_distance_to_frankfurt:
        min_distance_to_frankfurt = distance_to_frankfurt
        route_closest_to_frankfurt = strecke_nr

# Initialize the map centered around the endpoint of "strecke 4801"
m = folium.Map(location=[endpoint_4801.y, endpoint_4801.x], zoom_start=10)

# Add "strecke 4801" to the map
add_line_to_map(strecke_4801.iloc[0]['geometry'], m, 'blue', 4801)

# Add the nearest routes to the map
for strecke_nr, _, geometry in nearest_routes:
    color = 'green' if strecke_nr == route_closest_to_frankfurt else 'orange'
    add_line_to_map(geometry, m, color, strecke_nr)

# Show the map
m.save('strecke_4801_and_nearest_routes.html')
m



"Incomplete path to Frankfurt am Main"
#This was done to manually find the subsequent routes to Frankfurt, starting from Stuttgart
# Find "strecke 4801"
def find_nearby_routes(endpoint, continuous_gdf, exclude_route, max_routes=5):
    distances = []
    for _, route in continuous_gdf.iterrows():
        if route['strecke_nr'] != exclude_route:  # Exclude the specified route
            nearest_pt_on_route = nearest_points(endpoint, route['geometry'])[1]
            distance = endpoint.distance(nearest_pt_on_route)
            distances.append((route['strecke_nr'], distance, route['geometry']))

    # Select the nearest routes to the endpoint
    nearest_routes = sorted(distances, key=lambda x: x[1])[:max_routes]
    return nearest_routes

def find_route_closest_to_point(nearest_routes, target_point):
    min_distance_to_target = float('inf')
    route_closest_to_target = None
    route_closest_to_target_geometry = None
    for strecke_nr, _, geometry in nearest_routes:
        nearest_pt_to_target = nearest_points(geometry, target_point)[0]
        distance_to_target = nearest_pt_to_target.distance(target_point)
        if distance_to_target < min_distance_to_target:
            min_distance_to_target = distance_to_target
            route_closest_to_target = strecke_nr
            route_closest_to_target_geometry = geometry

    return route_closest_to_target, route_closest_to_target_geometry

strecke_4801 = continuous_gdf[continuous_gdf['strecke_nr'] == 4801]

# Find the endpoint of "strecke 4801"
endpoint_4801 = get_furthest_point(strecke_4801.iloc[0]['geometry'], stuttgart_point)

# Find the nearest routes to the endpoint of "strecke 4801"
nearest_routes = find_nearby_routes(endpoint_4801, continuous_gdf, 4801)

# Identify the route leading closest to Frankfurt am Main from those near "strecke 4801"
route_closest_to_frankfurt, route_closest_to_frankfurt_geometry = find_route_closest_to_point(nearest_routes, frankfurt_point)

# Find the endpoint of the route leading closest to Frankfurt am Main
endpoint_closest_to_frankfurt = get_furthest_point(route_closest_to_frankfurt_geometry, stuttgart_point)

# Find the nearest routes to the endpoint of the route closest to Frankfurt am Main
next_nearest_routes = find_nearby_routes(endpoint_closest_to_frankfurt, continuous_gdf, route_closest_to_frankfurt)

# Identify the next route leading closest to Frankfurt am Main from those near the previous closest route
next_route_closest_to_frankfurt, _ = find_route_closest_to_point(next_nearest_routes, frankfurt_point)

# Initialize the map centered around Stuttgart
m = folium.Map(location=[stuttgart_point.y, stuttgart_point.x], zoom_start=8)

# Add "strecke 4801" to the map
add_line_to_map(strecke_4801.iloc[0]['geometry'], m, 'blue', 4801)

# Add the route closest to Frankfurt am Main to the map
add_line_to_map(route_closest_to_frankfurt_geometry, m, 'green', route_closest_to_frankfurt)

# Add the next route closest to Frankfurt am Main to the map
for strecke_nr, _, geometry in next_nearest_routes:
    color = 'purple' if strecke_nr == next_route_closest_to_frankfurt else 'orange'
    add_line_to_map(geometry, m, color, strecke_nr)

# Show the map
m.save('incomplete_path_to_frankfurt.html')
m


"Finding the best routes to Frankfurt am Main"
import geopandas as gpd
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import nearest_points
import folium

# Define the functions (same as before)
#def get_furthest_point(geometry, reference_point):
    # ...

#def find_nearest_route(point, continuous_gdf):
    # ...

#def add_line_to_map(geometry, line_map, line_color, route_num):
    # ...

#def find_nearby_routes(endpoint, continuous_gdf, exclude_route, max_routes=10):
    # ...

#def find_route_closest_to_point(nearest_routes, target_point):
    # ...

# Initialize the map and key points
m = folium.Map(location=[stuttgart_point.y, stuttgart_point.x], zoom_start=8)
stuttgart_point = Point(9.18389001053732, 48.78312377049059)
frankfurt_point = Point(8.6637837, 50.107288400393465)
frankfurt_buffer = frankfurt_point.buffer(0.1)  # Define the buffer around Frankfurt am Main

# Initialize a list to store processed route numbers
processed_routes = []

def process_routes(route, route_geometry, target_point, continuous_gdf, map_obj, processed_list, depth=0, max_depth=4):
    if depth > max_depth:  # Limit the depth of recursion
        return
    
    # Find the nearest routes to the endpoint of the current route
    endpoint = get_furthest_point(route_geometry, stuttgart_point)
    nearest_routes = find_nearby_routes(endpoint, continuous_gdf, route, max_routes=10)
    
    # Filter down to the max 5 routes that lead nearest to the destination
    closest_routes = sorted(nearest_routes, key=lambda x: nearest_points(x[2], target_point)[0].distance(target_point))[:5]
    
    # Iterate through these routes
    for strecke_nr, _, geometry in closest_routes:
        # Append route number to the list
        processed_list.append(strecke_nr)

        # Check if the route leads into the Frankfurt am Main buffer region
        if geometry.intersects(frankfurt_buffer):
            # Highlight the route leading to Frankfurt am Main
            add_line_to_map(geometry, map_obj, 'green', strecke_nr)
        else:
            # Add the route to the map
            add_line_to_map(geometry, map_obj, 'blue', strecke_nr)

        # Recursively process the next routes
        process_routes(strecke_nr, geometry, target_point, continuous_gdf, map_obj, processed_list, depth=depth + 1, max_depth=max_depth)

# Start the process with "strecke 4801"
strecke_4801 = continuous_gdf[continuous_gdf['strecke_nr'] == 4801].iloc[0]
process_routes(4801, strecke_4801['geometry'], frankfurt_point, continuous_gdf, m, processed_routes)


# Save the map
m.save('complete_paths_to_frankfurt_from_4801.html')


# Now, processed_routes contains all the route numbers processed in the function
print("Processed Routes:", processed_routes)



"Add stations to the Map"
#This is just to visualize all the stations in Germany - the data is obtained from a different dataset, which does not include route data
import folium
import pandas as pd

# Load the data
data_delay = pd.read_csv('/Users/User2/Desktop/Data Literacy/Data Literacy Project/db_data_2016.csv', delimiter=';')

# Filter the DataFrame based on the condition
data_delay = data_delay[data_delay['Country_y'] == 'DEUTSCHLAND']

# Drop all NaN values
data_delay = data_delay.dropna()

# Group by 'Station or stop'
grouped_delay = data_delay.groupby('Station or stop').agg({
    'Name': 'first',  # Assuming the name is the same for all entries of each station
    'Number of train rides': 'mean',
    'Minutes of delay': 'mean',
    'Coordinate Latitude': 'mean',
    'Coordinate Londitude': 'mean'
}).reset_index()


# Assuming you have a Folium map object named 'm'
# If not, create one centered around a general location in Germany
# m = folium.Map(location=[51.1657, 10.4515], zoom_start=6)

# Add non-interactive dots for each train station to the map
for _, row in grouped_delay.iterrows():
    folium.CircleMarker(
        location=[row['Coordinate Latitude'], row['Coordinate Londitude']],
        radius=3,  # Small radius for dot-like appearance
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=1.0  # Fully opaque dots
    ).add_to(m)

# Save the map with the non-interactive dots added
m.save('complete_paths_to_frankfurt_with_stations_non_interactive.html')
m





"Find the nearest route to each station and create dataframe"
#Here, we attemot to merge the stations from the "station and delay dataset" to the corresponding routes closest to them from the "route dataset"
import pandas as pd
from shapely.geometry import Point
from shapely.ops import nearest_points
import geopandas as gpd
from tqdm import tqdm

# Assuming continuous_gdf is already a GeoDataFrame with CRS defined
# If not, convert it and define the CRS (coordinate reference system)
# continuous_gdf = gpd.GeoDataFrame(continuous_gdf, geometry='geometry')
# continuous_gdf.crs = {'init': 'epsg:4326'}  # or whichever is appropriate


def find_nearest_routes_for_stations(routes_gdf, stations_df, distance_threshold=0.01):
    # Initialize DataFrame to store the station and its corresponding nearest route
    stations_with_routes = pd.DataFrame(columns=['Station or stop', 'Route', 'Distance'])

    # Iterate over each station with tqdm
    for _, station in tqdm(stations_df.iterrows(), total=stations_df.shape[0], desc="Processing stations"):
        station_location = Point(station['Coordinate Londitude'], station['Coordinate Latitude'])
        nearest_route = None
        min_dist = float('inf')

        # Iterate over each route to find the nearest one
        for route_num in routes_gdf['strecke_nr'].unique():
            route_geometry = routes_gdf[routes_gdf['strecke_nr'] == route_num].iloc[0].geometry
            nearest_point = nearest_points(station_location, route_geometry)[1]
            distance = station_location.distance(nearest_point)

            # Update nearest route if this route is closer
            if distance <= distance_threshold and distance < min_dist:
                min_dist = distance
                nearest_route = route_num

        # Add the nearest route and its distance to the DataFrame
        if nearest_route is not None:
            new_row = pd.DataFrame({
                'Station or stop': [station['Station or stop']],
                'Route': [nearest_route],
                'Distance': [min_dist]
            })
            stations_with_routes = pd.concat([stations_with_routes, new_row], ignore_index=True)

    return stations_with_routes

# Call the function with your GeoDataFrame and stations DataFrame
stations_with_nearest_routes = find_nearest_routes_for_stations(continuous_gdf, grouped_delay)

# Save the new dataset
stations_with_nearest_routes.to_csv('stations_with_nearest_routes.csv', index=False)
print(stations_with_nearest_routes)

"Match all the station information with this new dataframe of stations and routes"
# Merge with the grouped_delay DataFrame to retain other columns
stations_with_routes_full = pd.merge(grouped_delay, stations_with_nearest_routes, on='Station or stop')

# Save the new dataset
stations_with_routes_full.to_csv('stations_with_routes_full.csv', index=False)
print(stations_with_routes_full)


"All Paths from Stuttgart to Frankfurt am Main"
#Here we do the same as before, in that we find all connected routes from Stuttgart to Frankfurt, but we define a full connection as a single direct path
def build_all_paths(current_route, current_path, target_point, continuous_gdf, all_paths, max_depth=3, depth=0):
    if depth > max_depth:
        return

    # Get the endpoint of the current route
    endpoint = get_furthest_point(continuous_gdf[continuous_gdf['strecke_nr'] == current_route].iloc[0]['geometry'], stuttgart_point)
    
    # Find nearby routes
    nearby_routes = find_nearby_routes(endpoint, continuous_gdf, current_route, max_routes=10)
    
    # Check if any of these routes lead directly to Frankfurt am Main
    for strecke_nr, _, geometry in nearby_routes:
        new_path = current_path + [strecke_nr]
        if geometry.intersects(frankfurt_buffer):
            all_paths.append(new_path)  # Add the path as it leads to Frankfurt am Main
        else:
            # Continue building the path if it doesn't lead to Frankfurt am Main yet
            build_all_paths(strecke_nr, new_path, target_point, continuous_gdf, all_paths, max_depth, depth=depth+1)

# Initialize the list for all paths
all_paths = []

# Start building paths from 'strecke 4801'
build_all_paths(4801, [4801], frankfurt_point, continuous_gdf, all_paths, max_depth=3)

# Now you can visualize the paths as before
print("All Possible Paths from Stuttgart to Frankfurt am Main: ", all_paths)



"Visualize all Paths from Stuttgart to Frankfurt am Main"
import folium
import random

# Initialize the map centered around Stuttgart
m = folium.Map(location=[stuttgart_point.y, stuttgart_point.x], zoom_start=8)

def random_color():
    """Generate a random hex color."""
    return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

def add_line_to_map(geometry, line_map, line_color):
    """Function to add LineString or MultiLineString to the map."""
    if isinstance(geometry, LineString):
        coords = [(lat, lon) for lon, lat, _ in geometry.coords]
        folium.PolyLine(coords, color=line_color).add_to(line_map)
    elif isinstance(geometry, MultiLineString):
        for line in geometry.geoms:
            coords = [(lat, lon) for lon, lat, _ in line.coords]
            folium.PolyLine(coords, color=line_color).add_to(line_map)

# Add each path to the map in a different color
for path in all_paths:
    path_color = random_color()
    for route_num in path:
        route_geometry = continuous_gdf[continuous_gdf['strecke_nr'] == route_num].iloc[0]['geometry']
        add_line_to_map(route_geometry, m, path_color)

# Save the map
m.save('all_paths_to_frankfurt.html')

# Display the map (if in Jupyter Notebook)
m




"Find Total Delays along all Paths from Stuttgart to Frankfurt am Main"
# Load required datasets
stations_with_routes_full = pd.read_csv('stations_with_routes_full.csv')

# Initialize DataFrame to store path delays
path_delays_df = pd.DataFrame(columns=['Path', 'Total Delay'])

# Calculate the average delays for each path
for path_index, path in enumerate(all_paths):
    total_delay = 0
    for route in path:
        # Filter stations for the current route
        stations_on_route = stations_with_routes_full[stations_with_routes_full['Route'] == route]
        
        # Calculate the sum of average delays for each station
        for _, station in stations_on_route.iterrows():
            individual_delay = station['Minutes of delay'] / station['Number of train rides']
            total_delay += individual_delay
    
    # Add the total delay of the path to the DataFrame
    path_delays_df.loc[path_index] = [' -> '.join(map(str, path)), total_delay]

# Save the DataFrame
path_delays_df.to_csv('path_delays.csv', index=False)
print(path_delays_df)




"Plot Path with the Least Delays"
import folium
import random

# Load the path delays data
path_delays_df = pd.read_csv('path_delays.csv')
stations_with_routes_full = pd.read_csv('stations_with_routes_full.csv')

# Identify the path with the least delay
least_delay_path = path_delays_df.loc[path_delays_df['Total Delay'].idxmin()]['Path']
least_delay_path_routes = least_delay_path.split(' -> ')

# Convert route numbers in least_delay_path_routes to integers
least_delay_path_routes = [int(route) for route in least_delay_path_routes]

# Initialize the map centered around Stuttgart
m = folium.Map(location=[stuttgart_point.y, stuttgart_point.x], zoom_start=8)

def random_color():
    """Generate a random hex color."""
    return "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])

def add_line_to_map(geometry, line_map, line_color, strecke_nr):
    """Function to add LineString or MultiLineString to the map."""
    if isinstance(geometry, LineString):
        coords = [(lat, lon) for lon, lat, _ in geometry.coords]
        folium.PolyLine(coords, color=line_color, popup=f"Strecke {strecke_nr}").add_to(line_map)
    elif isinstance(geometry, MultiLineString):
        for line in geometry.geoms:
            coords = [(lat, lon) for lon, lat, _ in line.coords]
            folium.PolyLine(coords, color=line_color, popup=f"Strecke {strecke_nr}").add_to(line_map)

# Add all paths to the map with random colors
for path in all_paths:
    path_color = random_color() if path != least_delay_path_routes else '#013220'  # Dark green for least delay path
    for route_num in path:
        route_geometry = continuous_gdf[continuous_gdf['strecke_nr'] == route_num].iloc[0]['geometry']
        add_line_to_map(route_geometry, m, path_color, route_num)

# Add interactive markers for each station along the least delay path
for _, station in stations_with_routes_full.iterrows():
    if station['Route'] in least_delay_path_routes:
        folium.CircleMarker(
            location=[station['Coordinate Latitude'], station['Coordinate Londitude']],
            radius=5,  # Slightly larger for visibility
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=1.0,
            popup=f"{station['Name']} - Delay: {station['Minutes of delay']} min"
        ).add_to(m)

# Save the map
m.save('highlighted_least_delay_path_with_stations.html')