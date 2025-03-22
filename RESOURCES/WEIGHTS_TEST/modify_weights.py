import xml.etree.ElementTree as ET
import glob
import os

file_prefix = "example"
direction = "increase"  # or "decrease"
target_edge = "-E5"  # The edge you're looking for
weight_change = 1  # Amount to change the weight by
directory = "RESOURCES/WEIGHTS_TEST"  # Set to current directory

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
                    current_weight = float(edge.get("value", 0))
                    
                    # Modify the weight based on direction
                    if direction == "increase":
                        edge.set("value", str(current_weight + weight_change))
                    elif direction == "decrease":
                        edge.set("value", str(max(0, current_weight - weight_change)))  # Prevent negative weights
                    
                    print(f"Modified {target_edge} in {file_path}: New weight = {edge.get('value')}")
                    modified = True
                    break  # Stop after modifying the edge
        
        if modified:
            # Write the changes back to the file
            tree.write(file_path)
            print(f"Changes written to {file_path}")
            break  # Stop after modifying the first occurrence of the edge

# Example function call
modify_edge_weight(directory, file_prefix, direction, target_edge, weight_change)
