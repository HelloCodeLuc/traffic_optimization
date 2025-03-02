import pygame
import math
import csv
import sys
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image

# Function to draw a dot for a node using Matplotlib
def draw_node(ax, node_position, node_radius=8):
    ax.scatter(node_position[0], node_position[1], s=node_radius**2, color='blue', zorder=2)

# Function to read the CSV file and return a list of dictionaries
def read_edge_data(file_path):
    edge_data = []
    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            edge_data.append({
                "edge_id": row["Edge ID"],
                "from_node": row["from"],
                "to_node": row["to"],
                "speed_limit": float(row["Speed Limit (km/h)"]),
                "average_speed": float(row["Average Speed (km/h)"])
            })
    return edge_data

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
    scaled_positions = {key: (x - min_x, y - min_y) for key, (x, y) in coordinates.items()}

    # Print statements after defining scaled_positions
    print("Original coordinates:", coordinates)
    print("Scaled coordinates:", scaled_positions)
    print(f"Smallest X: {min_x}, Smallest Y: {min_y}")

    return scaled_positions

# Function to calculate lane color based on average speed
def get_speed_color(average_speed):
    if average_speed < 30:
        return "brown"
    elif average_speed < 40:
        return "blue"
    elif average_speed < 50:
        return "green"
    elif average_speed < 60:
        return "yellow"
    else:
        return "gray"

# Function to draw two-way road using Matplotlib
def draw_two_way_road(ax, p1, p2, road_width, average_speed, speed_limit):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    angle = math.atan2(dy, dx)
    
    # Increase the lane separation by modifying the offset calculation
    lane_spacing_factor = 1.5  # Adjust this value to control spacing
    offset_dx = (road_width * lane_spacing_factor) / 2 * math.sin(angle)
    offset_dy = (road_width * lane_spacing_factor) / 2 * math.cos(angle)

    # Define road edges
    lane1_start = (p1[0] - offset_dx, p1[1] + offset_dy)
    lane1_end = (p2[0] - offset_dx, p2[1] + offset_dy)
    lane2_start = (p1[0] + offset_dx, p1[1] - offset_dy)
    lane2_end = (p2[0] + offset_dx, p2[1] - offset_dy)

    # Get colors
    color1 = get_speed_color(average_speed)
    color2 = get_speed_color(speed_limit)

    # Draw lanes
    ax.plot([lane1_start[0], lane1_end[0]], [lane1_start[1], lane1_end[1]], color=color1, linewidth=road_width, zorder=1)
    ax.plot([lane2_start[0], lane2_end[0]], [lane2_start[1], lane2_end[1]], color=color2, linewidth=road_width, zorder=1)

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
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two-Way Road with Directional Colors and Nodes")

# Create Matplotlib figure first
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_aspect('equal')
ax.set_facecolor('black')

# Read input files
file_name = "RESOURCES/CONNECTING_TWO_POINTS/GUI_junction_coordinates.csv"
scaled_positions = read_GUI_junction_coordinates(file_name)

file_path = "RESOURCES/CONNECTING_TWO_POINTS/GUI_average_speeds.csv"
edge_data = read_edge_data(file_path)

# Road width
road_width = 8

# Draw roads and nodes
for edge in edge_data:
    from_node = edge['from_node']
    to_node = edge['to_node']
    point1 = scaled_positions[from_node]
    point2 = scaled_positions[to_node]
    average_speed = edge['average_speed']
    speed_limit = edge['speed_limit']
    draw_two_way_road(ax, point1, point2, road_width, average_speed, speed_limit)

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
