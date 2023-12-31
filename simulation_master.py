import sys
import os
import subprocess
import traci
import random
import time
import shutil
import argparse
import matplotlib.pyplot as plt
import argparse

network_selection = "mynetworks/3lights.net.xml"
num_runs = 1 
max_steps = 500  

# Run randomtrips.py to generate random trips and save them to a file
def generate_random_trips(network_selection, trip_file, max_steps, seed):
    #cmd = f"C:/Users/chuny/Desktop/lucas/Python%20Projects/traffic_optimization/randomTrips.py -n OSM_RandomTrips/keeleandmajmack.net.xml -r {trip_file} -e {max_steps} --random -s {seed} -o output/trips.trips.xml"
    randomTrips = r'"C:\Program Files (x86)\Eclipse\Sumo\tools\randomTrips.py"'
    cmd = f"python {randomTrips} -n {network_selection} -r {trip_file} -e {max_steps} --random -s {seed}"

    print (f"DEBUG 1 : randomTrips.py command : {cmd}")
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

    with open(config_file, 'w') as f:
        f.write(config_template)

def run_sumo(config_file, gui_opt):
    # Launch SUMO with GUI using the generated configuration file
    sumo_cmd = ["sumo", "-c", config_file]
    if gui_opt:
        sumo_cmd = ["sumo-gui", "-c", config_file] 

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
    print("Average Idle Time:", average_idle_time )
    return average_idle_time

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
    plt.legend(loc='lower right')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SUMO simulation in batch or GUI mode.")
    parser.add_argument("--gui", action="store_true", help="Run with GUI")

    args = parser.parse_args()

    current_directory = os.getcwd()
    output_folder = "output"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_data_file = os.path.join(output_folder, "output_data.txt")

    for run in range(num_runs):
        random_seed = random.randint(1, 10000)  # Use a different random seed for each run
        trip_file = os.path.join(output_folder, f"random_trips_{random_seed}.xml")  # Generate a unique trip file name for each run
        print (f"DEBUG : trip_file = {trip_file}")
        # Generate random trips
        generate_random_trips(network_selection, trip_file, max_steps, random_seed)

        # Generate SUMO configuration file and update the route-files value
        config_file = os.path.join(output_folder, f"sumo_config_{random_seed}.sumocfg")
        generate_sumo_config(network_selection, config_file, current_directory, route_files=trip_file)

        # Run the SUMO simulation using the generated configuration file
        average_idle_time = run_sumo(config_file,args.gui)

        # Write the iteration number to the output_data file
        with open(output_data_file, "a") as f:
            f.write(f"Random Seed: {random_seed},")
            f.write(f"Trip File: {trip_file},")
            f.write(f"Configuration File: {config_file},")
            f.write(f"Average Idle Time: {average_idle_time}\n")
        # Clean up generated files
        print (f"DEBUG : trip_file = {trip_file}")

        os.remove(trip_file)
        os.remove(config_file)

    my_plot(output_data_file)
sys.exit(0)
