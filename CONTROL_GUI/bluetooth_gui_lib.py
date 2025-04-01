import pygame
import math
import csv
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image
import os
import sys

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
            text_x = x + 100
            text_y = y + 50

            # Display the values on the ax plot
            ax.text(text_x, text_y, f"O:{offset_diff},\nG:{green_diff}", fontsize=10, color="red", ha="center")

# Function to read the CSV file and return a list of dictionaries
def read_edge_data(file_path):
    edge_data = []
    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            edge_id = row["Edge ID"]
            speed_limit = float(row["Speed Limit (km/h)"])
            avg_speed = float(row["Average Speed (km/h)"])

            # Add both speeds into the same dictionary
            edge_data.append({
                "edge_id": edge_id,
                "from_node": row["from"],
                "to_node": row["to"],
                "speed_limit": speed_limit,
                "average_speed": avg_speed
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

    named_intersections = {key: (x, y) for key, (x, y) in coordinates.items()}

    return named_intersections

# Function to calculate lane color based on average speed
def get_speed_color(speed):
    if speed < 30:
        return "brown"
    elif speed < 40:
        return "blue"
    elif speed < 50:
        return "green"
    elif speed < 60:
        return "yellow"
    else:
        return "gray"

# Function to draw two-way road using Matplotlib
def draw_two_way_road(ax, p1, p2, road_width, lane_spacing_factor, edge_data, junctions_bluetooth):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    angle = math.atan2(dy, dx)

    coordinates = {}
    with open(junctions_bluetooth, mode='r') as file:
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

    # print (edge_data)
    matching_dict = next((d for d in edge_data if d.get('from_node') == p1_name and d.get('to_node') == p2_name), None)
    average_speed = matching_dict.get('average_speed') if matching_dict else None
    matching_dict2 = next((d for d in edge_data if d.get('from_node') == p2_name and d.get('to_node') == p1_name), None)
    average_speed2 = matching_dict2.get('average_speed') if matching_dict2 else None
    
    # print (f"from_node {p1_name} to_node {p2_name} average_speed1 ={average_speed}: {type(average_speed)}")
    # print (f"from_node {p2_name} to_node {p1_name} average_speed2 ={average_speed2}: {type(average_speed2)}")

    # Increase the lane separation by modifying the offset calculation
    # lane_spacing_factor = 5.8  # Adjust this value to control spacing
    offset_dx = (road_width * lane_spacing_factor) / 2 * math.sin(angle)
    offset_dy = (road_width * lane_spacing_factor) / 2 * math.cos(angle)

    # Define road edges
    lane1_start = (p1[0] - offset_dx, p1[1] + offset_dy)
    lane1_end = (p2[0] - offset_dx, p2[1] + offset_dy)
    lane2_start = (p1[0] + offset_dx, p1[1] - offset_dy)
    lane2_end = (p2[0] + offset_dx, p2[1] - offset_dy)

    # Draw lanes
    ax.plot([lane1_start[0], lane1_end[0]], [lane1_start[1], lane1_end[1]], color=get_speed_color(average_speed2), linewidth=road_width, zorder=1)
    ax.plot([lane2_start[0], lane2_end[0]], [lane2_start[1], lane2_end[1]], color=get_speed_color(average_speed), linewidth=road_width, zorder=1)

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

# this is to count non blank lines in output_data.txt to help show batches/run counts on gui main
def count_non_blank_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        non_blank_lines = [line for line in file if line.strip()]  # Filter out blank lines
    return len(non_blank_lines)

# this draws little boxes to depict batches and runs completed and in progress
def draw_stats(num_batches, num_runs_per_batch, output_dir, x, y, screen):
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 200, 0)
    RED = (200, 0, 0)

    # Constants
    SCREEN_WIDTH = 500
    SCREEN_HEIGHT = 200
    SQUARE_SIZE = 7
    SQUARE_SPACING = 5
    TEXT_PADDING = 100  # Space for "Batches:" text
    
    font = pygame.font.Font(None, 24)
    if os.path.exists(f"{output_dir}/output_data.txt"):
        file_path = f"{output_dir}/output_data.txt"
        non_blank_count = count_non_blank_lines(file_path)
        # print(f"Number of non-blank lines: {non_blank_count}")

        completed_batches, completed_runs = divmod(non_blank_count, num_runs_per_batch)
        runs_in_progress = num_runs_per_batch - completed_runs

        # print(f"Total non-blank lines: {non_blank_count}")
        # print(f"Completed batches: {completed_batches}")
        # print(f"Runs remaining: {runs_in_progress}")
        # Render "Batches:" text
        text_surface = font.render("Batches:", True, BLACK)
        screen.blit(text_surface, (x, y))
        text_surface = font.render("Sims In progress:", True, BLACK)
        screen.blit(text_surface, (x, y + 20))

        # Draw batch squares
        for i in range(num_batches):
            color = RED if i < completed_batches else GREEN
            x_pos = x + i * (SQUARE_SIZE + SQUARE_SPACING) + 150
            y_pos = y + SQUARE_SIZE//2
            pygame.draw.rect(screen, color, (x_pos, y_pos, SQUARE_SIZE, SQUARE_SIZE))
        # Draw runs in progress squares
        for i in range(num_runs_per_batch):
            color = RED if i < completed_runs else GREEN
            x_pos = x + i * (SQUARE_SIZE + SQUARE_SPACING) + 150
            y_pos = y + SQUARE_SIZE//2 + 20
            pygame.draw.rect(screen, color, (x_pos, y_pos, SQUARE_SIZE, SQUARE_SIZE))
