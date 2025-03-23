import subprocess
import os
import traci
import time

network_selection = "NETWORKS/simple_network/simple_network.net.xml"
config_file = "RESOURCES/DEMO_TEST/DEMO_config.sumocfg"
current_directory = os.getcwd()
max_steps = 2000
step = 0
route_files = "RESOURCES/DEMO_TEST/trip_file.xml"

def generate_sumo_config(network_selection, config_file, current_directory, max_steps, route_files):
    config_template = f"""<configuration>
    <input>
        <net-file value="{current_directory}/{network_selection}"/>
        <route-files value="{current_directory}/{route_files}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="{max_steps}"/>
    </time>
</configuration>"""
    # print (f"DEBUG INSIDE 4 {config_file}")
    with open(config_file, 'w') as f:
        f.write(config_template)
    f.close()


def generate_random_trips(network_selection, trip_file, max_steps, seed):
    debug = 0
    #cmd = f"C:/Users/chuny/Desktop/lucas/Python%20Projects/traffic_optimization/randomTrips.py -n OSM_RandomTrips/keeleandmajmack.net.xml -r {trip_file} -e {max_steps} --random -s {seed} -o out/trips.trips.xml"
    randomTrips = r'"C:\Program Files (x86)\Eclipse\Sumo\tools\randomTrips.py"'
    # print(weight_prefix)
    # sys.exit()
    cmd = f"python {randomTrips} -n {network_selection} -r {trip_file} -e {max_steps} --random -s {seed} -i 1"

    # print (f"This is the CMD line {cmd}")

    if (debug):print (f"DEBUG <generate_random_trips> : randomTrips.py command : {cmd}")

    subprocess.call(cmd, shell=True)

generate_random_trips(network_selection, route_files, max_steps, "001")
generate_sumo_config(network_selection, config_file, current_directory, max_steps, route_files)
sumo_cmd = ["sumo-gui", "-c", f"{config_file}"]

time.sleep(1)
traci.start(sumo_cmd)

while step < max_steps:
    traci.simulationStep()
    step += 1
    if step > max_steps:
        break

print("Exited the loop")
traci.close()