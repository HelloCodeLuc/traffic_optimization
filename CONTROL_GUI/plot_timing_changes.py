

import xml.etree.ElementTree as ET
import csv
import re

def extract_tl_logic_ids(network_file):
    tree = ET.parse(network_file)
    root = tree.getroot()
    
    tl_logic_ids = [tl.get("id") for tl in root.findall(".//tlLogic")]
    return tl_logic_ids

def extract_j_tl_mapping(network_file):
    tree = ET.parse(network_file)
    root = tree.getroot()
    
    j_tl_mapping = {}
    for conn in root.findall(".//connection"):
        via = conn.get("via")
        tl = conn.get("tl")
        if via and tl:
            j_number = via.split(":J")[-1].split("_")[0]
            j_tl_mapping[f"J{j_number}"] = tl
    
    return j_tl_mapping

# Extract the number sequence after "Green Light Timings:"
def extract_timings(line):
    match = re.search(r"Green Light Timings: ([\d:]+)", line)
    return match.group(1) if match else None

# Function to process the timings
def process_timings(tl_logic_ids, timings_str):
    if not timings_str:
        print("No valid timings found.")
        return

    timings_list = [int(num) for num in timings_str.split(":")]
    timings_dict = {}

    #print("\nProcessing traffic light timings:")
    for i in range(0, len(timings_list), 2):
        if i // 2 >= len(tl_logic_ids):
            break  # Stop if more pairs than traffic lights

        offset = timings_list[i]
        green_light_timing = timings_list[i + 1]
        tl_name = tl_logic_ids[i // 2]

        timings_dict[tl_name] = {"offset": offset, "green_light_timing": green_light_timing}

    return timings_dict

# coordinat4s to the Jnumber, Jnumber to tlname, tlname to timing change
# at the end we want to have a dictionary that maps the coodinats to the timing (green, offset)
def coordinates_to_diff_of_offset_and_greenlight (network_file, network_junction_csv, network_averages):
    # Example usage
    #file_path = "input.xml"  # Change this to your actual file path
    tl_logic_ids = extract_tl_logic_ids(network_file)
    #print(tl_logic_ids)

    # Example usage
    #file_path = "input.xml"  # Change this to your actual file path
    j_tl_mapping = extract_j_tl_mapping(network_file)
    #print(j_tl_mapping)

    # Read junction coordinates from file
    junction_coords = {}
    with open(network_junction_csv, "r") as junction_file:
        reader = csv.reader(junction_file)
        next(reader)  # Skip header
        for row in reader:
            junction_id, x, y = row
            key = f"{x},{y}"
            junction_coords[key] = j_tl_mapping.get(junction_id, "not applicable")

    # Print the results
    #print(junction_coords)

    # Read file and extract the first and last "keep" lines
    first_keep = None
    last_keep = None

    with open(network_averages, "r") as file:
        for line in file:
            if "keep" in line:
                if first_keep is None:
                    first_keep = line.strip()  # Save the first "keep" line
                last_keep = line.strip()  # Overwrites until the last "keep" line


    first_keep_timings = extract_timings(first_keep) if first_keep else None
    last_keep_timings = extract_timings(last_keep) if last_keep else None

    # Process first and last "keep" lines
    first_keep_dict = process_timings(tl_logic_ids, first_keep_timings)
    last_keep_dict = process_timings(tl_logic_ids, last_keep_timings)

    # Create a new dictionary indexed by x,y coordinates
    coord_differences = {}

    for coord, tl_name in junction_coords.items():
        if tl_name in first_keep_dict and tl_name in last_keep_dict:
            # Get values
            offset_last = last_keep_dict[tl_name]["offset"]
            offset_first = first_keep_dict[tl_name]["offset"]
            green_last = last_keep_dict[tl_name]["green_light_timing"]
            green_first = first_keep_dict[tl_name]["green_light_timing"]

            # Compute differences
            offset_diff = offset_last - offset_first
            green_diff = green_last - green_first

            # Store in dictionary
            coord_differences[coord] = {
                "offset_diff": offset_diff,
                "green_diff": green_diff
            }
    return coord_differences

#   with open(file_name, mode='r') as file:
# network_file = "../out/2025_03_15_13_51_49/TRAIN_OPTIMIZATION/school_extended.timing.net.xml.temp"
# network_junction_csv = "../NETWORKS/school_extended/school_extended_junctions.bluetooth.csv"
# network_averages = "../out/2025_03_15_13_51_49/TRAIN_OPTIMIZATION/network_averages.txt"

# coord_differences = coordinates_to_diff_of_offset_and_greenlight (network_file, network_junction_csv, network_averages)
# # Print the final dictionary
# print(coord_differences)
