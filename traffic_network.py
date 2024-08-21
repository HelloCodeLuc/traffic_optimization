import json
import pygame

# Replace with the correct path to your JSON file
file_path = 'traffic_network.json'

# Load the JSON file
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    exit()
except json.JSONDecodeError:
    print(f"Error: The file '{file_path}' is not a valid JSON file or is empty.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit()

# Access roads and intersections
roads = data.get("roads", [])
intersections = data.get("intersections", [])

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Traffic Network")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Draw the traffic network
def draw_traffic_network():
    screen.fill(WHITE)
    for road in roads:
        pygame.draw.line(screen, BLACK, tuple(road["start"]), tuple(road["end"]), road["lanes"] * 5)
    for intersection in intersections:
        location = tuple(intersection["location"])
        for light in intersection["traffic_lights"]:
            color = GREEN if light["state"] == "green" else RED
            pygame.draw.circle(screen, color, location, 10)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_traffic_network()
    pygame.display.flip()

pygame.quit()