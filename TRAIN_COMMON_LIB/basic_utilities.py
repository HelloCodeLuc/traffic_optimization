import os

from datetime import datetime

def get_current_datetime():
    # Get the current date and time
    now = datetime.now()
    
    # Format the date and time with underscores between values
    current_datetime_str = now.strftime("%Y_%m_%d_%H_%M_%S")
    
    return current_datetime_str

def hit_space_to_continue():
    print("Press space to continue...")
    while True:
        user_input = input()
        if user_input.lower() == ' ':
            break
    return

def return_num_of_cores ():
    # Method 1: Using the os module
    num_cores_os = os.cpu_count()
    print(f"Number of CPU cores (os.cpu_count()): {num_cores_os}")
    return num_cores_os