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
import glob
import xml.etree.ElementTree as ET
# sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_OPTIMIZATION'))
# import optimize_timing_lib
sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_COMMON_LIB'))
import basic_utilities



def bluetooth_create_ref_at_start(phase, num_batches, num_runs_per_batch, output_folder, bluetooth_network_with_timing, 
                                     max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, output_folder_subdir, network_selection, debug):
    basic_utilities.batched_run_sumo(phase, num_batches, num_runs_per_batch, output_folder, bluetooth_network_with_timing, 
                                     max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, network_selection, debug)
    shutil.copy(f"{output_folder}/{output_folder_subdir}/GUI_average_speeds.csv", f"{output_folder}/{output_folder_subdir}/GUI_average_speeds.start.csv")

def categorize_edges(network_file):
    """
    Categorizes edges in a SUMO network file into source, destination, and via edges.
    """
    tree = ET.parse(network_file)
    root = tree.getroot()
    
    outgoing_edges = {}
    incoming_edges = {}
    all_edges = set()
    
    for edge in root.findall("edge"):
        edge_id = edge.get("id")
        if edge_id and not edge_id.startswith(":"):  # Ignore internal edges
            all_edges.add(edge_id)
            for lane in edge.findall("lane"):
                for connection in root.findall("connection"):
                    if connection.get("from") == edge_id:
                        outgoing_edges.setdefault(edge_id, set()).add(connection.get("to"))
                    if connection.get("to") == edge_id:
                        incoming_edges.setdefault(edge_id, set()).add(connection.get("from"))
    
    source_edges = {e for e in all_edges if e not in incoming_edges}
    destination_edges = {e for e in all_edges if e not in outgoing_edges}
    via_edges = all_edges - source_edges - destination_edges
    
    return source_edges, destination_edges, via_edges

