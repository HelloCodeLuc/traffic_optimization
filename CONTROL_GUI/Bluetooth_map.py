import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from collections import defaultdict
import os
import pygame

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

def bluetooth_plot(edges, lane_speeds, nodes):
    # Initialize a new figure and canvas
    fig, ax = plt.subplots(figsize=(14, 14))
    
    # Define the roads of interest
    roads_of_interest = ['rutherford', 'dufferin']
    
    # Plot roads with color based on average speed for specified roads
    for edge in edges:
        edge_coords = edge[:2]
        edge_id = edge[2]

        if any(road in edge_id.lower() for road in roads_of_interest):
            avg_speeds = calculate_average_speed(lane_speeds[edge_id])

            # Coordinates for road segment
            x_values = [edge_coords[0][0], edge_coords[1][0]]
            y_values = [edge_coords[0][1], edge_coords[1][1]]

            # Direction 1
            road_color_dir1 = get_color_by_speed(avg_speeds['dir1'])
            ax.plot(x_values, y_values, color=road_color_dir1, linewidth=6)

            # Direction 2 (offset for visual separation)
            offset_x = 0.05
            x_values_dir2 = [x + offset_x for x in x_values]
            road_color_dir2 = get_color_by_speed(avg_speeds['dir2'])
            ax.plot(x_values_dir2, y_values, color=road_color_dir2, linewidth=6)

    # Draw connections based on common nodes
    node_connections = defaultdict(list)
    for edge in edges:
        node_connections[edge[0]].append(edge)
        node_connections[edge[1]].append(edge)

    for node, connected_edges in node_connections.items():
        for connected_edge in connected_edges:
            ax.plot([node[0], connected_edge[1][0]], [node[1], connected_edge[1][1]], color='gray', linestyle='--', linewidth=1)

    # Plot nodes
    for node in nodes:
        ax.scatter(node[0], node[1], color='blue', s=50)

    # Set limits and labels
    ax.set_xlim(min([node[0] for node in nodes]) - 2, max([node[0] for node in nodes]) + 2)
    ax.set_ylim(min([node[1] for node in nodes]) - 2, max([node[1] for node in nodes]) + 2)
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title('Road Network with Average Speed Color Coding for Rutherford and Dufferin')
    ax.grid(True)

    # Convert Matplotlib figure to Pygame surface
    canvas = FigureCanvas(fig)
    canvas.draw()
    plot_surface = pygame.image.fromstring(canvas.tostring_rgb(), canvas.get_width_height(), "RGB")
    plt.close(fig)
    return plot_surface

def bluetooth_extract_nodes_edges_create_plot():
    # Set up Pygame
    pygame.init()
    screen = pygame.display.set_mode((1400, 1400))
    pygame.display.set_caption("Bluetooth Plot")

    # Load XML data and prepare edges, lane_speeds, and nodes
    current_directory = os.getcwd()
    file_path = f'{current_directory}/../NETWORKS/school-extended.net.xml'

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit()

    nodes = []
    edges = []
    lane_speeds = defaultdict(lambda: {'dir1': [], 'dir2': []})

    for edge in root.findall(".//edge"):
        edge_id = edge.get('id')
        for lane in edge.findall(".//lane"):
            shape = lane.get('shape')
            speed = float(lane.get('speed'))
            if shape:
                points = shape.split(' ')
                node_coords = [tuple(map(float, point.split(','))) for point in points]
                nodes.extend(node_coords)

                for i in range(len(node_coords) - 1):
                    edges.append((node_coords[i], node_coords[i + 1], edge_id))

                    if len(edges) % 2 == 0:
                        lane_speeds[edge_id]['dir1'].append(speed)
                    else:
                        lane_speeds[edge_id]['dir2'].append(speed)

    # Generate the plot surface
    plot_surface = bluetooth_plot(edges, lane_speeds, nodes)

    # Main loop to display the plot
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        screen.blit(plot_surface, (0, 0))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    bluetooth_extract_nodes_edges_create_plot()