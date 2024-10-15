import simulation_lib
import sys
import os
import shutil
import re
import xml.etree.ElementTree as ET
# find current timings of defined light
# modify based on defined choice
# insert back into file
def network_timings(network_template, target_net_file, light_names, timing_light_increment, previous_greenlight_timings, previous_greenlight_timings_file, network_averages, num_of_greenlight_duplicate_limit):

    if os.path.exists(target_net_file):
        
        new_greenlight_timings_unique = False
        num_of_greenlight_duplicates = 0

        while not new_greenlight_timings_unique:
            random_light = random.randint(0, len(light_names)-1)   
            random_action = random.choice(["green_up", "green_down", 
                                           "green_up", "green_down",
                                           "green_up", "green_down",
                                           "green_up", "green_down",
                                           "green_up", "green_down",
                                           "offset_pos", "offset_neg"])

            print (f"Light:{light_names[random_light]} : Action:{random_action}")
            comment_pattern = f"{light_names[random_light]}"
            # Extract the next 6 lines after the comment
            lines_after_comment = simulation_lib.extract_lines_after_comment(target_net_file, comment_pattern)
            print("before:")
            for line in lines_after_comment:
                print(line)

            # Print the result
            modified_lines = []
            for line in lines_after_comment:
                #print(line)
                if random_action == "green_up" or random_action == "green_down":
                    if 'name="green"' in line:
                        #print("Found green"){

                        root = ET.fromstring(line)
                        duration = int(root.get('duration'))
                        new_duration = 0
                        if random_action == "green_up":
                            new_duration = f"{duration + timing_light_increment}"
                        else:
                            new_duration = f"{duration - timing_light_increment}"

                        #print (f"GREEN : from {duration} to {new_duration}")
                        line = line.replace(str(duration), new_duration)
                        # Print the modified string}

                    elif 'name="red"' in line:
                        #print("Found red")

                        root = ET.fromstring(line)
                        duration = int(root.get('duration'))
                        new_duration = 0
                        if random_action == "green_up":
                            new_duration = f"{duration - timing_light_increment}"
                        else:
                            new_duration = f"{duration + timing_light_increment}"

                        line = line.replace(str(duration), new_duration)
                        # Print the modified string
                elif "offset" in random_action:
                    if 'offset' in line:
                        offset_match = re.search(r'offset="(-?\d+)"', line)
                        offset = 0
                        if offset_match:
                            offset = int(offset_match.group(1))
                        new_offset = 0
                        if random_action == "offset_pos":
                            new_offset = f"{offset + timing_light_increment}"
                        else:
                            new_offset = f"{offset - timing_light_increment}"

                        line = line.replace(f"offset=\"{offset}\"", f"offset=\"{new_offset}\"")
                        # Print the modified string
                modified_lines.append(line)

            print("after:")
            for line in modified_lines:
                print(line)

            simulation_lib.create_target_net_xml_temp(comment_pattern, target_net_file, modified_lines)

            # review the 'state="GG' lines, if not already in hash prev green light setups, continue, else loop back to redo to create timings again.  Maybe also make this green light set a return value and prefix it into each line of network_averages.txt file.
            # maybe when we loop back. put a note in the network_averages.txt that we hit a previous run case.
            green_light_and_offset_timings = ""
            with open(f'{target_net_file}.temp', 'r') as file:
                for line in file:
                    if 'name="green' in line:
                        root = ET.fromstring(line)
                        duration = int(root.get('duration'))
                        if green_light_and_offset_timings == "":
                            green_light_and_offset_timings = f"{duration}"
                        else:
                            green_light_and_offset_timings = (f"{green_light_and_offset_timings}:{duration}")
                    elif "offset=" in line:
                        offset_match = re.search(r'offset="(-?\d+)"', line)
                        offset = 0
                        if offset_match:
                            offset = int(offset_match.group(1))
                        if green_light_and_offset_timings == "":
                            green_light_and_offset_timings = f"{offset}"
                        else:
                            green_light_and_offset_timings = (f"{green_light_and_offset_timings}:{offset}")

            file.close()
            print(f"DEBUG : green_light_timings = {green_light_and_offset_timings}\n")
            with open(previous_greenlight_timings_file, "a") as f:
                f.write(f"{green_light_and_offset_timings}\n")
            f.close()

            if green_light_and_offset_timings not in previous_greenlight_timings:
                previous_greenlight_timings[green_light_and_offset_timings] = 1
                new_greenlight_timings_unique = True
            else:
                with open(network_averages, "a") as f:
                    f.write(f"Duplicate New Green Light Timing: {green_light_and_offset_timings}\n")
                    num_of_greenlight_duplicates += 1
                    if num_of_greenlight_duplicates == num_of_greenlight_duplicate_limit:
                        f.write(f"Max number of duplicates of {num_of_greenlight_duplicate_limit} reached, exiting script.\n")
                        sys.exit(0)
                f.close()
                        
    else:
        shutil.copy2(network_template, target_net_file)
        shutil.copy2(network_template, f'{target_net_file}.temp')

        green_light_and_offset_timings = ""
        with open(f'{target_net_file}.temp', 'r') as file:
            for line in file:
                if 'name="green' in line:
                    root = ET.fromstring(line)
                    duration = int(root.get('duration'))
                    if green_light_and_offset_timings == "":
                        green_light_and_offset_timings = f"{duration}"
                    else:
                        green_light_and_offset_timings = (f"{green_light_and_offset_timings}:{duration}")
                elif "offset=" in line:
                    offset_match = re.search(r'offset="(-?\d+)"', line)
                    offset = 0
                    if offset_match:
                        offset = int(offset_match.group(1))
                    if green_light_and_offset_timings == "":
                        green_light_and_offset_timings = f"{offset}"
                    else:
                        green_light_and_offset_timings = (f"{green_light_and_offset_timings}:{offset}")
        file.close()
    return green_light_and_offset_timings

def calculate_overall_average_for_given_network(output_data_file, network_averages, greenlight_timings):
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
    FH.close()

    average = total / count 

    prev_best = 999.999
    if os.path.exists(network_averages):
        with open(network_averages, 'r') as file:
            for line in file:
                if "New overall average" in line:
                    #last_line = file.readlines()[-1].strip()
                    match = re.search(r'(\d+\.\d+)', line)
                    if float(match.group(1)) < prev_best:
                        prev_best = float(match.group(1))
        file.close()

    status = "throw"
    if prev_best == 0 or average < prev_best:
        status = "keep"

    with open(network_averages, "a") as f:
        f.write(f"Green Light Timings: {greenlight_timings}, New overall average: {average}, {status}\n")

    return status