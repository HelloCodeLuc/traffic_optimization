import pygame
import sys
import os
import re
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import ctypes
import bluetooth_gui_lib
import plot_timing_changes

sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_COMMON_LIB'))

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (169, 169, 169)
SHADOW = (100, 100, 100)
BLUE = (173, 216, 230)

figure_width = 400
offset = 25

# Define button properties
button_width, button_height = 60, 30
buttons = {
    "RUN": pygame.Rect(2*figure_width + offset*10, offset*2, button_width, button_height),
    "DEMO": pygame.Rect(2*figure_width + offset*13, offset*2, button_width, button_height),
    "C": pygame.Rect(2*figure_width + offset*16, offset*2, button_width, button_height)
}

# Store button click state (for shadow effect)
button_pressed = {"RUN": False, "DEMO": False, "C": False}

# Store hover state
button_hovered = {"RUN": False, "DEMO": False, "C": False}

# # Path to the output file
output_file = '../REFERENCE_DATA/output.good/network_averages.txt'

# Function to draw tabs with angled sides, wider at the bottom, and a visible line for unselected tabs
def draw_tabs(tabs, current_page, screen, tab_font, width):
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

# Function to draw buttons with shadow and hover effect
#def draw_buttons(buttons, button_pressed, button_hovered, screen, font, dropdown_font, SHADOW, GRAY, BLACK, WHITE, DARK_GRAY):
def draw_buttons(screen, font, simulation_state):
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
        if label == "RUN":
            if simulation_state == "RUN":
                text = font.render("STOP", True, BLACK)
            else:
                text = font.render("RUN", True, BLACK)
        else:
            text = font.render(label, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

# Function to append to command_queue.txt
def append_to_queue(command):
    with open("out/command_queue.txt", "w") as file:
        file.write(command + "\n")
    with open("out/command_queue_last.txt", "w") as file:
        file.write(command + "\n")

# Updated function to load network files with .net.xml extension
def load_network_dirs(network_dir):
    dirs = []
    if os.path.exists(network_dir) and os.path.isdir(network_dir):
        # List all files in the NETWORKS directory
        for dir in os.listdir(network_dir):
            dirs.append(dir)
    return dirs

# Function to draw dropdown menu
#def draw_dropdown(selected_network, screen, dropdown_open, dropdown_font, dropdown_options, dropdown_rect, GRAY, BLACK):
def draw_dropdown(dropdown_font, dropdown_options, screen, dropdown_rect, dropdown_open, selected_network, figure_width):
    # Draw the "Network: " label
    label_text = dropdown_font.render("Network:", True, BLACK)
    screen.blit(label_text, (20, 60))  # Positioned to the left of the dropdown

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
    ax.set_yticks(np.linspace(0, 120, 5))

    # Create a canvas and draw the figure onto it
    canvas = FigureCanvas(fig)
    canvas.draw()

    # Convert the plot to a Pygame surface
    raw_data = canvas.tostring_rgb()
    size = canvas.get_width_height()
    plot_surface = pygame.image.fromstring(raw_data, size, "RGB")
    
    plt.close(fig)  # Close the figure to free up resources
    return plot_surface

# #
def my_bluetooth(junction_coordinates_file, average_speeds_file, network_file, bluetooth_training_network_averages):

    # Read input files
    file_name = "RESOURCES/CONNECTING_TWO_POINTS/GUI_junction_coordinates.csv"
    junction_coordinates = bluetooth_gui_lib.read_GUI_junction_coordinates(junction_coordinates_file)

    file_path = "RESOURCES/CONNECTING_TWO_POINTS/GUI_average_speeds.csv"
    edge_data = bluetooth_gui_lib.read_edge_data(average_speeds_file)

    # Road width
    road_width = 8

    # Create Matplotlib figure
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_aspect('equal')
    ax.set_facecolor('black')

    # Set a black border around the figure
    fig.patch.set_edgecolor('black')
    fig.patch.set_linewidth(2)  # Border thickness

    # Remove extra padding
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Draw roads and nodes
    for edge in edge_data:
        from_node = edge['from_node']
        to_node = edge['to_node']
        point1 = junction_coordinates[from_node]
        point2 = junction_coordinates[to_node]
        average_speed = edge['average_speed']
        speed_limit = edge['speed_limit']
        bluetooth_gui_lib.draw_two_way_road(ax, point1, point2, road_width, average_speed, speed_limit)

    # Draw nodes
    if network_file != "":
        coord_differences = plot_timing_changes.coordinates_to_diff_of_offset_and_greenlight (f"NETWORKS/{network_file}", junction_coordinates_file, bluetooth_training_network_averages)

        for node_position in junction_coordinates.values():
            bluetooth_gui_lib.draw_node(ax, node_position, coord_differences)
    else:
        for node_position in junction_coordinates.values():
            bluetooth_gui_lib.draw_node(ax, node_position, None)

    # Remove axis labels and ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    # Convert Matplotlib figure to Pygame surface
    pygame_surface = bluetooth_gui_lib.fig_to_pygame(fig)
    plt.close(fig)
    return pygame_surface

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
    return os.path.getmtime(file_path) != last_modified

def find_latest_directory(base_folder):
    """
    Find the latest directory under the specified base folder.

    Parameters:
        base_folder (str): The path to the base folder.

    Returns:
        str: The path to the latest directory, or None if no directories are found.
    """
    if not os.path.exists(base_folder):
        print(f"The folder '{base_folder}' does not exist.")
        return None

    # List all directories in the base folder
    directories = [
        os.path.join(base_folder, d) for d in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, d))
    ]

    if not directories:
        #print(f"No directories found in '{base_folder}'.")
        return None

    # Find the latest directory by modification time
    latest_directory = max(directories, key=os.path.getmtime)
    return latest_directory

