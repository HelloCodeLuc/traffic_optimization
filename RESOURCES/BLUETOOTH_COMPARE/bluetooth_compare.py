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

    differences = {}
    for edge in common_edges:
        difference = speeds1[edge] - speeds2[edge]
        differences[edge] = difference

    average_difference = sum(abs(d) for d in differences.values()) / len(differences)

    # Identify the edge with the largest discrepancy based on absolute difference
    max_discrepancy_edge = max(differences, key=lambda edge: abs(differences[edge]))  # Corrected key function
    max_discrepancy_value = differences[max_discrepancy_edge]

    # Determine whether the max discrepancy is positive or negative
    # if the direction is decrease, it means that the bluetooth is running on that edge more cars than the city data. Vice versa if the direction is increase
    discrepancy_direction = 'decrease' if max_discrepancy_value > 0 else 'increase'

    return average_difference, (max_discrepancy_edge, max_discrepancy_value, discrepancy_direction)

average_diff, max_discrepancy = calculate_average_difference(file1, file2)

if average_diff is not None:
    print(f"The average speed difference is: {average_diff:.3f} km/h")
    print(f"The largest discrepancy is on Edge ID '{max_discrepancy[0]}' with a difference of {max_discrepancy[1]:.3f} km/h, which is {max_discrepancy[2]}.")
else:
    print("No common data to compare.")
