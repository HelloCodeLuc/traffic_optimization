import os
import re
import numpy as np
from datetime import datetime
import xml.etree.ElementTree as ET
import csv
import traci
import subprocess
import random
import glob
import time
from multiprocessing import Process, Queue

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

def extract_network_edges(network_file, output_csv_file):
    tree = ET.parse(network_file)
    root = tree.getroot()

    # Open CSV file for writing
    with open(output_csv_file, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write the header row
        csv_writer.writerow(['Edge_ID', 'From', 'To'])

        # Iterate over all 'edges' elements in the XML
        for edge in root.findall('edge'):
            edge_id = edge.get('id')
            from_junction = edge.get('from')
            to_junction = edge.get('to')

            # Write to CSV if x and y exist
            if from_junction and to_junction:
                csv_writer.writerow([edge_id, from_junction, to_junction])
    
    print(f"Edges extracted and saved to {output_csv_file}")

def read_edge_file(file_path):
    """
    Reads an edge file and returns a dictionary indexed by edge IDs.

    :param file_path: Path to the input file.
    :return: Dictionary with edge IDs as keys and tuples (From, To) as values.
    """
    edge_dict = {}

    # Get the directory of the script file
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Print the script's directory
    print("Script's directory:", script_directory)

    with open(file_path, 'r') as file:
        # Skip the title line
        next(file)

        # Process each line in the file
        for line in file:
            line = line.strip()
            if line:  # Skip empty lines
                edge_id, from_junction, to_junction = line.split(',')
                edge_dict[edge_id] = (from_junction, to_junction)

    return edge_dict

# Run randomtrips.py to generate random trips and save them to a file
def generate_random_trips(network_selection, trip_file, max_steps, seed):
    debug = 0
    #cmd = f"C:/Users/chuny/Desktop/lucas/Python%20Projects/traffic_optimization/randomTrips.py -n OSM_RandomTrips/keeleandmajmack.net.xml -r {trip_file} -e {max_steps} --random -s {seed} -o out/trips.trips.xml"
    randomTrips = r'"C:\Program Files (x86)\Eclipse\Sumo\tools\randomTrips.py"'
    cmd = f"python {randomTrips} -n {network_selection} -r {trip_file} -e {max_steps} --random -s {seed}"

    print (f"This is the CMD line {cmd}")

    if (debug):print (f"DEBUG <generate_random_trips> : randomTrips.py command : {cmd}")

    subprocess.call(cmd, shell=True)

def generate_random_trips_weighted(network_selection, trip_file, max_steps, seed, weight_prefix):
    debug = 0
    #cmd = f"C:/Users/chuny/Desktop/lucas/Python%20Projects/traffic_optimization/randomTrips.py -n OSM_RandomTrips/keeleandmajmack.net.xml -r {trip_file} -e {max_steps} --random -s {seed} -o out/trips.trips.xml"
    randomTrips = r'"C:\Program Files (x86)\Eclipse\Sumo\tools\randomTrips.py"'
    cmd = f"python {randomTrips} --weights-prefix {weight_prefix} -n {network_selection} -r {trip_file} -e {max_steps} --random -s {seed}"

    print (f"This is the CMD line {cmd}")

    if (debug):print (f"DEBUG <generate_random_trips> : randomTrips.py command : {cmd}")

    subprocess.call(cmd, shell=True)

# Generate the SUMO configuration file with the given template
def generate_sumo_config(network_selection, config_file, current_directory, max_steps, route_files):
    config_template = f"""<configuration>
    <input>
        <net-file value="{current_directory}/{network_selection}"/>
        <route-files value="{current_directory}/{route_files}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="{max_steps}"/>
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

def extract_speeds_from_edges(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Dictionary to store speed values associated with edge IDs
    edge_speeds = {}

    # Iterate through all the <edge> elements in the XML
    for edge in root.findall(".//edge"):
        edge_id = edge.attrib.get('id')  # Get the edge ID
        edge_function = edge.attrib.get("function", "")
        
        # Skip processing if function="internal"
        if edge_function == "internal":
            continue
        
        # Find the lane within the current edge element
        lane = edge.find(".//lane")
        if lane is not None:
            speed = lane.attrib.get("speed")  # Get the speed attribute
            if speed:
                edge_speeds[edge_id] = round(float(speed)*3.6, 3)
                print(edge_id, edge_speeds[edge_id])
    return edge_speeds

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
    
def calculate_average_difference(file1, file2):
    speeds1 = read_average_speeds(file1)
    speeds2 = read_average_speeds(file2)

    common_edges = set(speeds1.keys()) & set(speeds2.keys())
    if not common_edges:
        print("No common Edge IDs found between the files.")
        return None, None

    differences = {edge: abs(speeds1[edge] - speeds2[edge]) for edge in common_edges}
    average_difference = sum(differences.values()) / len(differences)

    # Identify the edge with the largest discrepancy
    max_discrepancy_edge = max(differences, key=differences.get)
    max_discrepancy_value = differences[max_discrepancy_edge]

    return average_difference, max_discrepancy_edge, max_discrepancy_value

def read_average_speeds(filename):
    average_speeds = {}
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            edge_id = row['Edge ID'].strip()
            try:
                average_speed = float(row['Average Speed (km/h)'])
                average_speeds[edge_id] = average_speed
            except ValueError:
                continue  # Skip rows with invalid speed data
    return average_speeds


# For a given batch, this summarizes the average speed for all edges across all run_sumo runs
def compute_average_speeds(input_folder, output_file):
    """
    Reads multiple CSV files, keeps all columns unchanged, and averages the last column (Average Speed) per edge.

    :param input_folder: Folder containing the input CSV files.
    :param output_file: Name of the output file where results will be saved.
    """
    speed_data = {}  # Dictionary to store sum of speeds and count per edge
    edge_details = {}  # Stores the first occurrence of each edge's details

    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

    if not csv_files:
        print("No CSV files found in the directory.")
        return

    # Process each CSV file
    for file in csv_files:
        with open(file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Read header

            for row in reader:
                if len(row) < 5:
                    continue  # Skip malformed rows

                edge_id = row[0]
                avg_speed = float(row[4])  # Extract last column (Average Speed)

                # Store the first occurrence of each edge's full details (excluding last column)
                if edge_id not in edge_details:
                    edge_details[edge_id] = row[:-1]  # Keep everything except last column

                # Sum speeds for averaging
                if edge_id in speed_data:
                    speed_data[edge_id]["sum"] += avg_speed
                    speed_data[edge_id]["count"] += 1
                else:
                    speed_data[edge_id] = {"sum": avg_speed, "count": 1}
        os.remove(file)

    # Write results to output file
    with open(output_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)  # Write the original header

        for edge_id, data in speed_data.items():
            avg_speed = data["sum"] / data["count"]
            writer.writerow(edge_details[edge_id] + [round(avg_speed, 3)])  # Keep all columns and update last one

    print(f"Average speeds written to {output_file}")


def run_sumo(config_file, max_steps, result_queue, average_speed_n_steps, out_dir, speed_limit, run_number):
    current_directory = os.getcwd()
    #print(f"current_directory : {current_directory}")
    # Launch SUMO with GUI using the generated configuration file
    sumo_cmd = ["sumo", "-c", f"{config_file}"]
    # if gui_opt:
    #     sumo_cmd = ["sumo-gui", "-c", f"{config_file}"] 

    # Initialize a dictionary to store idle times for each vehicle
    idle_times = {}
    traci.start(sumo_cmd)
    step = 0 
    simulation_step_size = 1
    all_edges = traci.edge.getIDList()
    edge_max_speed = {}

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

    edges = read_edge_file(f"{out_dir}/../GUI_edges.csv")

    #TODO we need to uniquify between bluetooth steps and optimization steps
    # Write the collected average speed data to a CSV file
    if not os.path.exists(f"{out_dir}/GUI_average_speeds_per_run_sumo"):
        os.makedirs(f"{out_dir}/GUI_average_speeds_per_run_sumo")
    output_file = f"{out_dir}/GUI_average_speeds_per_run_sumo/GUI_speeds.{run_number}.csv"
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Edge ID", "from", "to","Speed Limit (km/h)", "Average Speed (km/h)"])  # Write header

        for edge_id, speeds in edge_speeds.items():
            # Exclude junctions (edges with IDs starting with ':')
            if not edge_id.startswith(":"):
                # Calculate the average speed for the edge and round to the nearest thousandth
                if speeds:  # Check to avoid division by zero
                    #average_speed = ((sum(speeds) *3.6)/ len(speeds), 3)
                    average_speed_mps = sum(speeds) / len(speeds)  # Average speed in m/s
                    average_speed_kph = round(average_speed_mps * 3.6, 3)  # Convert to km/h
                    #round(average_speed, 2)
                else:
                    average_speed = edge_max_speed[edge_id]
                (from_junction, to_junction) = edges[edge_id]
                writer.writerow([edge_id, from_junction, to_junction, speed_limit[edge_id], average_speed_kph])  # Write edge and its average speed

    # Calculate average idle time
    average_idle_time = sum(idle_times.values()) / len(idle_times)

    traci.close()

    # Print the average idle time
    print(f"DEBUG INSIDE <run_sumo> : config_file={config_file}, max_steps={max_steps}, Average Idle Time:{average_idle_time}" )
    os.chdir(current_directory)
    result_queue.put(average_idle_time)


def batched_run_sumo (phase, num_batches, num_runs_per_batch, output_folder, network_with_timing, max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, network_selection, debug):
    output_folder_subdir = ""
    if phase == "bluetooth":
        output_folder_subdir = "TRAIN_BLUETOOTH"
    elif phase == "optimize":
        output_folder_subdir = "TRAIN_OPTIMIZATION"

    run_number = 0
    network_name = network_selection.split('/')[0]
    # network_name = os.path.splitext(os.path.splitext(network_selection)[0])[0]
    weight_prefix = f"NETWORKS/{network_name}/weights"

    for run in range(num_batches):
        random_seeds = []
        trip_files = []
        config_files = []
        for batch in range(num_runs_per_batch):
            random_seed = 0
            if (debug == 0):
                random_seed = random.randint(1, 10000)  # Use a different random seed for each run
            else:
                random_seed = debug_seed

            trip_file = os.path.join(f"{output_folder}/{output_folder_subdir}", f"random_trips_{random_seed}.xml")  # Generate a unique trip file name for each run
            print (f"trip file = {trip_file}")
            # Generate random trips
            
            weights_exist = any(f.startswith("weights") for f in os.listdir(network_name))

            if weights_exist:
                generate_random_trips_weighted(weight_prefix, f'{network_with_timing}.temp', trip_file, max_steps, random_seed)
                print("DEBUG: Using Weights")
            else:
                generate_random_trips(f'{network_with_timing}.temp', trip_file, max_steps, random_seed)

            # Generate SUMO configuration file and update the route-files value
            config_file = os.path.join(f"{output_folder}/{output_folder_subdir}", f"sumo_config_{random_seed}.sumocfg")
            print (f"config file = {config_file}")
            generate_sumo_config(f'{network_with_timing}.temp', config_file, current_directory, max_steps, trip_file)

            random_seeds.append(random_seed)
            trip_files.append(trip_file)
            config_files.append(config_file)

        # Create a queue to store the results
        result_queue = Queue()

        # Run the SUMO simulation using the generated configuration file
        # average_idle_time = basic_utilities.run_sumo(config_file, args.gui, int(max_steps))
        processes = []
        average_idle_times_from_batch = []

        # Launch each simulation in a separate process
        for config in config_files:
            run_number = run_number + 1
            process = Process(target=run_sumo, args=(config, int(max_steps), result_queue, average_speed_n_steps, f"{output_folder}/{output_folder_subdir}", speed_limit, run_number))
            processes.append(process)
            process.start()

        # Wait for all processes to finish
        for process in processes:
            process.join()

        # Collect results from the queue
        average_idle_times_from_batch = []
        while not result_queue.empty():
            result = result_queue.get()
            average_idle_times_from_batch.append(result)

        # Write the iteration number to the output_data file
        # output_data_file = output_data.txt
        with open(output_data_file, "a") as f:
            for idx, average_idle_time in enumerate(average_idle_times_from_batch):
                f.write(f"Random Seed: {random_seeds[idx]},")
                f.write(f"Trip File: {trip_files[idx]},")
                f.write(f"Configuration File: {config_files[idx]},")
                f.write(f"Average Idle Time: {average_idle_time}\n")
                if os.path.exists(trip_files[idx]):
                    os.remove(trip_files[idx]) 
                if os.path.exists(config_files[idx]):
                    os.remove(config_files[idx])

        if (debug == 1):
            sys.exit()
    compute_average_speeds(f"{output_folder}/{output_folder_subdir}/GUI_average_speeds_per_run_sumo", f"{output_folder}/{output_folder_subdir}/GUI_average_speeds.csv")