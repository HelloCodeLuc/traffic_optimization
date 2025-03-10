"""
loop
    If not first bluetooth run
        Compare weights to bluetooth reference and identify largest delta
        Make randomized change to the edge with highest delta through the weight file to better align with the bluetooth reference
        if average_speed_difference < average_speed_difference_last
            
    Else
        Bring reference city network and timing into bluetooth run area
    
    Simulated Network

    If not first bluetooth run
        If simulated network is closer to bluetooth, keep new   
    else
        keep start reference and deposit network in preperation for next simulation
"""
import sys
import os
import time
import shutil
import csv
# sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_OPTIMIZATION'))
# import optimize_timing_lib
sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_COMMON_LIB'))
import basic_utilities



def bluetooth_create_ref_at_start(phase, num_batches, num_runs_per_batch, output_folder, bluetooth_network_with_timing, 
                                     max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, output_folder_subdir, network_selection, debug):
    basic_utilities.batched_run_sumo(phase, num_batches, num_runs_per_batch, output_folder, bluetooth_network_with_timing, 
                                     max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, network_selection, debug)
    shutil.copy(f"{output_folder}/{output_folder_subdir}/GUI_average_speeds.csv", f"{output_folder}/{output_folder_subdir}/GUI_average_speeds.start.csv")

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

def bluetooth_training(phase, bluetooth_network_with_timing, output_folder, output_data_file, num_of_runs_on_network, num_batches, num_runs_per_batch, network_selection, 
                                                max_steps, network_with_timing, light_names, timing_light_increment, 
                                                num_of_greenlight_duplicate_limit, average_speed_n_steps):
    output_folder_subdir = "TRAIN_BLUETOOTH"

    print(">> In Bluetooth_Training")
    print(f"Network File: {network_selection}, Output Directory: {output_folder}")
    print(f"Bluetooth Network File: {bluetooth_network_with_timing}")
    
    bluetooth_csv = os.path.splitext(os.path.splitext(network_selection)[0])[0] + ".bluetooth.csv"
    # bluetooth_csv = f"NETWORKS/{filename}.bluetooth.csv"
    print(f"Bluetooth CSV File: {bluetooth_csv}")

    debug = 0
    current_directory = os.getcwd()
    speed_limit = basic_utilities.extract_speeds_from_edges(network_selection)

    if os.path.exists(bluetooth_network_with_timing):
        print("Bluetooth Network Exists")
    else:
        shutil.copy2(network_selection, bluetooth_network_with_timing)
        shutil.copy2(network_selection, f"{bluetooth_network_with_timing}.temp")

    bluetooth_create_ref_at_start(phase, num_batches, num_runs_per_batch, output_folder, bluetooth_network_with_timing, 
                                     max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, output_folder_subdir, network_selection, debug)
    # optimize_timing_lib.optimize_timing_main(phase, output_folder, output_data_file, num_of_runs_on_network, num_batches, num_runs_per_batch, network_selection, 
    #                                             max_steps, network_with_timing, light_names, timing_light_increment, network_averages, 
    #                                             num_of_greenlight_duplicate_limit, average_speed_n_steps)

    while True:
        #This is a backdoor for user to initiate stop from GUI
        if basic_utilities.check_queue_has_command("STOP", "out/command_queue.txt", 1): 
            print(">> Execution interrupted (BLUETOOTH)")
        if os.path.exists(bluetooth_csv):
            average_diff, max_discrepancy_edge, max_discrepancy_value = basic_utilities.calculate_average_difference(bluetooth_csv, f"{output_folder}/{output_folder_subdir}/GUI_average_speeds.csv")
            print(f"The average speed difference is: {average_diff:.3f} km/h")
            print(f"The largest discrepancy is on Edge ID '{max_discrepancy_edge}' with a difference of {max_discrepancy_value} km/h")
            print(">> Exit Bluetooth_Training")
        time.sleep(5)
        # sys.exit()
        break