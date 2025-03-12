import xml.etree.ElementTree as ET

file_path = weights

def modify_edge_weight(file_path, direction, highest_edge, weight_change):
    """
    Modify the weight of selected edges in a given weight file based on direction.

    :param file_path: Path to the weight file (XML format)
    :param direction: "increase" or "decrease" to modify the edge weight accordingly
    :param highest_edge: The highest edge ID to consider for modification
    :param weight_change: The amount to change the weight by
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Iterate over all edge elements
    for edge in root.findall(".//edge"):
        edge_id = edge.get("id")
        if edge_id and edge_id <= highest_edge:
            current_weight = float(edge.get("value", 0))
            
            if direction == "increase":
                edge.set("value", str(current_weight + weight_change))
            elif direction == "decrease":
                edge.set("value", str(max(0, current_weight - weight_change)))  # Ensure weight doesn't go negative
    
    # Save the modified XML file
    tree.write(file_path)

# Example usage
# modify_edge_weight("weights.xml", "increase", "-E5", 0.2)
