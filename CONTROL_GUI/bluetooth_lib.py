import pygame
import math
import csv 
import sys

# Read the CSV file
def read_GUI_junction_coordinates(file_name):
    scaled_positions = {}
    coordinates = {}
    with open(file_name, mode='r') as file:
        csv_reader = csv.DictReader(file)
    
        for row in csv_reader:
            # Ignore rows where the Junction ID starts with ':'
            junction_id = row['Junction ID']
            if not junction_id.startswith(':'):
                # Store the X and Y coordinates in the dictionary
                coordinates[junction_id] = (float(row['X Coordinate']), float(row['Y Coordinate']))


    """
    Normalize coordinates such that the x values are shifted left by the smallest x value,
    and y values are shifted up by the smallest y value.
    
    Args:
        coordinates (dict): A dictionary of coordinates with keys as IDs and values as (x, y) tuples.
        
    Returns:
        dict: The shifted coordinates.
    """
    # Extract all x and y values
    x_values = [coord[0] for coord in coordinates.values()]
    y_values = [coord[1] for coord in coordinates.values()]
    
    # Find the smallest x and y values
    min_x = min(x_values)
    min_y = min(y_values)
    
    # Shift all coordinates
    scaled_positions = {
        key: (x - min_x, y - min_y) for key, (x, y) in coordinates.items()
    }
    return scaled_positions

# Function to read the CSV file and return a list of dictionaries
def read_edge_data(file_path):
    edge_data = []
    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert numerical fields from strings to float
            edge_data.append({
                "edge_id": row["Edge ID"],
                "from_node": row["from"],
                "to_node": row["to"],
                "speed_limit": float(row["Speed Limit (km/h)"]),
                "average_speed": float(row["Average Speed (km/h)"])
            })
    return edge_data

# Function to draw a dot for a node (intersection)
def draw_node(screen, node_position, node_radius=8):
    pygame.draw.circle(screen, NODE_COLOR, (int(node_position[0]), int(node_position[1])), node_radius)

# Function to calculate lane color based on average speed
def get_speed_color(average_speed):
    if average_speed < 30:  # Explicitly set color to Brown if speed is less than 30
        return BROWN  # 30 km/h and under
    elif average_speed < 40:  # Blue is for speeds in the 30-40 range
        return BLUE  # 30-40 km/h
    elif average_speed < 50:  # Green for speeds 40-50 km/h
        return GREEN  # 40-50 km/h
    elif average_speed < 60:  # Yellow for 50-60 km/h
        return YELLOW  # 50-60 km/h
    else:  # Gray for anything over 60 km/h
        return GRAY  # 60+ km/h

# Function to draw two-way road with directional lanes
def draw_two_way_road(screen, p1, p2, road_width, average_speed, speed_limit):
    # Calculate angle and offsets for the road's direction
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    angle = math.atan2(dy, dx)
    offset_dx = road_width / 2 * math.sin(angle)
    offset_dy = road_width / 2 * math.cos(angle)
    
    # Points for the left and right edges of the two-way road
    lane1_start = (p1[0] - offset_dx, p1[1] + offset_dy)
    lane1_end = (p2[0] - offset_dx, p2[1] + offset_dy)
    lane2_start = (p1[0] + offset_dx, p1[1] - offset_dy)
    lane2_end = (p2[0] + offset_dx, p2[1] - offset_dy)

    # Assign lane colors based on speed (Average speed vs. Speed limit)
    color1 = get_speed_color(average_speed)
    color2 = get_speed_color(speed_limit)

    # Draw the road lanes with corresponding colors
    pygame.draw.line(screen, color1, lane1_start, lane1_end, road_width)
    pygame.draw.line(screen, color2, lane2_start, lane2_end, road_width)