# Main page drawing function
def draw_page(gui_colour, output_dir, figure_width, plot_surface_average_idle, plot_surface_optimize_start, 
                  plot_surface_optimize_current, plot_surface_bluetooth_reference, 
                  plot_surface_bluetooth_start, plot_surface_bluetooth_current, current_page, screen, width, 
                  height, font, dropdown_font, dropdown_options, dropdown_rect, dropdown_open, selected_network, 
                  simulation_state):
    if gui_colour == "blue":
        # Draw the white bar at the top (x=0, y=0, width=full screen, height=200)
        pygame.draw.rect(screen, (175, 238, 238), (0, 40, width, height))

    if current_page == "Main":

        if plot_surface_bluetooth_reference is not None:
            screen.blit(plot_surface_bluetooth_reference, (offset, offset*5))
        else:
            pygame.draw.rect(screen, WHITE, (offset, offset*5, figure_width, figure_width))
            pygame.draw.rect(screen, BLACK, (offset, offset*5, figure_width, figure_width), 2)

        if plot_surface_bluetooth_current is not None:
            screen.blit(plot_surface_bluetooth_current, (offset + figure_width + offset, offset*5))
        else:
            pygame.draw.rect(screen, WHITE, (offset + figure_width + offset, offset*5, figure_width, figure_width))
            pygame.draw.rect(screen, BLACK, (offset + figure_width + offset, offset*5, figure_width, figure_width), 2)

        if plot_surface_optimize_current is not None:
            screen.blit(plot_surface_optimize_current, (3*offset + 2*figure_width, offset*5))
        else:
            pygame.draw.rect(screen, WHITE, (3*offset + 2*figure_width, offset*5, figure_width, figure_width))
            pygame.draw.rect(screen, BLACK, (3*offset + 2*figure_width, offset*5, figure_width, figure_width), 2)

        text = font.render("Bluetooth Reference", True, BLACK)
        screen.blit(text, (offset, offset*4))
        text = font.render("Bluetooth Current", True, BLACK)
        screen.blit(text, (offset + figure_width + offset, offset*4))
        text = font.render("Optimize Current", True, BLACK)
        screen.blit(text, (3*offset + 2*figure_width, offset*4))

        draw_buttons(screen, font, simulation_state)

        phase = "Start"
        if os.path.exists(f"{output_dir}/TRAIN_OPTIMIZATION"):
            phase = "Geenlight/Offset Optimization"
        elif os.path.exists(f"{output_dir}/TRAIN_BLUETOOTH"):
            phase = "Align to Bluetooth Reference"

        text = font.render(f"Phase: {phase}", True, BLACK)
        screen.blit(text, (10, figure_width + 140))
        text = font.render(f"TODO - DEMO file snap, then add back cfg cleanup", True, BLACK)
        screen.blit(text, (10, figure_width + 160))
        text = font.render(f"TODO - fix the phase to update", True, BLACK)
        screen.blit(text, (10, figure_width + 180))
        text = font.render(f"TODO - why is a few lights offset and greenlight timing changes not showing", True, BLACK)
        screen.blit(text, (10, figure_width + 200))
        draw_dropdown(dropdown_font, dropdown_options, screen, dropdown_rect, dropdown_open, selected_network, figure_width)
    elif current_page == "Bluetooth Training":
        if plot_surface_bluetooth_reference is not None:
            screen.blit(plot_surface_bluetooth_reference, (offset, 100))
        else:
            # Draw black border (outline)
            pygame.draw.rect(screen, BLACK, (offset, 100, figure_width, figure_width), 2)
            
        if plot_surface_bluetooth_start is not None:
            screen.blit(plot_surface_bluetooth_start, (offset + figure_width + offset, 100))
        else:
            # Draw black border (outline)
            pygame.draw.rect(screen, BLACK, (offset + figure_width + offset, 100, figure_width, figure_width), 2)

        if plot_surface_bluetooth_current is not None:
            screen.blit(plot_surface_bluetooth_current, (3*offset + 2*figure_width, 100))
        else:
            # Draw black border (outline)
            pygame.draw.rect(screen, BLACK, (3*offset + 2*figure_width, 100, figure_width, figure_width), 2)

        text = font.render("Reference", True, BLACK)
        screen.blit(text, (offset, 75))
        text = font.render("Start", True, BLACK)
        screen.blit(text, (offset + figure_width + offset, 75))
        text = font.render("Current", True, BLACK)
        screen.blit(text, (3*offset + 2*figure_width, 75))
        
    elif current_page == "Sim Optimization":

        # Draw the plot on the Default page
        if plot_surface_average_idle is not None:
            screen.blit(plot_surface_average_idle, (offset, figure_width + offset*5))  
        else:
            # Draw black border (outline)
            pygame.draw.rect(screen, BLACK, (offset, figure_width + offset*5, figure_width, figure_width), 2)
        
        if plot_surface_optimize_start is not None:
            screen.blit(plot_surface_optimize_start, (offset, offset*4))
        else:
            # Draw black border (outline)
            pygame.draw.rect(screen, BLACK, (offset, offset*4, figure_width, figure_width), 2)
            
        if plot_surface_optimize_current is not None:
            screen.blit(plot_surface_optimize_current, (offset + figure_width + offset, offset*4))
        else:
            # Draw black border (outline)
            pygame.draw.rect(screen, BLACK, (offset + figure_width + offset, offset*4, figure_width, figure_width), 2)

        text = font.render("Start", True, BLACK)
        screen.blit(text, (offset, 75))
        text = font.render("Current", True, BLACK)
        screen.blit(text, (offset + figure_width + offset, 75))

