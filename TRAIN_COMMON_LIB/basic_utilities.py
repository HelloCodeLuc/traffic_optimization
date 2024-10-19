import os
import re
import numpy as np
from datetime import datetime

def get_current_datetime():
    # Get the current date and time
    now = datetime.now()
    
    # Format the date and time with underscores between values
    current_datetime_str = now.strftime("%Y_%m_%d_%H_%M_%S")
    
    return current_datetime_str

def hit_space_to_continue():
    print("Press space to continue...")
    while True:
        user_input = input()
        if user_input.lower() == ' ':
            break
    return

def get_most_recent_subdirectory(parent_dir):
    # Get a list of all subdirectories in the given directory
    subdirectories = [d for d in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, d))]
    
    if not subdirectories:
        return None  # No subdirectories found
    
    # Get the full path for each subdirectory and sort them by modification time
    subdirectories = sorted(subdirectories, key=lambda d: os.path.getmtime(os.path.join(parent_dir, d)), reverse=True)
    
    # Return the most recent subdirectory
    return subdirectories[0]

def return_num_of_cores ():
    # Method 1: Using the os module
    num_cores_os = os.cpu_count()
    print(f"Number of CPU cores (os.cpu_count()): {num_cores_os}")
    return num_cores_os

def my_plot(output_data_file):
    import matplotlib.pyplot as plt

     # Read the file and process lines
    with open(output_data_file, 'r') as file:
        lines = file.readlines()

    # Count the number of lines
    num_lines = len(lines)
    print(f"Number of lines in the file: {num_lines}")

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
                print("New overall average:", average_idle_time)
            else:
                print("No match found")

            iteration = index

            # Append to lists
            iteration_numbers.append(iteration)
            average_idle_times.append(float(average_idle_time))

    # Plotting
    plt.plot(iteration_numbers, average_idle_times, marker='o')
    plt.xlabel('Iteration')
    plt.ylabel('Average Idle Time')
    plt.title('Average Idle Time Over Iterations')
    plt.grid(True)
    plt.xlim(left=0)
    #plt.gca().invert_yaxis()
    # Reduce the number of y-axis labels using np.linspace
    plt.yticks(np.linspace(80, 120, 5))
    plt.show()
