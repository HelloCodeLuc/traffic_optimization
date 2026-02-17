import sys
import os
import shutil
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_COMMON_LIB'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_OPTIMIZATION'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'CONTROL_GUI'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_BLUETOOTH'))
import bluetooth_lib
import basic_utilities
import optimize_timing_lib
import gui_main
import json
from multiprocessing import Process, Queue
from datetime import datetime

#TODO put an average line on graph

network_selection = ""
light_names = []

light_name_data = {
    "3lights/3lights.net.xml": ["left", "middle", "right"],
    "city_timing/city_timing.net.xml": ["mcnaughton_keele", "barhill_rutherford", "ivy_dufferin",
            "keele_barhill", "keele_rutherford", "mackenzie_dufferin",
            "mackenzie_peter", "maurier_dufferin", "peter_rutherford",
            "rutherford_dufferin"],
    "school_extended/school_extended.net.xml": ["mcnaughton_keele", "barhill_rutherford", "ivy_dufferin",
            "keele_barhill", "keele_rutherford", "mackenzie_dufferin",
            "mackenzie_peter", "maurier_dufferin", "peter_rutherford",
            "rutherford_dufferin"],
    "school/school.net.xml": ["mcnaughton_keele", "barhill_rutherford", "ivy_dufferin",
            "keele_barhill", "keele_rutherford", "mackenzie_dufferin",
            "mackenzie_peter", "maurier_dufferin", "peter_rutherford",
            "rutherford_dufferin"],
    "weight_test/weight_test.net.xml": ["main"],
    "simple_network/simple_network.net.xml": ["main1", "main2"],
    "simple_network_actuated/simple_network_actuated.net.xml": ["main1", "main2"],
    "Hwy7_404_network/Hwy7_404_network.net.xml": ["bayview_and_hwy7", "bayview_and_briggs", "bayview_and_blackmore", "bayview_and_16th", "hwy7_and_valleymede", "hwy7_and_saddlecreek", "hwy7_and_chalmers", "spadina_and_16th", "leslie_and_pearce", "leslie_and_wilmot", "leslie_and_beaver_creek", "leslie_and_16th", "leslie_and_commerce_valley", "leslie_and_minthorn", "leslie_and_hwy7", "hwy7_and_east_beaver_creek", "hwy7_and_bayview"]
    }

gui_colour = "blue"
timing_light_increment = 4
num_batches = 1
num_runs_per_batch = 2
max_steps = 1100
max_num_of_runs_on_network = 1000
num_of_greenlight_duplicate_limit = 200
average_speed_n_steps = 1100
start_command = "RUN"
stop_command = "STOP"
phase = "start"
weight_prefix = "weights"
weight_change = 0.1
weight_accuracy = 100
max_weight = 100

