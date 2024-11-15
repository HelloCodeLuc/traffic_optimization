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

edge_id = "-E1"  # Replace with the edge ID you are analyzing

try:
    while step <= max_steps:
        traci.simulationStep()  # Advance the simulation
        step += 1

        if step > (max_steps-last_n_steps):
            # Check all vehicles currently on the edge
            vehicles = traci.edge.getLastStepVehicleIDs(edge_id)

            if vehicles:
                total_speed = sum(traci.vehicle.getSpeed(vid) for vid in vehicles)
                avg_speed = total_speed / len(vehicles)*3.6
            else:
                avg_speed = 0

            # Store the average speed for this step
            speed_data.append(avg_speed)

finally:
    traci.close()

# Calculate the average travel time
print(f"Average speed on edge {edge_id}: {avg_speed}")