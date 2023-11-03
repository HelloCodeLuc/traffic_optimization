import traci

# Start the SUMO simulation and connect to it
traci.start(['sumo', '-c', 'C:/Users/chuny/Desktop/OSM_RandomTrips/keeleandmajmack.sumocfg'])

# Create a dictionary to store waiting times for each vehicle
waiting_times = {}
route_lengths = {}  # Dictionary to store the route length for each vehicle

# Main simulation loop
while traci.simulation.getMinExpectedNumber() > 0:
    # Step the simulation
    traci.simulationStep()

    # Get a list of all vehicles in the simulation
    vehicles = traci.vehicle.getIDList()

    for vehicle_id in vehicles:
        # Check if the vehicle is already in the dictionary
        if vehicle_id not in waiting_times:
            waiting_times[vehicle_id] = 0

        # Get the waiting time for the vehicle (time spent waiting at traffic lights)
        waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
        waiting_times[vehicle_id] += waiting_time

    # Update route lengths for each vehicle
    for vehicle_id in route_lengths:
        route = traci.vehicle.getRoute(vehicle_id)
        route_length = sum(traci.lane.getLength(lane_id) for lane_id in route)
        route_lengths[vehicle_id] = route_length

# Calculate and print the average waiting time for each vehicle
for vehicle_id in waiting_times:
    total_waiting_time = waiting_times[vehicle_id]
    route_length = route_lengths.get(vehicle_id, 0)
    
    # Calculate the average waiting time
    average_waiting_time = total_waiting_time / route_length if route_length > 0 else 0

    print(f"Vehicle {vehicle_id}: Average Waiting Time = {average_waiting_time:.2f} seconds")

# Finish the simulation and close the connection
traci.close()
