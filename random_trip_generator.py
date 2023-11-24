import sys
import os
import subprocess
import traci
import random
import time
import shutil
import argparse

def generate_random_trips(trip_file, max_steps, seed):
    # Run randomtrips.py to generate random trips and save them to a file
    print ("DEBUG 0")
    #cmd = f"C:/Users/chuny/Desktop/lucas/Python%20Projects/traffic_optimization/randomTrips.py -n OSM_RandomTrips/keeleandmajmack.net.xml -r {trip_file} -e {max_steps} --random -s {seed} -o output/trips.trips.xml"
    randomTrips = r'"C:\Program Files (x86)\Eclipse\Sumo\tools\randomTrips.py"'
    cmd = f"python {randomTrips} -n OSM_RandomTrips/keeleandmajmack.net.xml -r {trip_file} -e {max_steps} --random -s {seed}"

    print (f"DEBUG 1 : randomTrips.py command : {cmd}")
    subprocess.call(cmd, shell=True)
    print ("DEBUG 2")

def generate_sumo_config(config_file, current_directory, route_files):
    # Generate the SUMO configuration file with the given template
    config_template = f"""<configuration>
    <input>
        <net-file value="{current_directory}/OSM_RandomTrips/keeleandmajmack.net.xml"/>
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
 
    traci.start(sumo_cmd)

    step = 0
    while step < max_steps:
        traci.simulationStep()
        step += 1
        time.sleep(0.1)

    traci.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run SUMO simulation in batch or GUI mode.")
    parser.add_argument("--gui", action="store_true", help="Run with GUI")

    args = parser.parse_args()




    current_directory = os.getcwd()
    output_folder = "output"

    if os.path.exists(output_folder):
        try:
           # Use shutil.rmtree() to remove the directory and its contents
           shutil.rmtree(output_folder)
           print(f'Deleted directory: {output_folder}')
        except Exception as e:
           print(f"Error: {e}")
    else:
        print(f"Directory '{output_folder}' does not exist.")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    num_runs = 10  # Change this to the number of times you want to run the simulation
    max_steps = 20
    #max_steps = 2000  # Change this to the desired number of simulation steps

    output_data_file = os.path.join(output_folder, "output_data.txt")

    for run in range(num_runs):
        random_seed = random.randint(1, 10000)  # Use a different random seed for each run
        trip_file = os.path.join(output_folder, f"random_trips_{random_seed}.xml")  # Generate a unique trip file name for each run
        print (f"DEBUG : trip_file = {trip_file}")
        # Generate random trips
        generate_random_trips(trip_file, max_steps, random_seed)
        print ("DEBUG 3")
        #sys.exit(0)
        # Generate SUMO configuration file and update the route-files value
        config_file = os.path.join(output_folder, f"sumo_config_{random_seed}.sumocfg")
        generate_sumo_config(config_file, current_directory, route_files=trip_file)
        # Set working directory to the output folder for the SUMO simulation
        #os.chdir(output_folder)

        # Run the SUMO simulation using the generated configuration file
        run_sumo(config_file, args.gui)

         # Write the iteration number to the output_data file
        with open(output_data_file, "a") as f:
            f.write(f"Iteration: {run},")
            f.write(f"Random Seed: {random_seed},")
            f.write(f"Trip File: {trip_file},")
            f.write(f"Configuration File: {config_file}\n")
        # Clean up generated files
        print (f"DEBUG : trip_file = {trip_file}")
        # sys.exit(0)

        os.remove(trip_file)
        os.remove(config_file)

