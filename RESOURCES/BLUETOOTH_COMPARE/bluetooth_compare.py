import csv

file1 = "RESOURCES/BLUETOOTH_COMPARE/simple_network.bluetooth.csv"
file2 = "RESOURCES/BLUETOOTH_COMPARE/simple_network_output.bluetooth.csv"

delta_threshold = 5.0  # Set threshold for significant differences

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

def calculate_average_difference(file1, file2, threshold):
    speeds1 = read_average_speeds(file1)
    speeds2 = read_average_speeds(file2)

    common_edges = set(speeds1.keys()) & set(speeds2.keys())
    if not common_edges:
        print("No common Edge IDs found between the files.")
        return None, None, None, None, {}

    differences = {edge: speeds1[edge] - speeds2[edge] for edge in common_edges}
    average_difference = sum(abs(diff) for diff in differences.values()) / len(differences)

    # Identify the edge with the largest discrepancy
    max_discrepancy_edge = max(differences, key=lambda x: abs(differences[x]))
    max_discrepancy_value = differences[max_discrepancy_edge]
    max_discrepancy_direction = "increase" if max_discrepancy_value > 0 else "decrease"

    # Identify all edges with discrepancies higher than the threshold
    significant_differences = {edge: (diff, "increase" if diff > 0 else "decrease") for edge, diff in differences.items() if abs(diff) > threshold}

    return average_difference, max_discrepancy_edge, max_discrepancy_value, max_discrepancy_direction, significant_differences

average_diff, max_edge, max_value, significant_diffs = calculate_average_difference(file1, file2, delta_threshold)

if average_diff is not None:
    print(f"The average speed difference is: {average_diff:.3f} km/h")
    print(f"The largest discrepancy is on Edge ID '{max_edge}' with a difference of {max_value:.3f} km/h")
    if significant_diffs:
        print("Edges with discrepancies greater than threshold:")
        for edge, (diff, direction) in significant_diffs.items():
            print(f"Edge ID '{edge}': Difference of {diff:.3f} km/h ({direction})")
    else:
        print("No edges exceed the threshold.")
else:
    print("No common data to compare.")
