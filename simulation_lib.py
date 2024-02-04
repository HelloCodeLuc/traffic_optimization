import subprocess
import traci
import os
import sys

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
        # Extract information from each line
        parts = line.split(',')
        iteration = index
        average_idle_time = float(parts[-1].split(':')[1])

        # Append to lists
        iteration_numbers.append(iteration)
        average_idle_times.append(average_idle_time)

    # Plotting
    plt.plot(iteration_numbers, average_idle_times, marker='o')
    plt.xlabel('Iteration')
    plt.ylabel('Average Idle Time')
    plt.title('Average Idle Time Over Iterations')
    plt.grid(True)
    plt.xlim(left=0)
    plt.show()

def run_sumo(config_file, gui_opt, max_steps, result_queue):
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
    while step < max_steps:
        traci.simulationStep()
        step += simulation_step_size
        #time.sleep(0.1) #TODO 

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

    # Calculate average idle time
    average_idle_time = sum(idle_times.values()) / len(idle_times)

    traci.close()

    # Print the average idle time
    print(f"DEBUG INSIDE <run_sumo> : config_file={config_file}, gui_opt={gui_opt}, max_steps={max_steps}, Average Idle Time:{average_idle_time}" )
    os.chdir(current_directory)
    result_queue.put(average_idle_time)

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

def hit_space_to_continue():
    print("Press space to continue...")
    while True:
        user_input = input()
        if user_input.lower() == ' ':
            break
    return

# Run randomtrips.py to generate random trips and save them to a file
def generate_random_trips(network_selection, trip_file, max_steps, seed):
    debug = 0
    #cmd = f"C:/Users/chuny/Desktop/lucas/Python%20Projects/traffic_optimization/randomTrips.py -n OSM_RandomTrips/keeleandmajmack.net.xml -r {trip_file} -e {max_steps} --random -s {seed} -o output/trips.trips.xml"
    randomTrips = r'"C:\Program Files (x86)\Eclipse\Sumo\tools\randomTrips.py"'
    cmd = f"python {randomTrips} -n {network_selection} -r {trip_file} -e {max_steps} --random -s {seed}"

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
