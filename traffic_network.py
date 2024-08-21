import json
import pygame

# Global variable to control debugging output
DEBUG = 0  # Set to 1 to enable debug printing, 0 to disable

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

# Function to draw nodes on the Pygame screen
def draw_nodes(screen, nodes, font, total_nodes):
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

    # Updated scale factors
    x_scale = 0.025
    y_scale = -0.025

    # X-axis offset to shift nodes
    x_offset = screen.get_width() // 2

    # Fill the background
    screen.fill(WHITE)
    
    # Flag to check if node ID 1 has been printed
    debug_printed = False
    
    for node in nodes:
        x = int(node["X"] * x_scale + x_offset)
        y = int(node["Y"] * y_scale + screen.get_height() // 2)
        
        # Print debugging information if DEBUG is enabled
        if DEBUG and node["INTID"] == 1 and not debug_printed:
            print(f'Drawing node ID {node["INTID"]} at ({x}, {y}) - Total nodes: {total_nodes}')
            debug_printed = True

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
        draw_nodes(screen, nodes, font, total_nodes)

    pygame.quit()

# Run the main function
if __name__ == "__main__":
    main()
