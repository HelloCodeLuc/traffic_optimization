import xml.etree.ElementTree as ET
import os

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

def generate_weight_files(network_file, output_dir, variable):
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
                f.write(f"    <edge id=\"{edge}\" value=\"1.0\"/>\n")
            f.write("  </interval>\n")
            f.write("</edgedata>\n")
    
    write_weight_file(f"{variable}.src.xml", source_edges)
    write_weight_file(f"{variable}.dst.xml", destination_edges)
    write_weight_file(f"{variable}.via.xml", via_edges)
    
    print("Weight files generated in", output_dir)

# Example usage
network_file = "RESOURCES/WEIGHT_GENERATION/school_extended.net.xml"
output_dir = "RESOURCES/WEIGHT_GENERATION"
prefix = "weights"
generate_weight_files(network_file, output_dir, prefix)
