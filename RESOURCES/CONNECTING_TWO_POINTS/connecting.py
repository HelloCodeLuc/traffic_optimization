import pygame
import math
import csv
import sys
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

# Function to draw a dot for a node using Matplotlib
def draw_node(ax, node_position, node_radius=8):
    ax.scatter(node_position[0], node_position[1], s=node_radius**2, color='blue', zorder=2)

# Function to read the CSV file and store both speeds in the same dictionary
def read_edge_data(file_path):
    edge_data = []

    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            edge_id = row["Edge ID"]
            avg_speed = float(row["Average Speed (km/h)"])

            # Add both speeds into the same dictionary
            edge_data.append({
                "edge_id": edge_id,
                "from_node": row["from"],
                "to_node": row["to"],
                "average_speed": avg_speed
            })

    return edge_data

def read_edge_name(edge_file):
    # Dictionary to store (from, to) → edge_id mapping
    edge_mapping = {}

    # Read the CSV file and create the dictionary
    with open(edge_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            edge_id = row['Edge_ID']
            from_node = row['From']
            to_node = row['To']

            # Store the mapping with (from, to) as the key
            edge_mapping[(from_node, to_node)] = edge_id

    return edge_mapping

# Function to read and scale GUI junction coordinates
def read_GUI_junction_coordinates(file_name):
    coordinates = {}
    with open(file_name, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            junction_id = row['Junction ID']
            if not junction_id.startswith(':'):
                coordinates[junction_id] = (float(row['X Coordinate']), float(row['Y Coordinate']))

    # Find the minimum x and y coordinates
    min_x = min(coord[0] for coord in coordinates.values())
    min_y = min(coord[1] for coord in coordinates.values())

    # Shift the coordinates to move the origin to the top-left of the screen
    scaled_positions = {key: (x, y) for key, (x, y) in coordinates.items()}

    return scaled_positions

# Function to calculate lane color based on average speed
def get_speed_color(speed):
    if speed < 30:
        return "red"
    elif speed < 40:
        return "blue"
    elif speed < 50:
        return "green"
    elif speed < 60:
        return "yellow"
    else:
        return "gray"

# Function to draw two-way road using Matplotlib
def draw_two_way_road(ax, p1, p2, road_width, edge_data):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    angle = math.atan2(dy, dx)

    coordinates = {}
    with open(file_name, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            junction_id = row['Junction ID']
            if not junction_id.startswith(':'):
                coordinates[junction_id] = (float(row['X Coordinate']), float(row['Y Coordinate']))

    # Get all keys that have the specified value
    p1_array = [k for k, v in coordinates.items() if v == p1]
    p1_name = p1_array[0]
    # Get all keys that have the specified value
    p2_array = [k for k, v in coordinates.items() if v == p2]
    p2_name = p2_array[0]

    matching_dict = next((d for d in edge_data if d.get('from_node') == p1_name and d.get('to_node') == p2_name), None)
    average_speed = matching_dict.get('average_speed') if matching_dict else None
    matching_dict2 = next((d for d in edge_data if d.get('from_node') == p2_name and d.get('to_node') == p1_name), None)
    average_speed2 = matching_dict2.get('average_speed') if matching_dict2 else None
    
    # Lane separation offset
    lane_spacing_factor = 1.8
    offset_dx = (road_width * lane_spacing_factor) / 2 * math.sin(angle)
    offset_dy = (road_width * lane_spacing_factor) / 2 * math.cos(angle)

    # Define road edges
    lane1_start = (p1[0] - offset_dx, p1[1] + offset_dy)
    lane1_end = (p2[0] - offset_dx, p2[1] + offset_dy)
    lane2_start = (p1[0] + offset_dx, p1[1] - offset_dy)
    lane2_end = (p2[0] + offset_dx, p2[1] - offset_dy)

    # Draw lanes with both colors
    ax.plot([lane1_start[0], lane1_end[0]], [lane1_start[1], lane1_end[1]], color=get_speed_color(average_speed2), linewidth=road_width, zorder=1)
    ax.plot([lane2_start[0], lane2_end[0]], [lane2_start[1], lane2_end[1]], color=get_speed_color(average_speed), linewidth=road_width, zorder=1)

# Function to convert Matplotlib figure to Pygame surface
def fig_to_pygame(fig):
    """Convert a Matplotlib figure to a Pygame surface."""
    buf = BytesIO()
    fig.savefig(buf, format="PNG")  # Save figure as PNG to buffer
    buf.seek(0)  # Move to the beginning of the buffer

    # Load the image with PIL and convert to a format pygame supports
    image = Image.open(buf)
    mode = image.mode
    size = image.size
    data = image.tobytes()

    return pygame.image.fromstring(data, size, mode)  # Convert to pygame surface

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two-Way Road with Directional Colors and Nodes")

# Create Matplotlib figure
fig, ax = plt.subplots(figsize=(4, 4))
ax.set_aspect('equal')
ax.set_facecolor('black')

# Set a black border around the figure
fig.patch.set_edgecolor('black')
fig.patch.set_linewidth(2)

# Remove extra padding
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Read input files
file_name = "NETWORKS/simple_network/simple_network_junctions.bluetooth.csv"
scaled_positions = read_GUI_junction_coordinates(file_name)

file_path = "NETWORKS/simple_network/simple_network.bluetooth.csv"
edge_data = read_edge_data(file_path)

file = "RESOURCES/CONNECTING_TWO_POINTS/GUI_edges.csv"
edge_name = read_edge_name(file)

# Road width
road_width = 8

# Draw roads and nodes
for edge in edge_data:
    from_node = edge['from_node']
    to_node = edge['to_node']

    if from_node in scaled_positions and to_node in scaled_positions:
        point1 = scaled_positions[from_node]
        point2 = scaled_positions[to_node]

        average_speed = edge['average_speed']

        draw_two_way_road(ax, point1, point2, road_width, edge_data)

# Draw nodes
for node_position in scaled_positions.values():
    draw_node(ax, node_position)

# Remove axis labels and ticks
ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)

# Convert Matplotlib figure to Pygame surface
pygame_surface = fig_to_pygame(fig)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen to black before rendering the new frame
    screen.fill((0, 0, 0))

    # Display the image from Matplotlib
    screen.blit(pygame_surface, (0, 0))
    pygame.display.flip()

pygame.quit()