def main_loop(num_batches, num_runs_per_batch, network_selection, max_steps, phase, output_folder, restart):

    while True:
        command = optimize_timing_lib.read_commands("out/command_queue.txt")
        if command is not None:
            if "NETWORK_CHANGE" in command:
                network_name = command.split(":")[1].strip()
                network_prefix = os.path.dirname(network_name)  
                network_selection = f"NETWORKS/{network_name}"
                light_names = light_name_data[network_name]
                print(f"Network name: {network_name}")
                print(light_names)
                
                # Read the JSON file  
                with open(f"NETWORKS/{network_prefix}/{network_prefix}.cfg.json", 'r') as file:  
                    data = json.load(file)  
                
                # Assign values to variables  
                weight_accuracy = data.get('weight_accuracy', 4)  # Defaults to 4 if not set                  
                # Print the assigned values  
                print(f"Weight Accuracy: {weight_accuracy}")  


            elif command == "RESTART":
                parsed_string_without_extension = ""
                last_run_restart = True
                last_run_dir = basic_utilities.last_run_folder("out")
                last_run_network = basic_utilities.last_run_network(f"out/{last_run_dir}/TRAIN_OPTIMIZATION", ".timing.net.xml")
                if last_run_network == None:
                    last_run_network = basic_utilities.last_run_network(f"out/{last_run_dir}/TRAIN_BLUETOOTH", ".timing.net.xml")
                if (restart == 0):
                    if not os.path.exists(output_folder):
                        os.makedirs(output_folder)
                        os.makedirs(f"{output_folder}/TRAIN_BLUETOOTH")

                    # Input and output file paths
                    csv_file_edges = f'{output_folder}/GUI_edges.csv'
                    csv_file_junctions = f'{output_folder}/GUI_junction_coordinates.csv'
                    # Run the function
                    basic_utilities.extract_network_edges(network_selection, csv_file_edges)
                    basic_utilities.extract_network_junctions(network_selection, csv_file_junctions)

                    output_data_file = os.path.join(output_folder, "TRAIN_BLUETOOTH/output_data.txt")
                    parsed_string = network_selection.split("/")[-1]
                    parsed_string_without_extension = parsed_string.replace(".net.xml", "")
                    bluetooth_network_with_timing = os.path.join(output_folder, f"TRAIN_BLUETOOTH/{parsed_string_without_extension}.timing.net.xml")
                    phase = "bluetooth"
                    bluetooth_lib.bluetooth_training(phase, bluetooth_network_with_timing, output_folder, output_data_file, max_num_of_runs_on_network, num_batches, num_runs_per_batch, network_selection, 
                                                    max_steps, bluetooth_network_with_timing, light_names, timing_light_increment,  
                                                    num_of_greenlight_duplicate_limit, average_speed_n_steps, weight_prefix, weight_change, weight_accuracy, max_weight, last_run_restart, last_run_dir, last_run_network)

                    # sys.exit()
                    os.makedirs(f"{output_folder}/TRAIN_OPTIMIZATION")
                    shutil.copy2 (f'{output_folder}/TRAIN_BLUETOOTH/GUI_average_speeds.csv' , f'{output_folder}/TRAIN_OPTIMIZATION/GUI_average_speeds.start.csv')
                else: 
                    parsed_string_without_extension = basic_utilities.find_timing_file_prefix(output_folder)

                phase = "optimize"
                output_data_file = os.path.join(output_folder, "TRAIN_OPTIMIZATION/output_data.txt")
                network_averages = os.path.join(output_folder, "TRAIN_OPTIMIZATION/network_averages.txt")
                network_with_timing = os.path.join(output_folder, f"TRAIN_OPTIMIZATION/{parsed_string_without_extension}.timing.net.xml")

                optimize_timing_lib.optimize_timing_main (phase, output_folder, output_data_file, max_num_of_runs_on_network, num_batches, num_runs_per_batch, network_selection, 
                                                max_steps, network_with_timing, light_names, timing_light_increment, network_averages, 
                                                num_of_greenlight_duplicate_limit, average_speed_n_steps, restart)
                command = "STOP"


            elif command == start_command:
                parsed_string_without_extension = ""
                last_run_restart = False
                if (restart == 0):
                    if not os.path.exists(output_folder):
                        os.makedirs(output_folder)
                        os.makedirs(f"{output_folder}/TRAIN_BLUETOOTH")
                    if os.path.exists(f"NETWORKS/{network_prefix}/detectors.add.xml"):
                        os.makedirs("out/detectors")
                        shutil.copy2(f"NETWORKS/{network_prefix}/detectors.add.xml", f"out/detectors/detectors.add.xml")

                    # Input and output file paths
                    csv_file_edges = f'{output_folder}/GUI_edges.csv'
                    csv_file_junctions = f'{output_folder}/GUI_junction_coordinates.csv'
                    # Run the function
                    basic_utilities.extract_network_edges(network_selection, csv_file_edges)
                    basic_utilities.extract_network_junctions(network_selection, csv_file_junctions)

                    output_data_file = os.path.join(output_folder, "TRAIN_BLUETOOTH/output_data.txt")
                    parsed_string = network_selection.split("/")[-1]
                    parsed_string_without_extension = parsed_string.replace(".net.xml", "")
                    bluetooth_network_with_timing = os.path.join(output_folder, f"TRAIN_BLUETOOTH/{parsed_string_without_extension}.timing.net.xml")
                    phase = "bluetooth"
                    bluetooth_lib.bluetooth_training(phase, bluetooth_network_with_timing, output_folder, output_data_file, max_num_of_runs_on_network, num_batches, num_runs_per_batch, network_selection, 
                                                    max_steps, bluetooth_network_with_timing, light_names, timing_light_increment,  
                                                    num_of_greenlight_duplicate_limit, average_speed_n_steps, weight_prefix, weight_change, weight_accuracy, max_weight, last_run_restart)

                    # sys.exit()
                    os.makedirs(f"{output_folder}/TRAIN_OPTIMIZATION")
                    shutil.copy2 (f'{output_folder}/TRAIN_BLUETOOTH/GUI_average_speeds.csv' , f'{output_folder}/TRAIN_OPTIMIZATION/GUI_average_speeds.start.csv')
                else: 
                    parsed_string_without_extension = basic_utilities.find_timing_file_prefix(output_folder)

                phase = "optimize"
                output_data_file = os.path.join(output_folder, "TRAIN_OPTIMIZATION/output_data.txt")
                network_averages = os.path.join(output_folder, "TRAIN_OPTIMIZATION/network_averages.txt")
                network_with_timing = os.path.join(output_folder, f"TRAIN_OPTIMIZATION/{parsed_string_without_extension}.timing.net.xml")

                optimize_timing_lib.optimize_timing_main (phase, output_folder, output_data_file, max_num_of_runs_on_network, num_batches, num_runs_per_batch, network_selection, 
                                                max_steps, network_with_timing, light_names, timing_light_increment, network_averages, 
                                                num_of_greenlight_duplicate_limit, average_speed_n_steps, restart)
                command = "STOP"


if __name__ == "__main__":

    restart = 0

    if not os.path.exists("out"):
       os.makedirs("out")

    if (restart == 1):
        latest = basic_utilities.get_latest_output_directory()    
        output_folder = latest
    else:
        date = f"{basic_utilities.get_current_datetime()}"
        output_folder = f"out/{date}"

    print("output folder:", output_folder)
    # Create a list to store the processes and results
    processes = []

    process = Process(target=gui_main.gui_main, args=(gui_colour, max_steps, output_folder, num_batches, num_runs_per_batch, restart))
    processes.append(process)
    process = Process(target=main_loop, args=(num_batches, num_runs_per_batch, network_selection, max_steps, phase, output_folder, restart))
    processes.append(process)
    for process in processes:
        process.start()
   
    # Wait for all processes to finish (optional)
    for process in processes:
        process.join()
