import traci
import sumolib
from collections import deque

# Start SUMO with TraCI
sumoBinary = sumolib.checkBinary('sumo-gui')  # or 'sumo' for command-line version
sumoCmd = [sumoBinary, "-c", "C:/Users/Lucas/Lucas/traffic_optimization/traffic_optimization/RESOURCES/DATA_EXTRACTION/sumo_config_1355.sumocfg", "--duration-log.statistics"]
traci.start(sumoCmd)

step = 0
max_steps = 2000
last_n_steps = 20
speed_data = deque(maxlen=last_n_steps)
avg_speed = 0

all_edges = traci.edge.getIDList()

# Initialize a dictionary to store arrays of average speeds for each edge
edge_speeds = {}

try:
    while step <= max_steps:
        traci.simulationStep()  # Advance the simulation
        step += 1

        if step > (max_steps-last_n_steps):
            for edge_id in all_edges:
                if not edge_id.startswith(":"):
                    # Get the average speed for the edge at this simulation step
                     avg_speed = traci.edge.getLastStepMeanSpeed(edge_id)
                    # # Check all vehicles currently on the edge
                    # vehicles = traci.edge.getLastStepVehicleIDs(edge_id)

                    # if vehicles:
                    #     total_speed = sum(traci.vehicle.getSpeed(vid) for vid in vehicles)
                    #     avg_speed = total_speed / len(vehicles)*3.6
                    # else:
                    #     avg_speed = 0

                print(f"Average speed on edge {edge_id}: {avg_speed}")                
                    # Add the speed to the hash of arrays
                if edge_id not in edge_speeds:
                    edge_speeds[edge_id] = []  # Initialize the array for this edge
                edge_speeds[edge_id].append(avg_speed)
                    # # Store the average speed for this step
                    # speed_data.append(avg_speed)

    # Print the hash of arrays
    print("Hash of arrays (average speeds per edge):")
    for edge_id, speeds in edge_speeds.items():
        print(f"{edge_id}: {speeds}")

finally:
    traci.close()