import pygame
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two-Way Road with Directional Colors")

# Colors
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Define points
point1 = (200, 150)
point2 = (600, 450)
point3 = (100, 200)
road_width = 10  # Width of the road (includes both lanes)

def draw_two_way_road(screen, p1, p2, road_width):
    # Calculate the angle between the two points
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    angle = math.atan2(dy, dx)
    
    # Calculate offsets for the road lanes
    offset_x = math.sin(angle) * road_width / 2
    offset_y = -math.cos(angle) * road_width / 2
    
    # Calculate the coordinates of the four corners of the road
    p1_left = (p1[0] + offset_x, p1[1] + offset_y)
    p1_right = (p1[0] - offset_x, p1[1] - offset_y)
    p2_left = (p2[0] + offset_x, p2[1] + offset_y)
    p2_right = (p2[0] - offset_x, p2[1] - offset_y)
    
    # Draw the road as a filled polygon
    pygame.draw.polygon(screen, GRAY, [p1_left, p1_right, p2_right, p2_left])
    
    # Calculate midpoints for red and blue lanes
    mid_p1 = ((p1_left[0] + p1_right[0]) / 2, (p1_left[1] + p1_right[1]) / 2)
    mid_p2 = ((p2_left[0] + p2_right[0]) / 2, (p2_left[1] + p2_right[1]) / 2)
    
    # Draw red path from p1 to p2
    pygame.draw.polygon(screen, RED, [p1_left, mid_p1, mid_p2, p2_left])

    # Draw blue path from p2 to p1
    pygame.draw.polygon(screen, BLUE, [p2_right, mid_p2, mid_p1, p1_right])

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Fill screen with black
    screen.fill(BLACK)
    
    # Draw the two-way road
    draw_two_way_road(screen, point1, point2, road_width)
    draw_two_way_road(screen, point1, point3, road_width)    
    # Update the display
    pygame.display.flip()

pygame.quit()
