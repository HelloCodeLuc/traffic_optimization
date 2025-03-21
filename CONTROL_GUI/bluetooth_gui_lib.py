import pygame
import math
import csv
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image

# Function to draw a dot for a node using Matplotlib
def draw_node(ax, node_position, coord_differences, node_radius=8):
    ax.scatter(node_position[0], node_position[1], s=node_radius**2, color='blue', zorder=2)

    if coord_differences != None:
        formatted_position = f"{node_position[0]:.2f},{node_position[1]:.2f}"

        if formatted_position in coord_differences:      
            # Extract the offset and green light timing difference
            diff_values = coord_differences[formatted_position]
            offset_diff = diff_values["offset_diff"]
            green_diff = diff_values["green_diff"]

            # Get x, y from node_position
            x, y = map(float, node_position)

            # Offset the text position
            text_x = x + 15
            text_y = y + 12

            # Display the values on the ax plot
            ax.text(text_x, text_y, f"O:{offset_diff},\nG:{green_diff}", fontsize=10, color="red", ha="center")

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

# Read the csv file
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

    return coordinates

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