def gui_main(gui_colour, output_dir):

    # Initialize Pygame
    pygame.init()

    # Set up the window (Enlarged size)
    width, height = figure_width*3 + offset*4, 900
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("TRAFFIC OPTIMIZER")
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    ctypes.windll.user32.SetWindowPos(hwnd, 0, 100, 100, width, height, 0x0001)

    # Define tabs
    tab_font = pygame.font.Font(None, 28)
    tabs = {
        "Main": pygame.Rect(10, 0, 180, 40),
        "Bluetooth Training": pygame.Rect(200, 0, 180, 40),
        "Sim Optimization": pygame.Rect(390, 0, 180, 40)
    }
    current_page = "Main"

    # Define font
    font = pygame.font.Font(None, 28)
    dropdown_font = pygame.font.Font(None, 24)  # Smaller font for the dropdown

    # Dropdown variables
    dropdown_open = False
    dropdown_rect = pygame.Rect(120, 60, 300, 30)  # Adjusted position for dropdown
    dropdown_options = ["--Select Network--"]
    selected_network = "--Select Network--"

    # Define the relative path to the network directory with respect to current working directory
    current_dir = os.getcwd()
    network_dir = os.path.join(current_dir, "NETWORKS")

    running = True
    dropdown_options.extend(load_network_dirs(network_dir))  # Load network files into dropdown

    simulation_state = "STOP"

    if not os.path.exists("out"):
        os.makedirs("out")

    # Set up a timer event to check for file modifications
    FILE_MODIFIED_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(FILE_MODIFIED_EVENT, 100)  # Check every 100ms

    # Load the plot as an image surface
    last_modified_optimize_network_averages_txt = 0 
    last_modified_optimize_start_GUI_average_speeds = 0
    last_modified_optimize_current_GUI_average_speeds = 0
    plot_surface_average_idle = None
    plot_surface_optimize_start = None
    plot_surface_optimize_current = None
    
    last_modified_bluetooth_reference_average_speeds = 0
    plot_surface_bluetooth_reference = None
    last_modified_bluetooth_start_average_speeds = 0
    plot_surface_bluetooth_start = None
    last_modified_bluetooth_current_average_speeds = 0
    plot_surface_bluetooth_current = None
    
    while running:
        junction_coords_file = f"{output_dir}\\GUI_junction_coordinates.csv"

        optimize_network_averages_txt = f'{output_dir}/TRAIN_OPTIMIZATION/network_averages.txt'
        optimize_start_GUI_average_speeds = f'{output_dir}/TRAIN_OPTIMIZATION/GUI_average_speeds.start.csv'
        optimize_current_GUI_average_speeds = f'{output_dir}/TRAIN_OPTIMIZATION/GUI_average_speeds.csv'

        bluetooth_training_reference_average_speeds_file = f"NETWORKS/{network_dir}/{network_dir}.bluetooth.csv"
        bluetooth_training_start_average_speeds_file = f"{output_dir}/TRAIN_BLUETOOTH/GUI_average_speeds.start.csv"
        bluetooth_training_current_average_speeds_file = f"{output_dir}/TRAIN_BLUETOOTH/GUI_average_speeds.csv"
        bluetooth_training_network_averages = f"{output_dir}/TRAIN_BLUETOOTH/network_averages.txt"
        # network_file = f"NETWORKS/{network_dir}/{network_dir}.net.xml"

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
                if os.path.exists(optimize_network_averages_txt):
                    if file_modified(optimize_network_averages_txt, last_modified_optimize_network_averages_txt):
                        last_modified_optimize_network_averages_txt = os.path.getmtime(optimize_network_averages_txt)
                        plot_surface_average_idle = my_plot(optimize_network_averages_txt) 
                if os.path.exists(optimize_start_GUI_average_speeds):
                    if file_modified(optimize_start_GUI_average_speeds, last_modified_optimize_start_GUI_average_speeds):
                        last_modified_optimize_start_GUI_average_speeds = os.path.getmtime(optimize_start_GUI_average_speeds)
                        plot_surface_optimize_start = my_bluetooth(junction_coords_file, optimize_start_GUI_average_speeds, "", "")
                if os.path.exists(optimize_current_GUI_average_speeds):
                    if file_modified(optimize_current_GUI_average_speeds, last_modified_optimize_current_GUI_average_speeds):
                        last_modified_optimize_current_GUI_average_speeds = os.path.getmtime(optimize_current_GUI_average_speeds)
                        plot_surface_optimize_current = my_bluetooth(junction_coords_file, optimize_current_GUI_average_speeds,
                                                                     selected_network, optimize_network_averages_txt) 
                if os.path.exists(bluetooth_training_reference_average_speeds_file) and os.path.exists(junction_coords_file):
                    if file_modified(bluetooth_training_reference_average_speeds_file, last_modified_bluetooth_reference_average_speeds):   
                        last_modified_bluetooth_reference_average_speeds = os.path.getmtime(bluetooth_training_reference_average_speeds_file)
                        plot_surface_bluetooth_reference = my_bluetooth(junction_coords_file, bluetooth_training_reference_average_speeds_file, "", "")
                if os.path.exists(bluetooth_training_start_average_speeds_file):
                    if file_modified(bluetooth_training_start_average_speeds_file, last_modified_bluetooth_start_average_speeds):   
                        last_modified_bluetooth_start_average_speeds = os.path.getmtime(bluetooth_training_start_average_speeds_file)
                        plot_surface_bluetooth_start = my_bluetooth(junction_coords_file, bluetooth_training_start_average_speeds_file, "", "")
                if os.path.exists(bluetooth_training_current_average_speeds_file):
                    if file_modified(bluetooth_training_current_average_speeds_file, last_modified_bluetooth_current_average_speeds):   
                        last_modified_bluetooth_current_average_speeds = os.path.getmtime(bluetooth_training_current_average_speeds_file)
                        plot_surface_bluetooth_current = my_bluetooth(junction_coords_file, bluetooth_training_current_average_speeds_file, "", "")

            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        queue_message = label
                        if label == "RUN" :
                            if not selected_network == "--Select Network--":
                                if simulation_state == "RUN":
                                    simulation_state = "STOP"
                                else:
                                    simulation_state = "RUN"
                                queue_message = simulation_state
                                button_pressed[label] = True  # Set button to pressed state
                                append_to_queue(queue_message)  # Append to the queue file
                        elif label == "DEMO" :
                            queue_message = label
                            button_pressed[label] = True  # Set button to pressed state
                            append_to_queue(queue_message)  # Append to the queue file
                        else:
                            button_pressed[label] = True  # Set button to pressed state
                            append_to_queue(queue_message)  # Append to the queue file
                
                # Handle dropdown click
                if dropdown_rect.collidepoint(event.pos):
                    dropdown_open = not dropdown_open  # Toggle dropdown open/close
                elif dropdown_open:
                    # Check if clicked on any option in dropdown
                    for i, option in enumerate(dropdown_options):
                        option_rect = pygame.Rect(dropdown_rect.x, dropdown_rect.y + (i + 1) * dropdown_rect.height, dropdown_rect.width, dropdown_rect.height)
                        if option_rect.collidepoint(event.pos):
                            network_dir = option
                            selected_network = f"{network_dir}/{network_dir}.net.xml"  # Set the selected network
                            append_to_queue(f"NETWORK_CHANGE : {selected_network}")  # Append network change to the queue
                            dropdown_open = False  # Close the dropdown

                # Tab switching
                for label, rect in tabs.items():
                    if rect.collidepoint(event.pos):
                        current_page = label

            if event.type == pygame.MOUSEBUTTONUP:
                for label in button_pressed:
                    button_pressed[label] = False  # Reset button to unpressed state
        
        # Get mouse position to check hover state
        mouse_pos = pygame.mouse.get_pos()

        # Update hover state
        for label, rect in buttons.items():
            if rect.collidepoint(mouse_pos):
                button_hovered[label] = True
            else:
                button_hovered[label] = False

        #if basic_utilities.check_queue_has_command("MAX", "out/command_queue.txt", 0): 
        #    simulation_state = "STOP"
        # Draw UI components
        draw_tabs(tabs, current_page, screen, tab_font, width )
        draw_page(gui_colour, output_dir, figure_width, plot_surface_average_idle, plot_surface_optimize_start, plot_surface_optimize_current, plot_surface_bluetooth_reference, 
                  plot_surface_bluetooth_start, plot_surface_bluetooth_current, current_page, screen, width, 
                  height, font, dropdown_font, dropdown_options, dropdown_rect, dropdown_open, selected_network, simulation_state)

        pygame.display.flip()

        # Limit the frame rate to 60 FPS
        pygame.time.Clock().tick(60)

    # Clean up Pygame
    pygame.quit()