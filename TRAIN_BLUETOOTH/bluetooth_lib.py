"""
loop
    If not first bluetooth run
        Compare weights to bluetooth reference and identify largest delta
        Make change to simulated network to better align with the bluetooth reference
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
sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_COMMON_LIB'))
import basic_utilities

def create_ref_at_start(phase, num_batches, num_runs_per_batch, output_folder, bluetooth_network_with_timing, max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, debug):
    basic_utilities.batched_run_sumo(phase, num_batches, num_runs_per_batch, output_folder, bluetooth_network_with_timing, max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, debug)

def bluetooth_training(phase, output_folder, network_selection, bluetooth_network_with_timing, num_batches, num_runs_per_batch, max_steps, average_speed_n_steps, output_data_file):
    print(">> In Bluetooth_Training")
    print(f"Network File: {network_selection}, Output Directory: {output_folder}")
    print(f"Bluetooth Network File: {bluetooth_network_with_timing}")
    debug = 0
    current_directory = os.getcwd()
    speed_limit = basic_utilities.extract_speeds_from_edges(network_selection)

    if os.path.exists(bluetooth_network_with_timing):
        print("Bluetooth Network Exists")
    else:
        shutil.copy2(network_selection, bluetooth_network_with_timing)
        shutil.copy2(network_selection, f"{bluetooth_network_with_timing}.temp")

    create_ref_at_start(phase, num_batches, num_runs_per_batch, output_folder, bluetooth_network_with_timing, max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, debug)
    
    #sys.exit()

    while True:
        if basic_utilities.check_queue_has_command("STOP", "out/command_queue.txt", 1): 
            print(">> Execution interrupted (BLUETOOTH)")
            sys.exit()
        print(">> Exit Bluetooth_Training")
        time.sleep(5)
        break