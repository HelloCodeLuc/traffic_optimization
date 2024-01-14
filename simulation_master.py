import sys
import os
import simulation_lib 

import random
import time
import shutil
import argparse
#import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import re

#TODO create the average idle time across all runs for a specific network timings
#TODO put an average line on graph
#TODO work to move to reference a temp network file with modified timing
network_selection = "mynetworks/3lights.net.xml"
light_names = ["left","middle","right"]
timing_light_increment = 1
num_runs = 4
max_steps = 500  
num_of_runs_on_network = 3

def network_timings(network_template, target_net_file, light_names, timing_light_increment):
    #TODO find current timings of defined light
    #TODO modify based on defined choice
    #TODO insert back into file
    random_light = random.randint(0, len(light_names)-1)   
    random_direction = random.choice(["up", "down"])
    print (f"{light_names[random_light]} : {random_direction}")

    comment_pattern = f"{light_names[random_light]}"

    if os.path.exists(target_net_file):

        # Extract the next 6 lines after the comment
        lines_after_comment = simulation_lib.extract_lines_after_comment(network_template, comment_pattern)
        print("before:")
        for line in lines_after_comment:
            print(line)
        
        # Print the result
        modified_lines = []
        for line in lines_after_comment:
            #print(line)
            if 'state="GG' in line:
                #print("Found green")

                root = ET.fromstring(line)
                duration = int(root.get('duration'))
                new_duration = 0
                if random_direction == "up":
                    new_duration = f"{duration + timing_light_increment}"
                else:
                    new_duration = f"{duration - timing_light_increment}"

                #print (f"GREEN : from {duration} to {new_duration}")
                line = line.replace(str(duration), new_duration)
                # Print the modified string

            elif 'state="rrrGG' in line:
                #print("Found red")

                root = ET.fromstring(line)
                duration = int(root.get('duration'))
                new_duration = 0
                if random_direction == "up":
                    new_duration = f"{duration - timing_light_increment}"
                else:
                    new_duration = f"{duration + timing_light_increment}"

                #print (f"RED : from {duration} to {new_duration}")
                line = line.replace(str(duration), new_duration)
                # Print the modified string
            modified_lines.append(line)

        print("after:")
        for line in modified_lines:
            print(line)

        simulation_lib.create_target_netfile(network_template, comment_pattern, target_net_file, modified_lines)
    else:
        shutil.copy2(network_template, target_net_file)
        shutil.copy2(network_template, f'{target_net_file}.temp')
        
    return

def calculate_overall_average_for_given_network(output_data_file, network_averages):
    total = 0.0
    count = 0
    with open(output_data_file, "r") as FH:
        for line in FH:
            # Check if the comment pattern is present in the line
            if "Average Idle Time: " in line:
                print(f"line value:{line}")
                match = re.search(r'Average Idle Time\: (\d+\.\d+)', line)
                average_idle_time = float(match.group(1))
                count += 1
                #print(f"average_idle_time value:{average_idle_time}")
                total += average_idle_time

    average = total / count 

    prev_best = 0

    if os.path.exists(network_averages):
        with open(network_averages, 'r') as file:
            last_line = file.readlines()[-1].strip()
            match = re.search(r'(\d+\.\d+)', last_line)
            prev_best = float(match.group(1))
            print(last_line)   

    with open(network_averages, "a") as f:
        f.write(f"New overall average: {average}\n")

    if prev_best == 0 or average < prev_best:
        return 1 
    else:
        return 0
    


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run SUMO simulation in batch or GUI mode.")
    parser.add_argument("--gui", action="store_true", help="Run with GUI")

    args = parser.parse_args()

    current_directory = os.getcwd()
    output_folder = "output"

    if os.path.exists(output_folder):
        try:
            shutil.rmtree(output_folder)
        except OSError as e:
            print(f'Error removing directory {output_folder}: {e}')

    os.makedirs(output_folder)

    output_data_file = os.path.join(output_folder, "output_data.txt")
    network_averages = os.path.join(output_folder, "network_averages.txt")
    parsed_string = network_selection.split("/")[-1]
    parsed_string_without_extension = parsed_string.rstrip(".net.xml")
    network_with_timing = os.path.join(output_folder, f"{parsed_string_without_extension}.timing.net.xml")

    for net_index in range(num_of_runs_on_network):
        network_timings(network_selection, network_with_timing, light_names, timing_light_increment)

        for run in range(num_runs):
            random_seed = random.randint(1, 10000)  # Use a different random seed for each run
            trip_file = os.path.join(output_folder, f"random_trips_{random_seed}.xml")  # Generate a unique trip file name for each run
            print (f"DEBUG : trip_file = {trip_file}")
            # Generate random trips
            simulation_lib.generate_random_trips(f'{network_with_timing}.temp', trip_file, max_steps, random_seed)

            # Generate SUMO configuration file and update the route-files value
            config_file = os.path.join(output_folder, f"sumo_config_{random_seed}.sumocfg")
            simulation_lib.generate_sumo_config(f'{network_with_timing}.temp', config_file, current_directory, route_files=trip_file)

            # Run the SUMO simulation using the generated configuration file
            average_idle_time = simulation_lib.run_sumo(config_file, args.gui, int(max_steps))

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

        is_more_efficient = calculate_overall_average_for_given_network(output_data_file, network_averages)
        if(is_more_efficient):
            shutil.copy2(f'{network_with_timing}.temp', network_with_timing)
        
        os.remove(output_data_file)
        #simulation_lib.hit_space_to_continue()

    #simulation_lib.my_plot(output_data_file)


    
sys.exit(0)
