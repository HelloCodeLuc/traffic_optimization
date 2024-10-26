import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from collections import defaultdict
import os

# Get the current working directory
current_directory = os.getcwd()

# Print the current working directory
print("Current Working Directory:", current_directory)

# Parse the XML file
file_path = r'(current_directory)\..\NETWORKS\school-extended.net.xml'

try:
    tree = ET.parse(file_path)
    root = tree.getroot()
except Exception as e:
    print(f"An error occurred: {e}")
    exit()

# Initialize lists for nodes, edges, and lane speeds
nodes = []
edges = []
lane_speeds = defaultdict(lambda: {'dir1': [], 'dir2': []})

# Extract nodes, edges, and lane speeds from the XML file
for edge in root.findall(".//edge"):
    edge_id = edge.get('id')
    for lane in edge.findall(".//lane"):
        shape = lane.get('shape')
        speed = float(lane.get('speed'))
        if shape:
            points = shape.split(' ')
            node_coords = [tuple(map(float, point.split(','))) for point in points]
            nodes.extend(node_coords)

            # Store each consecutive pair of coordinates as an edge
            for i in range(len(node_coords) - 1):
                edges.append((node_coords[i], node_coords[i + 1], edge_id))  # Include edge_id

                # Simulating lane directionality with odd/even logic for demo purposes
                if len(edges) % 2 == 0:
                    lane_speeds[edge_id]['dir1'].append(speed)
                else:
                    lane_speeds[edge_id]['dir2'].append(speed)

                # Debug: Check if the speeds are correctly added
                print(f"Edge: {edge_id}, Direction 1 Speeds: {lane_speeds[edge_id]['dir1']}, Direction 2 Speeds: {lane_speeds[edge_id]['dir2']}")

# Function to calculate average speed for a lane
def calculate_average_speed(speeds):
    avg_speed_dir1 = sum(speeds['dir1']) / len(speeds['dir1']) if speeds['dir1'] else 0
    avg_speed_dir2 = sum(speeds['dir2']) / len(speeds['dir2']) if speeds['dir2'] else 0
    return {'dir1': avg_speed_dir1, 'dir2': avg_speed_dir2}

# Function to map speeds to colors
def get_color_by_speed(speed):
    if 20 <= speed < 30:
        return 'blue'
    elif 30 <= speed < 40:
        return 'green'
    elif 40 <= speed < 50:
        return 'yellow'
    elif 50 <= speed < 60:
        return 'red'
    elif speed >= 60:
        return 'gray'
    elif speed < 20:
        return 'brown'
    return 'black'  # Default color if no match

# Create the plot
plt.figure(figsize=(14, 14))  # Adjust the figure size for better visibility

# Define the roads of interest
roads_of_interest = ['rutherford', 'dufferin']

# Plot the roads with color based on average speed for specified roads
for edge in edges:
    edge_coords = edge[:2]  # Get coordinates
    edge_id = edge[2]  # Get edge ID

    # Only process roads of interest
    if any(road in edge_id.lower() for road in roads_of_interest):
        avg_speeds = calculate_average_speed(lane_speeds[edge_id])
        print(f"Average speeds for edge {edge_id}: {avg_speeds}")  # Debug: Print average speeds

        # Extract coordinates for both ends of the road segment
        x_values = [edge_coords[0][0], edge_coords[1][0]]
        y_values = [edge_coords[0][1], edge_coords[1][1]]

        # Plot direction 1
        road_color_dir1 = get_color_by_speed(avg_speeds['dir1'])
        print(f"Road color for direction 1 of {edge_id}: {road_color_dir1}")  # Debug: Check color for direction 1
        plt.plot(x_values, y_values, color=road_color_dir1, linewidth=6)  # Direction 1

        # Plot direction 2 (slightly offset for visual distinction)
        offset_x = 0.05  # Adjust this value for better visual separation
        x_values_dir2 = [x + offset_x for x in x_values]
        road_color_dir2 = get_color_by_speed(avg_speeds['dir2'])
        print(f"Road color for direction 2 of {edge_id}: {road_color_dir2}")  # Debug: Check color for direction 2
        plt.plot(x_values_dir2, y_values, color=road_color_dir2, linewidth=6)  # Direction 2

# Create connections between roads based on common nodes
node_connections = defaultdict(list)
for edge in edges:
    node_connections[edge[0]].append(edge)
    node_connections[edge[1]].append(edge)

# Optionally visualize connections (for debugging or checking)
for node, connected_edges in node_connections.items():
    for connected_edge in connected_edges:
        plt.plot([node[0], connected_edge[1][0]], [node[1], connected_edge[1][1]], color='gray', linestyle='--', linewidth=1)  # Draw connection lines

# Plot nodes
for node in nodes:
    plt.scatter(node[0], node[1], color='blue', s=50)  # Larger dots for nodes

# Set limits to zoom out and fit the entire network
plt.xlim(min([node[0] for node in nodes]) - 2, max([node[0] for node in nodes]) + 2)  # Increased padding
plt.ylim(min([node[1] for node in nodes]) - 2, max([node[1] for node in nodes]) + 2)  # Increased padding

# Customize the plot
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('Road Network with Average Speed Color Coding for Rutherford and Dufferin')
plt.grid(True)
plt.show()
