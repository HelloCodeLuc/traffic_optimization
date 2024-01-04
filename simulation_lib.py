import subprocess

def my_plot(output_data_file):
    import matplotlib.pyplot as plt

    # Read the file and process lines
    with open(output_data_file, 'r') as file:
        lines = file.readlines()

    # Count the number of lines
    num_lines = len(lines)
    print(f"Number of lines in the file: {num_lines}")

    # Extract and plot Average Idle Times
    iteration_numbers = []
    average_idle_times = []

    for index, line in enumerate(lines):
        # Extract information from each line
        parts = line.split(',')
        iteration = index
        average_idle_time = float(parts[-1].split(':')[1])

        # Append to lists
        iteration_numbers.append(iteration)
        average_idle_times.append(average_idle_time)

    # Plotting
    plt.plot(iteration_numbers, average_idle_times, marker='o')
    plt.xlabel('Iteration')
    plt.ylabel('Average Idle Time')
    plt.title('Average Idle Time Over Iterations')
    plt.grid(True)
    plt.xlim(left=0)
    plt.show()

# Run randomtrips.py to generate random trips and save them to a file
def generate_random_trips(network_selection, trip_file, max_steps, seed):
    #cmd = f"C:/Users/chuny/Desktop/lucas/Python%20Projects/traffic_optimization/randomTrips.py -n OSM_RandomTrips/keeleandmajmack.net.xml -r {trip_file} -e {max_steps} --random -s {seed} -o output/trips.trips.xml"
    randomTrips = r'"C:\Program Files (x86)\Eclipse\Sumo\tools\randomTrips.py"'
    cmd = f"python {randomTrips} -n {network_selection} -r {trip_file} -e {max_steps} --random -s {seed}"

    print (f"DEBUG 1 : randomTrips.py command : {cmd}")
    subprocess.call(cmd, shell=True)

# Generate the SUMO configuration file with the given template
def generate_sumo_config(network_selection, config_file, current_directory, route_files):
    config_template = f"""<configuration>
    <input>
        <net-file value="{current_directory}/{network_selection}"/>
        <route-files value="{current_directory}/{route_files}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="2000"/>
    </time>
</configuration>"""

    with open(config_file, 'w') as f:
        f.write(config_template)
