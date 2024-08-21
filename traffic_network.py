import json
import pygame

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
def draw_nodes(screen, nodes, font):
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

    x_scale = 0.025
    y_scale = -0.025

    screen.fill(WHITE)
    for node in nodes:
        x = int(node["X"] * x_scale + screen.get_width() // 2)
        y = int(node["Y"] * y_scale + screen.get_height() // 2)
        
        # Only print the first node for debugging
        if node["INTID"] == 1:
            print(f'Drawing node ID {node["INTID"]} at ({x}, {y})')

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

        draw_nodes(screen, nodes, font)

    pygame.quit()

# Run the main function
if __name__ == "__main__":
    main()
