import sys
import os
import simulation_lib 
import random
import shutil
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_COMMON_LIB'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_OPTIMIZATION'))
import basic_utilities
import optimize_timing_lib
from multiprocessing import Process, Queue
#TODO put an average line on graph

network_sel = 3
network_selection = ""
light_names = []
if (network_sel == 0):
    network_selection = "NETWORKS/3lights.net.xml"
    light_names = ["left","middle","right"]
elif (network_sel == 1):
    network_selection = "NETWORKS/school.net.xml"
    light_names = ["mcnaughton_keele","barhill_rutherford","ivy_dufferin","keele_barhill","keele_rutherford","mackenzie_dufferin","mackenzie_peter","maurier_dufferin","peter_rutherford","rutherford_dufferin"]
elif (network_sel == 2):
    network_selection = "NETWORKS/school.timing.net.xml"
    light_names = ["mcnaughton_keele","barhill_rutherford","ivy_dufferin","keele_barhill","keele_rutherford","mackenzie_dufferin","mackenzie_peter","maurier_dufferin","peter_rutherford","rutherford_dufferin"]
elif (network_sel == 3):
    network_selection = "NETWORKS/school-extended.net.xml"
    light_names = ["mcnaughton_keele","barhill_rutherford","ivy_dufferin","keele_barhill","keele_rutherford","mackenzie_dufferin","mackenzie_peter","maurier_dufferin","peter_rutherford","rutherford_dufferin"]
elif (network_sel == 4):
    network_selection = "NETWORKS/weight_test.net.xml"
    light_names = ["main"]

timing_light_increment = 2
num_batches = 5
num_runs_per_batch = 10
max_steps = 2000
num_of_runs_on_network = 1000
num_of_greenlight_duplicate_limit = 40
# Example usage:
date = basic_utilities.get_current_datetime()

output_folder = f"out/{date}"
output_data_file = os.path.join(output_folder, "TRAIN_OPTIMIZATION/output_data.txt")
network_averages = os.path.join(output_folder, "TRAIN_OPTIMIZATION/network_averages.txt")
parsed_string = network_selection.split("/")[-1]
parsed_string_without_extension = parsed_string.replace(".net.xml", "")
network_with_timing = os.path.join(output_folder, f"TRAIN_OPTIMIZATION/{parsed_string_without_extension}.timing.net.xml")

debug = 0
if (debug == 1):
    num_batches = 1
    num_runs_per_batch = 1
    debug_seed = 3920
    max_steps = 10000

if (0):    
    simulation_lib.my_plot(network_averages)
    sys.exit()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run SUMO simulation in batch or GUI mode.")
    parser.add_argument("--gui", action="store_true", help="Run with GUI")
 
    args = parser.parse_args()
    
    if (debug == 1):
        args.gui = True

    current_directory = os.getcwd()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        os.makedirs(f"{output_folder}/TRAIN_OPTIMIZATION")
        os.makedirs(f"{output_folder}/TRAIN_BLUETOOTH")
        
    previous_greenlight_timings_file = os.path.join(output_folder, "TRAIN_OPTIMIZATION/previous_greenlight_timings.txt")
    print(f"previous_greenlight_timings = {previous_greenlight_timings_file}\n")
    previous_greenlight_timings = {}
    if os.path.exists(previous_greenlight_timings_file):
        with open(previous_greenlight_timings_file, 'r') as file:
            for line in file:
                line = line.strip()
                previous_greenlight_timings[line] = 1
        file.close()

    core_count = simulation_lib.return_num_of_cores()
    print(f"Number of CPU cores: {core_count}\n")

    for net_index in range(num_of_runs_on_network):
        greenlight_timings = ""
        if (debug == 0):
            greenlight_timings = optimize_timing_lib.network_timings(network_selection, network_with_timing, light_names, timing_light_increment, previous_greenlight_timings, previous_greenlight_timings_file, network_averages, num_of_greenlight_duplicate_limit)

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

                trip_file = os.path.join(f"{output_folder}\TRAIN_OPTIMIZATION", f"random_trips_{random_seed}.xml")  # Generate a unique trip file name for each run
                # Generate random trips
                simulation_lib.generate_random_trips(f'{network_with_timing}.temp', trip_file, max_steps, random_seed)

                # Generate SUMO configuration file and update the route-files value
                config_file = os.path.join(f"{output_folder}\TRAIN_OPTIMIZATION", f"sumo_config_{random_seed}.sumocfg")
                simulation_lib.generate_sumo_config(f'{network_with_timing}.temp', config_file, current_directory, route_files=trip_file)
                
                random_seeds.append(random_seed)
                trip_files.append(trip_file)
                config_files.append(config_file)

            # Create a queue to store the results
            result_queue = Queue()

            # Run the SUMO simulation using the generated configuration file
            # average_idle_time = simulation_lib.run_sumo(config_file, args.gui, int(max_steps))
            processes = []
            average_idle_times_from_batch = []

            # Launch each simulation in a separate process
            for config in config_files:
                process = Process(target=simulation_lib.run_sumo, args=(config, args.gui, int(max_steps), result_queue))
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


        is_more_efficient = optimize_timing_lib.calculate_overall_average_for_given_network(output_data_file, network_averages, greenlight_timings)
        if(is_more_efficient == "keep"):
            shutil.copy2(f'{network_with_timing}.temp', network_with_timing)
        
        os.remove(output_data_file)
        #simulation_lib.hit_space_to_continue()





