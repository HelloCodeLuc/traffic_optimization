import os
import shutil
import subprocess
import xml.etree.ElementTree as ET

def generate_weight_file(network_file, weight_prefix="weights", default_weight=1.0):
    """
    Generates SUMO weight files (source, destination, and via) for all edges.

    :param network_file: Path to SUMO .net.xml file
    :param weight_prefix: Prefix for the weight files (default: "weights")
    :param default_weight: Default weight assigned to edges
    """
    weight_file = f"{weight_prefix}.xml"

    tree = ET.parse(network_file)
    root = tree.getroot()
    
    weights = ET.Element("weights")

    for edge in root.findall("edge"):
        edge_id = edge.get("id")
        ET.SubElement(weights, "edge", id=edge_id, weight=str(default_weight))
    
    tree = ET.ElementTree(weights)
    with open(weight_file, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
    
    # Duplicate the weight file for SUMO's expected files
    shutil.copy(weight_file, f"{weight_prefix}.src.xml")
    shutil.copy(weight_file, f"{weight_prefix}.dst.xml")
    shutil.copy(weight_file, f"{weight_prefix}.via.xml")

    print(f"Weight files generated: {weight_prefix}.src.xml, {weight_prefix}.dst.xml, {weight_prefix}.via.xml")
    return weight_prefix

def generate_trips(network_file, weight_prefix="weights", trip_file="trips.rou.xml", trip_count=500, period=1.0):
    """
    Uses SUMO's randomTrips.py to generate a route file with the given weight files.

    :param network_file: Path to SUMO .net.xml file
    :param weight_prefix: Prefix for weight files (default: "weights")
    :param trip_file: Path to output .rou.xml file
    :param trip_count: Number of trips to generate
    :param period: Time interval between trip generations
    """
    cmd = [
        "python", "C:/Program Files (x86)/Eclipse/Sumo/tools/randomTrips.py",
        "-n", network_file,
        "--weights-prefix", weight_prefix,
        "-r", trip_file,
        "-e", str(trip_count),
        "--period", str(period)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"Route file generated: {trip_file}")
    return trip_file

def run_sumo(network_file, route_file):
    """
    Runs SUMO with the given network and route file.

    :param network_file: Path to SUMO .net.xml file
    :param route_file: Path to generated .rou.xml file
    """
    cmd = ["sumo-gui", "-n", network_file, "-r", route_file]
    
    print(f"Starting SUMO GUI: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

# Main Function
def main():
    network_file = "RESOURCES/WEIGHTS_TEST/simple_network.net.xml"  # Change to your network file
    weight_prefix = generate_weight_file(network_file)
    route_file = generate_trips(network_file, weight_prefix=weight_prefix)
    run_sumo(network_file, route_file)

if __name__ == "__main__":
    main()
