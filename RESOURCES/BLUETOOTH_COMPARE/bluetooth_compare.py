import csv

file1 = "RESOURCES/BLUETOOTH_COMPARE/simple_network.bluetooth.csv"
file2 = "RESOURCES/BLUETOOTH_COMPARE/simple_network_output.bluetooth.csv"

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

def calculate_average_difference(file1, file2):
    speeds1 = read_average_speeds(file1)
    speeds2 = read_average_speeds(file2)

    common_edges = set(speeds1.keys()) & set(speeds2.keys())
    if not common_edges:
        print("No common Edge IDs found between the files.")
        return None, None

    differences = {edge: abs(speeds1[edge] - speeds2[edge]) for edge in common_edges}
    average_difference = sum(differences.values()) / len(differences)

    # Identify the edge with the largest discrepancy
    max_discrepancy_edge = max(differences, key=differences.get)
    max_discrepancy_value = differences[max_discrepancy_edge]

    return average_difference, max_discrepancy_edge, max_discrepancy_value

average_diff, max_discrepancy_edge, max_discrepancy_value = calculate_average_difference(file1, file2)

if average_diff is not None:
    print(f"The average speed difference is: {average_diff:.3f} km/h")
    print(f"The largest discrepancy is on Edge ID '{max_discrepancy_edge}' with a difference of {max_discrepancy_value} km/h")
else:
    print("No common data to compare.")
