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
from multiprocessing import Process, Queue

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
    "simple_network/simple_network.net.xml": ["main_1", "main_2"]
    }

gui_colour = "blue"
timing_light_increment = 2
num_batches = 1
num_runs_per_batch = 6
max_steps = 2000
max_num_of_runs_on_network = 1000
num_of_greenlight_duplicate_limit = 40
average_speed_n_steps = 20
start_command = "RUN"
stop_command = "STOP"
phase = "start"
weight_prefix = "weights"
weight_change = 1
weight_accuracy = 5

def main_loop(num_batches, num_runs_per_batch, network_selection, max_steps, phase, output_folder):

    while True:
        command = optimize_timing_lib.read_commands("out/command_queue.txt")
        if command is not None:
            if "NETWORK_CHANGE" in command:
                network_name = command.split(":")[1].strip()
                network_selection = f"NETWORKS/{network_name}"
                light_names = light_name_data[network_name]
                print(network_name)
                print(light_names)
            # elif command == "DEMO":
            #     if os.path.exists(f"{output_folder}/TRAIN_OPTIMIZATION"):
            #         print ("DEMO_TRAIN_OPTIMIZATION")
            #         basic_utilities.demo_gui(f"{output_folder}/TRAIN_OPTIMIZATION")
            #     elif os.path.exists(f"{output_folder}/TRAIN_BLUETOOTH"):
            #         print ("DEMO_TRAIN_BLUETOOTH")
            #         basic_utilities.demo_gui(f"{output_folder}/TRAIN_BLUETOOTH")
            elif command == start_command:

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
                                                num_of_greenlight_duplicate_limit, average_speed_n_steps, weight_prefix, weight_change, weight_accuracy)

                # sys.exit()
                os.makedirs(f"{output_folder}/TRAIN_OPTIMIZATION")
                phase = "optimize"
                shutil.copy2 (f'{output_folder}/TRAIN_BLUETOOTH/GUI_average_speeds.csv' , f'{output_folder}/TRAIN_OPTIMIZATION/GUI_average_speeds.start.csv')
                output_data_file = os.path.join(output_folder, "TRAIN_OPTIMIZATION/output_data.txt")
                network_averages = os.path.join(output_folder, "TRAIN_OPTIMIZATION/network_averages.txt")
                network_with_timing = os.path.join(output_folder, f"TRAIN_OPTIMIZATION/{parsed_string_without_extension}.timing.net.xml")

                optimize_timing_lib.optimize_timing_main (phase, output_folder, output_data_file, max_num_of_runs_on_network, num_batches, num_runs_per_batch, network_selection, 
                                                max_steps, network_with_timing, light_names, timing_light_increment, network_averages, 
                                                num_of_greenlight_duplicate_limit, average_speed_n_steps)
                command = "STOP"


if __name__ == "__main__":

    #if not os.path.exists("out"):
    #    os.makedirs("out")

    date = f"{basic_utilities.get_current_datetime()}"
    output_folder = f"out/{date}"

    # Create a list to store the processes and results
    processes = []

    process = Process(target=gui_main.gui_main, args=(gui_colour, output_folder))
    processes.append(process)
    process = Process(target=main_loop, args=(num_batches, num_runs_per_batch, network_selection, max_steps, phase, output_folder))
    processes.append(process)
    for process in processes:
        process.start()
   
    # Wait for all processes to finish (optional)
    for process in processes:
        process.join()
