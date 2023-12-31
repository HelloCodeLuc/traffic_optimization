

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
    plt.legend(loc='lower right')
    plt.show()