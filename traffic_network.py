import json
import pygame

# Global variable to control debugging output
DEBUG = 1  # Set to 1 to enable debug printing, 0 to disable

# Function to load data from JSON file
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        exit()
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file or is empty.")
        exit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit()

# Function to adjust nodes to center the leftmost node at x=0
def adjust_node_positions(nodes):
    # Find the minimum and maximum x and y values
    min_x = min(node["X"] for node in nodes)
    max_x = max(node["X"] for node in nodes)
    min_y = min(node["Y"] for node in nodes)
    max_y = max(node["Y"] for node in nodes)

    # Calculate the x and y offset needed to shift the leftmost node to x=0 and center the nodes
    x_offset = -min_x
    y_offset = -min_y

    if DEBUG:
        print(f"Adjusting nodes. Minimum x value: {min_x}, Minimum y value: {min_y}")
    
    # Apply the offset to all nodes
    for node in nodes:
        original_x = node["X"]
        original_y = node["Y"]
        node["X"] += x_offset
        node["Y"] += y_offset
        if DEBUG:
            print(f"Node ID {node['INTID']}: x changed from {original_x} to {node['X']}, y changed from {original_y} to {node['Y']}")

    return max_x - min_x, max_y - min_y  # Return the range of x and y values

# Function to draw nodes on the Pygame screen
def draw_nodes(screen, nodes, font, total_nodes, x_range, y_range):
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

    # Adjusted scale factors for slightly smaller nodes
    x_scale = (screen.get_width() - 80) / x_range  # 80 pixels margin instead of 60
    y_scale = (screen.get_height() - 80) / y_range  # 80 pixels margin instead of 60

    # Fill the background
    screen.fill(WHITE)
    
    # Flag to check if node ID 1 has been printed
    debug_printed = False
    
    for node in nodes:
        x = int(node["X"] * x_scale + 40)  # 40 pixels offset from the edge
        y = int(screen.get_height() - (node["Y"] * y_scale + 40))  # Flip y-coordinate
        
        # Print debugging information if DEBUG is enabled
        if DEBUG and node["INTID"] == 1 and not debug_printed:
            print(f'Drawing node ID {node["INTID"]} at ({x}, {y}) - Total nodes: {total_nodes}')
            debug_printed = True

        # Set nodes 10 and 11 to red, others based on TYPE
        if node["INTID"] in [10, 11]:
            color = RED
        else:
            color = RED if node["TYPE"] == 1 else GREEN

        pygame.draw.circle(screen, color, (x, y), 5)
        text_surface = font.render(f'{node["INTID"]}', True, color)
        screen.blit(text_surface, (x + 10, y - 10))
    
    pygame.display.flip()

# Main function to set up Pygame and run the simulation
def main():
    # Load node data from JSON file
    file_path = 'nodes.json'
    data = load_data(file_path)
    nodes = data.get("nodes", [])
    
    if not nodes:
        print("Error: No nodes found in the JSON file.")
        exit()

    # Count the total number of nodes
    total_nodes = len(nodes)

    # Adjust node positions so that the leftmost node is at x=0
    x_range, y_range = adjust_node_positions(nodes)

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Nodes on Cartesian Plane")
    font = pygame.font.SysFont(None, 24)

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw nodes on the screen
        draw_nodes(screen, nodes, font, total_nodes, x_range, y_range)

    pygame.quit()

# Run the main function
if __name__ == "__main__":
    main()