def generate_weight_files(network_file, output_dir, variable, ):
    """
    Generates weight file templates for source, destination, and via edges.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    source_edges, destination_edges, via_edges = categorize_edges(network_file)
    
    def write_weight_file(file_name, edges):
        with open(os.path.join(output_dir, file_name), "w") as f:
            f.write("<edgedata>\n")
            f.write("  <interval begin=\"0\" end=\"100\">\n")
            for edge in edges:
                f.write(f"    <edge id=\"{edge}\" value=\"20.0\"/>\n")
            f.write("  </interval>\n")
            f.write("</edgedata>\n")
    
    write_weight_file(f"{variable}.src.xml", source_edges)
    write_weight_file(f"{variable}.dst.xml", destination_edges)
    write_weight_file(f"{variable}.via.xml", via_edges)
    
    print("Weight files generated in", output_dir)

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

def modify_edge_weight(directory, file_prefix, direction, target_edge, weight_change):
    """
    Modify the weight of a specified edge in src, dst, and via files in the given directory.
    
    :param directory: Path to the directory where weight files are stored
    :param file_prefix: Prefix of the weight files (e.g., "example")
    :param direction: "increase" or "decrease" to modify the edge weight accordingly
    :param target_edge: The specific edge ID to modify
    :param weight_change: The amount to change the weight by
    """
    # Find all files matching the prefix (including src, dst, via)
    files = [f for f in glob.glob(os.path.join(directory, f"{file_prefix}*.xml")) if not f.endswith(".net.xml")]
    
    if not files:
        print(f"No files found matching the pattern: {file_prefix}*.xml in {directory}")
        return
    
    print(f"Processing files: {files}")
    
    # Iterate over each file and look for the specified edge
    for file_path in files:
        print(f"Checking file: {file_path}")
        
        try:
            tree = ET.parse(file_path)
        except ET.ParseError as e:
            print(f"Error parsing {file_path}: {e}")
            continue  # Skip this file and continue with the next one
        
        root = tree.getroot()
        modified = False  # Track whether the edge was modified in this file
        
        for interval in root.findall(".//interval"):
            for edge in interval.findall("edge"):
                edge_id = edge.get("id")
                if edge_id and edge_id.strip() == target_edge:  # Ensure correct match
                    raw_value = edge.get("value")  # Extract raw value
                    if raw_value is None:
                        print(f"Warning: Edge {edge_id} in {file_path} has no value attribute, defaulting to 0.")
                        current_weight = 0
                    else:
                        try:
                            current_weight = float(raw_value)
                        except ValueError:
                            print(f"Error: Edge {edge_id} in {file_path} has an invalid value '{raw_value}', skipping.")
                            continue

                    print(f"Found edge: {target_edge} in {file_path}, current weight: {current_weight}")

                    # Modify the weight
                    if direction == "increase":
                        new_weight = current_weight + weight_change
                    elif direction == "decrease":
                        new_weight = max(0, current_weight - weight_change)  # Prevent negative weights
                    else:
                        print(f"Error: Unknown direction '{direction}'")
                        return
                    
                    print(f"Updating edge {target_edge} in {file_path} from {current_weight} to {new_weight}")
                    edge.set("value", str(new_weight))
                    modified = True
                    break  # Stop after modifying the edge
        
        if modified:
            # Write the changes back to the file
            tree.write(file_path)
            print(f"Changes written to {file_path}")
            break  # Stop after modifying the first occurrence of the edge

def bluetooth_training(phase, bluetooth_network_with_timing, output_folder, output_data_file, max_num_of_runs_on_network, num_batches, num_runs_per_batch, network_selection, 
                                                max_steps, network_with_timing, light_names, timing_light_increment, 
                                                num_of_greenlight_duplicate_limit, average_speed_n_steps, weight_prefix, weight_change, weight_accuracy):
    output_folder_subdir = "TRAIN_BLUETOOTH"
    network_name = os.path.basename(os.path.dirname(network_selection))

    print(">> In Bluetooth_Training")
    # print(f"Network File: {network_selection}, Output Directory: {output_folder}")
    # print(f"Bluetooth Network File: {bluetooth_network_with_timing}")
    
    bluetooth_csv = os.path.splitext(os.path.splitext(network_selection)[0])[0] + ".bluetooth.csv"
    # bluetooth_csv = f"NETWORKS/{filename}.bluetooth.csv"
    # print(f"Bluetooth CSV File: {bluetooth_csv}")

    debug = 0
    current_directory = os.getcwd()
    speed_limit = basic_utilities.extract_speeds_from_edges(network_selection)

    if not os.path.exists(bluetooth_network_with_timing):
        shutil.copy2(network_selection, bluetooth_network_with_timing)
        shutil.copy2(network_selection, f"{bluetooth_network_with_timing}.temp")

    if os.path.exists(f"NETWORKS/{network_name}/weights.src.xml"):
        shutil.copy2(f"NETWORKS/{network_name}/weights.src.xml", f"{output_folder}/TRAIN_BLUETOOTH")
        shutil.copy2(f"NETWORKS/{network_name}/weights.dst.xml", f"{output_folder}/TRAIN_BLUETOOTH")
        if os.path.exists(f"NETWORKS/{network_name}/weights.via.xml"):
            shutil.copy2(f"NETWORKS/{network_name}/weights.via.xml", f"{output_folder}/TRAIN_BLUETOOTH")
    else:
        generate_weight_files(network_selection, f"{output_folder}/TRAIN_BLUETOOTH", weight_prefix)
        generate_weight_files(network_selection, f"NETWORKS/{network_name}", weight_prefix)
        print("Generated new weight files")
        # sys.exit()

    bluetooth_create_ref_at_start(phase, num_batches, num_runs_per_batch, output_folder, bluetooth_network_with_timing, 
                                     max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, output_folder_subdir, network_selection, debug)
    average_diff, target_edge, max_discrepancy_value, direction, = basic_utilities.calculate_average_difference(bluetooth_csv, f"{output_folder}/{output_folder_subdir}/GUI_average_speeds.csv")

    while True:
        #This is a backdoor for user to initiate stop from GUI
        if basic_utilities.check_queue_has_command("STOP", "out/command_queue.txt", 1): 
            print(">> Execution interrupted (BLUETOOTH)")
        if os.path.exists(bluetooth_csv):
            basic_utilities.batched_run_sumo(phase, num_batches, num_runs_per_batch, output_folder, network_with_timing,
                                              max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, network_selection, debug)
            average_diff, target_edge, max_discrepancy_value, direction, = basic_utilities.calculate_average_difference(bluetooth_csv, f"{output_folder}/{output_folder_subdir}/GUI_average_speeds.csv")
            print(f"The average speed difference is: {average_diff:.3f} km/h")
            print(f"The largest discrepancy is on Edge ID '{target_edge}' with a difference of {max_discrepancy_value} km/h")
        else:
            print("DEBUG: No Bluetooth CSV found")
            sys.exit()
        if average_diff < weight_accuracy:
            print("DEBUG: Weight Accuracy Met")
            break
        else:
            modify_edge_weight(f"{output_folder}/TRAIN_BLUETOOTH", weight_prefix, direction, target_edge, weight_change)
            basic_utilities.batched_run_sumo(phase, num_batches, num_runs_per_batch, output_folder, bluetooth_network_with_timing, 
                                             max_steps, current_directory, average_speed_n_steps, speed_limit, output_data_file, network_selection, debug)
            continue
    print(">> Exit Bluetooth_Training")
    time.sleep(5)