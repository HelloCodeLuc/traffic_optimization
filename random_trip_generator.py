import os
import subprocess
import traci
import random
import time

def generate_random_trips(trip_file, max_steps, seed):
    # Run randomtrips.py to generate random trips and save them to a file
    cmd = f"python randomtrips.py -n keeleandmajmack.net.xml -r {trip_file} -e {max_steps} --random -s {seed}"
    subprocess.call(cmd, shell=True)

def run_sumo():
    # Launch SUMO and load the generated random trips
    sumo_cmd = ["sumo-gui", "-c", "keeleandmajmack.sumocfg"]
    traci.start(sumo_cmd)

    step = 0
    while step < max_steps:
        traci.simulationStep()
        step += 1
        time.sleep(0.1)

    traci.close()

if __name__ == "__main__":
    num_runs = 1  # Change this to the number of times you want to run the simulation
    max_steps = 2000  # Change this to the desired number of simulation steps

    for run in range(num_runs):
        random_seed = random.randint(1, 10000)  # Use a different random seed for each run
        trip_file = f"random_trips_{random_seed}.xml"  # Generate a unique trip file name for each run

        # Generate random trips
        generate_random_trips(trip_file, max_steps, random_seed)

        # Run the SUMO simulation
        run_sumo()

        # Clean up generated trip file
        os.remove(trip_file)
