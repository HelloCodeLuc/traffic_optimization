import sys
import os
import simulation_lib as simulation_lib 

import random
import shutil
import argparse
#import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import re
import subprocess
from multiprocessing import Process, Queue

def run_sumo_simulation(simulation_config, option, result_queue):
    print(f"INSIDE {simulation_config} : {option}")
    #command = ["sumo", "-c", simulation_config]
    # Modify the command and subprocess call as needed
    # You might need to capture the output and extract the relevant information
    result = 42.0  # Replace this with the actual result from the simulation
    result_queue.put(result)

if __name__ == "__main__":
    # Specify simulation configurations for each simulation
    simulation_configs = ["simulation1.sumocfg", "simulation2.sumocfg", "simulation3.sumocfg"]

    result_queue = Queue()
    # Create a list to store the processes and results
    processes = []

    

    # Launch each simulation in a separate process
    for config in simulation_configs:
        process = Process(target=run_sumo_simulation, args=(config,"option2", result_queue))
        processes.append(process)
        process.start()

    # Wait for all processes to finish (optional)
    for process in processes:
        process.join()

    results = []
    # Collect results from each process
    while not result_queue.empty():
        result = result_queue.get()
        results.append(result)

    print("Results:", results)
