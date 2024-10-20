import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Set up the window
width, height = 300, 300
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Button & Dropdown Example")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (169, 169, 169)
SHADOW = (100, 100, 100)
BLUE = (173, 216, 230)

# Define button properties
button_width, button_height = 60, 30
buttons = {
    "A": pygame.Rect(50, 130, button_width, button_height),
    "B": pygame.Rect(120, 130, button_width, button_height),
    "C": pygame.Rect(190, 130, button_width, button_height)
}

# Store button click state (for shadow effect)
button_pressed = {"A": False, "B": False, "C": False}

# Store hover state
button_hovered = {"A": False, "B": False, "C": False}

# Define font
font = pygame.font.Font(None, 36)
dropdown_font = pygame.font.Font(None, 24)  # Smaller font for the dropdown

# Dropdown variables
dropdown_open = False
dropdown_rect = pygame.Rect(120, 50, 150, 30)  # Adjusted position for dropdown
dropdown_options = ["default_network"]
selected_network = "default_network"

# Define the relative path to the network directory with respect to current working directory
current_dir = os.getcwd()
network_dir = os.path.join(current_dir, "../../NETWORKS")

# Function to draw buttons with shadow and hover effect
def draw_buttons():
    for label, rect in buttons.items():
        if button_pressed[label]:
            # If button is pressed, draw as if it is pushed down
            pygame.draw.rect(screen, SHADOW, (rect.x + 3, rect.y + 3, rect.width, rect.height))  # Shadow when pressed
            pygame.draw.rect(screen, DARK_GRAY, rect)  # Darker button
        else:
            # Draw normal button with shadow effect
            pygame.draw.rect(screen, SHADOW, (rect.x + 5, rect.y + 5, rect.width, rect.height))  # Idle shadow
            pygame.draw.rect(screen, GRAY, rect)  # Regular button
        
        # If button is hovered, draw white outline
        if button_hovered[label]:
            pygame.draw.rect(screen, WHITE, rect, 3)  # White outline
        
        # Render the text label
        text = font.render(label, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

# Function to append to command_queue.txt
def append_to_queue(command):
    with open("command_queue.txt", "a") as file:
        file.write(command + "\n")

# Updated function to load network files with .net.xml extension
def load_network_files():
    files = []
    if os.path.exists(network_dir) and os.path.isdir(network_dir):
        # List all files in the NETWORKS directory
        for file in os.listdir(network_dir):
            if file.endswith(".net.xml"):  # Only .net.xml files
                files.append(file)
    return files

# Function to draw dropdown menu
def draw_dropdown():
    global selected_network
    # Draw the "Network: " label
    label_text = dropdown_font.render("Network:", True, BLACK)
    screen.blit(label_text, (20, 55))  # Positioned to the left of the dropdown

    pygame.draw.rect(screen, GRAY, dropdown_rect)  # Main dropdown button
    text = dropdown_font.render(selected_network, True, BLACK)
    screen.blit(text, (dropdown_rect.x + 10, dropdown_rect.y + 5))

    # If dropdown is open, show options
    if dropdown_open:
        for i, option in enumerate(dropdown_options):
            option_rect = pygame.Rect(dropdown_rect.x, dropdown_rect.y + (i + 1) * dropdown_rect.height, dropdown_rect.width, dropdown_rect.height)
            pygame.draw.rect(screen, BLUE if option == selected_network else GRAY, option_rect)
            option_text = dropdown_font.render(option, True, BLACK)
            screen.blit(option_text, (option_rect.x + 10, option_rect.y + 5))

# Main loop
running = True
dropdown_options.extend(load_network_files())  # Load network files into dropdown

while running:
    screen.fill(WHITE)
    
    draw_buttons()
    draw_dropdown()

    # Get mouse position to check hover state
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for label, rect in buttons.items():
                if rect.collidepoint(mouse_pos):
                    button_pressed[label] = True  # Set button to pressed state
                    append_to_queue(label)  # Append to the queue file
            
            # Handle dropdown click
            if dropdown_rect.collidepoint(mouse_pos):
                dropdown_open = not dropdown_open  # Toggle dropdown open/close
            elif dropdown_open:
                # Check if clicked on any option in dropdown
                for i, option in enumerate(dropdown_options):
                    option_rect = pygame.Rect(dropdown_rect.x, dropdown_rect.y + (i + 1) * dropdown_rect.height, dropdown_rect.width, dropdown_rect.height)
                    if option_rect.collidepoint(mouse_pos):
                        selected_network = option  # Set the selected network
                        append_to_queue(f"NETWORK_CHANGE : {selected_network}")  # Append network change to the queue
                        dropdown_open = False  # Close the dropdown

        if event.type == pygame.MOUSEBUTTONUP:
            for label in button_pressed:
                button_pressed[label] = False  # Reset button to unpressed state
    
    # Update hover state
    for label, rect in buttons.items():
        if rect.collidepoint(mouse_pos):
            button_hovered[label] = True
        else:
            button_hovered[label] = False

    pygame.display.flip()

# Clean up Pygame
pygame.quit()
