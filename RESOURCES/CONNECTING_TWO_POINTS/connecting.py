import pygame
import math
import csv 
import sys

# Function to draw a dot for a node (intersection)
def draw_node(screen, node_position, node_radius=8):
    pygame.draw.circle(screen, NODE_COLOR, (int(node_position[0]), int(node_position[1])), node_radius)

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
    
# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two-Way Road with Directional Colors and Nodes")

# Colors
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
NODE_COLOR = (0, 0, 255)  # Blue color for nodes (junctions)

# Initialize an empty dictionary to store junction data
scaled_positions = {}

# File name
file_name = "RESOURCES/CONNECTING_TWO_POINTS/GUI_junction_coordinates.csv"

scaled_positions = read_GUI_junction_coordinates(file_name)

# Output the dictionary
print(scaled_positions)

# Example usage
file_path = "RESOURCES/CONNECTING_TWO_POINTS/GUI_average_speeds.csv"
edge_data = read_edge_data(file_path)

# Main loop
running = True

# Road width (includes both lanes)
road_width = 10

# Center the diagram by finding the center of the coordinates
all_x = [pos[0] for pos in scaled_positions.values()]
all_y = [pos[1] for pos in scaled_positions.values()]

# Calculate the center (average position)
# center_x = sum(all_x) / len(all_x)
# center_y = sum(all_y) / len(all_y)

# Offset all positions by subtracting the center
# offset_scaled_positions = {
#     key: (value[0] - center_x + WIDTH / 2, value[1] - center_y + HEIGHT / 2)
#     for key, value in scaled_positions.items()
# }

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Fill screen with black
    screen.fill(BLACK)
    
    # Loop through each edge and draw the roads with updated speeds and nodes
    for edge in edge_data:
        from_node = edge['from_node']
        to_node = edge['to_node']
        point1 = scaled_positions[from_node]
        point2 = scaled_positions[to_node]
        average_speed = edge['average_speed']
        speed_limit = edge['speed_limit']
        draw_two_way_road(screen, point1, point2, road_width, average_speed, speed_limit)
    
    # Draw dots for each node (intersection)
    for node_position in scaled_positions.values():
        draw_node(screen, node_position)
    
    # Update the display
    pygame.display.flip()

pygame.quit()
