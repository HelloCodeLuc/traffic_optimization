import sys
import simulation_lib as simulation_lib 
import os
import shutil
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_COMMON_LIB'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_OPTIMIZATION'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'CONTROL_GUI'))
import basic_utilities
import optimize_timing_lib
import gui_main
import Bluetooth_map
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
num_batches = 1
num_runs_per_batch = 2
max_steps = 2000
num_of_runs_on_network = 1000
num_of_greenlight_duplicate_limit = 40
average_speed_n_steps = 20
# Example usage:
date = f"{basic_utilities.get_current_datetime()}"
output_folder = f"out/{date}"

def main_loop(num_batches, num_runs_per_batch, network_selection, max_steps, output_folder):

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

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        os.makedirs(f"{output_folder}/TRAIN_OPTIMIZATION")
        os.makedirs(f"{output_folder}/TRAIN_BLUETOOTH")

        optimize_timing_lib.optimize_timing_main (output_folder, output_data_file, num_of_runs_on_network, num_batches, num_runs_per_batch, network_selection, 
                                                max_steps, network_with_timing, light_names, timing_light_increment, network_averages, 
                                                num_of_greenlight_duplicate_limit, average_speed_n_steps, debug)



if __name__ == "__main__":

    # Create a list to store the processes and results
    processes = []

    process = Process(target=main_loop, args=(num_batches, num_runs_per_batch, network_selection, max_steps, output_folder))
    processes.append(process)
    process = Process(target=gui_main.gui_main, args=(output_folder,))
    processes.append(process)
    for process in processes:
        process.start()
   
    # Wait for all processes to finish (optional)
    for process in processes:
        process.join()
