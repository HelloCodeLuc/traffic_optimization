import pygame
import sys
import os
import re
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from time import sleep
import ctypes

# Initialize Pygame
pygame.init()

# Set up the window (Enlarged size)
width, height = 900, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("GUI with Tabs")
hwnd = ctypes.windll.user32.GetForegroundWindow()
ctypes.windll.user32.SetWindowPos(hwnd, 0, 100, 100, width, height, 0x0001)

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
    "A": pygame.Rect(100, 450, button_width, button_height),
    "B": pygame.Rect(170, 450, button_width, button_height),
    "C": pygame.Rect(240, 450, button_width, button_height)
}

button_pressed = {"A": False, "B": False, "C": False}
button_hovered = {"A": False, "B": False, "C": False}

# Define tabs
tab_font = pygame.font.Font(None, 28)
tabs = {
    "Main": pygame.Rect(10, 0, 180, 40),
    "Bluetooth Training": pygame.Rect(200, 0, 180, 40),
    "Sim Optimization": pygame.Rect(390, 0, 180, 40)
}
current_page = "Main"

# Define font
font = pygame.font.Font(None, 36)
dropdown_font = pygame.font.Font(None, 24)

# Dropdown variables
dropdown_open = False
dropdown_rect = pygame.Rect(120, 400, 300, 30)
dropdown_options = ["default_network"]
selected_network = "default_network"

current_dir = os.getcwd()
network_dir = os.path.join(current_dir, "../../NETWORKS")
output_file = '../REFERENCE_DATA/output.good/network_averages.txt'

# Function to create the plot using matplotlib and render it as a surface in pygame
def my_plot(output_data_file):
    # Read the file and process lines
    with open(output_data_file, 'r') as file:
        lines = file.readlines()

    # Extract and plot Average Idle Times
    iteration_numbers = []
    average_idle_times = []

    for index, line in enumerate(lines):
        if "keep" in line or "throw" in line: 
            # Extract information from each line
            pattern = r"New overall average: (\d+\.\d{2})"

            # Use re.search to find the match in the line
            match = re.search(pattern, line)

            # Check if a match is found and extract the value
            if match:
                average_idle_time = match.group(1)
                iteration = index

                # Append to lists
                iteration_numbers.append(iteration)
                average_idle_times.append(float(average_idle_time))

    # Create a figure and plot the data
    fig, ax = plt.subplots(figsize=(5, 3))  # Adjust the figure size if needed
    ax.plot(iteration_numbers, average_idle_times, marker='o')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Average Idle Time')
    ax.set_title('Average Idle Time Over Iterations')
    ax.grid(True)
    ax.set_xlim(left=0)

    # Reduce the number of y-axis labels using np.linspace
    ax.set_yticks(np.linspace(80, 120, 5))

    # Add padding at the bottom for the x-axis label
    plt.subplots_adjust(bottom=0.2)  # Adjust as needed for enough bottom space

    # Create a canvas and draw the figure onto it
    canvas = FigureCanvas(fig)
    canvas.draw()

    # Convert the plot to a Pygame surface
    raw_data = canvas.tostring_rgb()
    size = canvas.get_width_height()
    plot_surface = pygame.image.fromstring(raw_data, size, "RGB")
    
    plt.close(fig)  # Close the figure to free up resources
    return plot_surface

# Function to check if the file has been updated
def has_file_updated(file_path, last_mod_time):
    try:
        current_mod_time = os.path.getmtime(file_path)
        if current_mod_time != last_mod_time:
            return current_mod_time
    except FileNotFoundError:
        pass
    return last_mod_time

# Function to check if the file has been modified
def file_modified(file_path, last_modified):
    return os.path.getmtime(file_path) > last_modified

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

