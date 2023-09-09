import os
import traci
import traci.constants as tc

def run_sumo_simulation(sumo_binary, sumo_config):
    # Step 1: Start the SUMO simulation
    sumo_cmd = [sumo_binary, "-c", sumo_config]
    traci.start(sumo_cmd)

    try:
        # Step 2: Simulation loop
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

            # Perform actions during the simulation step if needed

        # Step 3: End the simulation
        traci.close()
    except Exception as e:
        print("Error in simulation loop:", e)

if __name__ == "__main__":
    print("Start main...")
    # Path to the SUMO binary (e.g., sumo or sumo-gui)
    #sumo_binary = "C:/Users/chuny/Desktop/lucas/Eclipse/Sumo/bin/sumo-gui.exe"
    sumo_binary = "C:/Users/chuny/Desktop/lucas/Eclipse/Sumo/bin/sumo.exe"

    # Path to the SUMO configuration file
    #sumo_config = "C:/Users/chuny/Desktop/lucas/Python Projects/Sumo_setup/my_config-file.sumocfg"
    sumo_config = "C:/Users/chuny/Desktop/lucas/Python Projects/Sumo_setup/keeleandmajmack.sumocfg"

    # Run the simulation
    run_sumo_simulation(sumo_binary, sumo_config)

    print ("Finished execution.")