import traci
import traci.constants as tc
import os

current_directory = os.getcwd()

file_path = os.path.join(current_directory, 'output/sumo_config_9759.sumocfg')

# Connect to SUMO
traci.start(["sumo", "-c", file_path])

# Initialize a dictionary to store idle times for each vehicle
idle_times = {}

# Simulation steps
simulation_steps = 1000  # Adjust the number of simulation steps as needed
simulation_step_size = 1  # Adjust the simulation step size as needed

for step in range(simulation_steps):
    traci.simulationStep()

    # Get the list of vehicles
    vehicles = traci.vehicle.getIDList()

    # Update idle times
    for vehicle_id in vehicles:
        speed = traci.vehicle.getSpeed(vehicle_id)
        if speed < 5:
            if vehicle_id not in idle_times:
                idle_times[vehicle_id] = 0
            else:
                idle_times[vehicle_id] += simulation_step_size

# Calculate average idle time
average_idle_time = sum(idle_times.values()) / len(idle_times)

# Disconnect from SUMO
traci.close()

# Print the average idle time
print("Average Idle Time:", average_idle_time)
