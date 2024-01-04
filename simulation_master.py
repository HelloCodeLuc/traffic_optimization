import sys
import os
import simulation_lib 
import traci
import random
import time
import shutil
import argparse
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

#TODO create the average idle time across all runs for a specific network timings
#TODO put an average line on graph
#TODO work to move to reference a temp network file with modified timing
network_selection = "mynetworks/3lights.net.xml"
light_names = ["left","middle","right"]
timing_light_increment = 1
num_runs = 1 
max_steps = 500  
num_networks = 3

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

def extract_lines_after_comment(filename, comment_pattern):
    result = []
    is_comment_section = False

    with open(filename, 'r') as file:
        for line in file:
            # Check if the comment pattern is present in the line
            if "LUCAS COMMENT" in line and comment_pattern in line:
                # Start extracting lines after the comment
                is_comment_section = True
                continue

            # Check if we are in the comment section
            if is_comment_section:
                # Append the line to the result
                result.append(line.rstrip('\n'))

                # Check if we have extracted 6 lines
                if len(result) == 6:
                    break

    return result

def create_target_netfile(previous_template, comment_pattern, target_net_file, modified_lines):
    is_comment_section = False
    with open(f'{target_net_file}.temp', 'w') as WFH:

        with open(previous_template, 'r') as file:
             for line in file:
                # Check if the comment pattern is present in the line
                if "LUCAS COMMENT" in line and comment_pattern in line:
                    WFH.write(line)
                    for _ in range(6):
                        next(file)
                    for i in range(6):
                        WFH.write(f'{modified_lines[i]}\n')
                else: 
                    WFH.write(line)  

    return

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
        lines_after_comment = extract_lines_after_comment(network_template, comment_pattern)
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

        create_target_netfile(network_template, comment_pattern, target_net_file, modified_lines)
        #sys.exit() 

    else:
        shutil.copy2(network_template, target_net_file)
        shutil.copy2(network_template, f'{target_net_file}.temp')
        
    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run SUMO simulation in batch or GUI mode.")
    parser.add_argument("--gui", action="store_true", help="Run with GUI")

    args = parser.parse_args()

    current_directory = os.getcwd()
    output_folder = "output"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_data_file = os.path.join(output_folder, "output_data.txt")
    parsed_string = network_selection.split("/")[-1]
    parsed_string_without_extension = parsed_string.rstrip(".net.xml")
    network_with_timing = os.path.join(output_folder, f"{parsed_string_without_extension}.timing.net.xml")

    for net_index in range(num_networks):
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

        print("Press space to continue...")
        while True:
            user_input = input()
            if user_input.lower() == ' ':
                break

    simulation_lib.my_plot(output_data_file)
    
sys.exit(0)