# Function to draw buttons with shadow and hover effect
def draw_buttons():
    for label, rect in buttons.items():
        if button_pressed[label]:
            pygame.draw.rect(screen, SHADOW, (rect.x + 3, rect.y + 3, rect.width, rect.height))
            pygame.draw.rect(screen, DARK_GRAY, rect)
        else:
            pygame.draw.rect(screen, SHADOW, (rect.x + 5, rect.y + 5, rect.width, rect.height))
            pygame.draw.rect(screen, GRAY, rect)
        
        if button_hovered[label]:
            pygame.draw.rect(screen, WHITE, rect, 3)
        
        text = font.render(label, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

# Function to draw tabs with angled sides, wider at the bottom, and a visible line for unselected tabs
def draw_tabs():
    # Track the rightmost edge of the last tab
    last_tab_right_edge = 0
    for label, rect in tabs.items():
        # Determine the color and whether the tab is selected
        is_selected = label == current_page
        color = BLUE if is_selected else GRAY

        # Calculate points for an angled, wider-at-bottom tab shape
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        if is_selected:
            # Points for a selected tab (top slightly narrower)
            points = [(x - 5, y + h), (x + 5, y), (x + w - 5, y), (x + w + 5, y + h)]
        else:
            # Points for an unselected tab with a bottom line
            points = [(x - 5, y + h), (x + 5, y), (x + w - 5, y), (x + w + 5, y + h)]
            # Draw a 1-pixel black line at the bottom of unselected tabs
            pygame.draw.line(screen, BLACK, (x - 5, y + h), (x + w + 5, y + h), 4)

        # Draw the tab shape
        pygame.draw.polygon(screen, color, points)

        # Draw the tab label text
        text = tab_font.render(label, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

        # Update the right edge of the last tab
        last_tab_right_edge = max(last_tab_right_edge, x + w + 5)

    # Draw a black line from the bottom-right of the last tab to the right border of the screen
    pygame.draw.line(screen, BLACK, (last_tab_right_edge, y + h), (width, y + h), 4)

# Function to draw dropdown
def draw_dropdown():
    global selected_network
    label_text = dropdown_font.render("Network:", True, BLACK)
    screen.blit(label_text, (20, 405))

    pygame.draw.rect(screen, GRAY, dropdown_rect)
    text = dropdown_font.render(selected_network, True, BLACK)
    screen.blit(text, (dropdown_rect.x + 10, dropdown_rect.y + 5))

    if dropdown_open:
        for i, option in enumerate(dropdown_options):
            option_rect = pygame.Rect(dropdown_rect.x, dropdown_rect.y + (i + 1) * dropdown_rect.height, dropdown_rect.width, dropdown_rect.height)
            pygame.draw.rect(screen, BLUE if option == selected_network else GRAY, option_rect)
            option_text = dropdown_font.render(option, True, BLACK)
            screen.blit(option_text, (option_rect.x + 10, option_rect.y + 5))

# Main page drawing function
def draw_page(plot_surface):
    if current_page == "Main":
        # Draw the plot on the Default page
        screen.blit(plot_surface, (50, 70))  # Positioning the plot near the top
        draw_buttons()
        draw_dropdown()
    elif current_page == "Bluetooth Training":
        # Placeholder for Bluetooth Training page content
        text = font.render("Bluetooth Training Page", True, BLACK)
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2))
    elif current_page == "Sim Optimization":
        # Placeholder for Sim Optimization page content
        text = font.render("Sim Optimization Page", True, BLACK)
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2))

# Main loop
running = True
dropdown_options.extend(["network1.net.xml", "network2.net.xml"])  # Example dropdown options

# Initialize last modified time for the file
file_path = '../REFERENCE_DATA/output.good/network_averages.txt'
last_modified = os.path.getmtime(file_path)

# Load the plot as an image surface
plot_surface = my_plot(file_path)

# Set up a timer event to check for file modifications
FILE_MODIFIED_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(FILE_MODIFIED_EVENT, 100)  # Check every 100ms

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.VIDEORESIZE:
            # Ignore resize events
            pass
        if event.type == pygame.WINDOWRESIZED:
            # Handle resize event
            pass

        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        
        if event.type == FILE_MODIFIED_EVENT:
            # Check if the file has been modified
            if file_modified(file_path, last_modified):
                last_modified = os.path.getmtime(file_path)
                plot_surface = my_plot(file_path)  # Update the plot

        if event.type == pygame.MOUSEBUTTONDOWN:
            for label, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    button_pressed[label] = True  # Set button to pressed state
                    append_to_queue(label)  # Append to the queue file

            if dropdown_rect.collidepoint(event.pos):
                dropdown_open = not dropdown_open
            elif dropdown_open:
                for i, option in enumerate(dropdown_options):
                    option_rect = pygame.Rect(dropdown_rect.x, dropdown_rect.y + (i + 1) * dropdown_rect.height, dropdown_rect.width, dropdown_rect.height)
                    if option_rect.collidepoint(event.pos):
                        selected_network = option
                        dropdown_open = False

            # Tab switching
            for label, rect in tabs.items():
                if rect.collidepoint(event.pos):
                    current_page = label

        if event.type == pygame.MOUSEBUTTONUP:
            for label in button_pressed:
                button_pressed[label] = False
    
    # Update hover state
    mouse_pos = pygame.mouse.get_pos()
    for label, rect in buttons.items():
        button_hovered[label] = rect.collidepoint(mouse_pos)

    # Draw UI components
    draw_tabs()
    draw_page(plot_surface)
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
