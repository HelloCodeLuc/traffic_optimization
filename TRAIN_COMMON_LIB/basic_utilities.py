import os
import re
import numpy as np
from datetime import datetime
import xml.etree.ElementTree as ET
import csv
import traci
import subprocess

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

def extract_network_junctions(network_file, output_csv_file):
    tree = ET.parse(network_file)
    root = tree.getroot()

    # Open CSV file for writing
    with open(output_csv_file, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write the header row
        csv_writer.writerow(['Junction ID', 'X Coordinate', 'Y Coordinate'])

        # Iterate over all 'junction' elements in the XML
        for junction in root.findall('junction'):
            junction_id = junction.get('id')
            x_coord = junction.get('x')
            y_coord = junction.get('y')

            # Write to CSV if x and y exist
            if x_coord and y_coord:
                csv_writer.writerow([junction_id, x_coord, y_coord])
    
    print(f"Coordinates extracted and saved to {output_csv_file}")
    
# Run randomtrips.py to generate random trips and save them to a file
def generate_random_trips(network_selection, trip_file, max_steps, seed):
    debug = 0
    #cmd = f"C:/Users/chuny/Desktop/lucas/Python%20Projects/traffic_optimization/randomTrips.py -n OSM_RandomTrips/keeleandmajmack.net.xml -r {trip_file} -e {max_steps} --random -s {seed} -o out/trips.trips.xml"
    randomTrips = r'"C:\Program Files (x86)\Eclipse\Sumo\tools\randomTrips.py"'
    cmd = f"python {randomTrips} -n {network_selection} -r {trip_file} -e {max_steps} --random -s {seed}"

    print (f"This is the CMD line {cmd}")

    if (debug):print (f"DEBUG <generate_random_trips> : randomTrips.py command : {cmd}")

    subprocess.call(cmd, shell=True)

# Generate the SUMO configuration file with the given template
def generate_sumo_config(network_selection, config_file, current_directory, route_files):
    config_template = f"""<configuration>
    <input>
        <net-file value="{current_directory}/{network_selection}"/>
        <route-files value="{current_directory}/{route_files}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="2000"/>
    </time>
</configuration>"""
    print (f"DEBUG INSIDE 4 {config_file}")
    with open(config_file, 'w') as f:
        f.write(config_template)
    f.close()

#creates a new network file with changed traffic light changes to run simulations from
#the comment pattern represents a specific traffic light label
def create_target_net_xml_temp(comment_pattern, target_net_file, modified_lines):
    is_comment_section = False
    with open(f'{target_net_file}.temp', 'w') as WFH:
        inside_tlLogic = False
        with open(target_net_file, 'r') as file:
             for line in file:
                # Check if the comment pattern is present in the line
                if "<tlLogic" in line and comment_pattern in line:
                    inside_tlLogic = True
                elif inside_tlLogic:
                    if "</tlLogic" in line:
                        inside_tlLogic = False
                        for i in range(len(modified_lines)):
                            WFH.write(f'{modified_lines[i]}\n')
                else: 
                    WFH.write(line)  
        file.close()

    WFH.close()
    return

#Comment pattern represents the intersection. This function will extract traffic light timings for the intersection
def extract_lines_after_comment(filename, comment_pattern):
    result = []
    is_comment_section = False

    with open(filename, 'r') as file:
        for line in file:
            # Check if the comment pattern is present in the line
            if "<tlLogic" in line and comment_pattern in line:
                # Start extracting lines after the comment
                is_comment_section = True

            # Check if we are in the comment section
            if is_comment_section:
                # Append the line to the result
                result.append(line.rstrip('\n'))

                # Check if we have extracted 6 lines
                if "</tlLogic" in line:
                    break

    return result


def run_sumo(config_file, gui_opt, max_steps, result_queue, average_speed_n_steps, out_dir):
    current_directory = os.getcwd()
    #print(f"current_directory : {current_directory}")
    # Launch SUMO with GUI using the generated configuration file
    sumo_cmd = ["sumo", "-c", f"{config_file}"]
    if gui_opt:
        sumo_cmd = ["sumo-gui", "-c", f"{config_file}"] 

    # Initialize a dictionary to store idle times for each vehicle
    idle_times = {}
    traci.start(sumo_cmd)
    step = 0 
    simulation_step_size = 1
    all_edges = traci.edge.getIDList()

    # Initialize a dictionary to store arrays of average speeds for each edge
    edge_speeds = {}

    while step < max_steps:
        traci.simulationStep()
        step += simulation_step_size
        #time.sleep(0.1) #TODO 
        #
        if step > (max_steps-average_speed_n_steps):
            for edge_id in all_edges:
                if not edge_id.startswith(":"):
                    # Get the average speed for the edge at this simulation step
                    avg_speed = traci.edge.getLastStepMeanSpeed(edge_id)             
                    # Add the speed to the hash of arrays
                if edge_id not in edge_speeds:
                    edge_speeds[edge_id] = []  # Initialize the array for this edge
                edge_speeds[edge_id].append(avg_speed)

        # Get the list of vehicles
        vehicles = traci.vehicle.getIDList()

        # Update idle times
        for vehicle_id in vehicles:
            speed = traci.vehicle.getSpeed(vehicle_id)
            if speed < 5:
                if vehicle_id not in idle_times:
                    idle_times[vehicle_id] = 0
                else:
                    idle_times[vehicle_id] += simulation_step_size

    #TODO we need to uniquify between bluetooth steps and optimization steps
    # Write the collected average speed data to a CSV file
    output_file = f"{out_dir}/GUI_average_speeds.csv"
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Edge ID", "Average Speed (m/s)"])  # Write header

        for edge_id, speeds in edge_speeds.items():
            # Exclude junctions (edges with IDs starting with ':')
            if not edge_id.startswith(":"):
                # Calculate the average speed for the edge and round to the nearest thousandth
                if speeds:  # Check to avoid division by zero
                    average_speed = round(sum(speeds) / len(speeds), 3)
                else:
                    average_speed = 0
                writer.writerow([edge_id, average_speed])  # Write edge and its average speed

    # Calculate average idle time
    average_idle_time = sum(idle_times.values()) / len(idle_times)

    traci.close()

    # Print the average idle time
    print(f"DEBUG INSIDE <run_sumo> : config_file={config_file}, gui_opt={gui_opt}, max_steps={max_steps}, Average Idle Time:{average_idle_time}" )
    os.chdir(current_directory)
    result_queue.put(average_idle_time)

def check_queue_has_command (command, queue_file, delete_control):
    if os.path.exists(queue_file):
        found = 0
        with open(queue_file, "r") as f:
            for line in f:
                line = line.strip()
                if line == command:
                    found = 1
        f.close()
        if found == 1:
            if (delete_control == 1):
                print(f">> Removing {queue_file}")
                os.remove(queue_file) 
            return True
        else:
            return False
    else:
        return False