import signal
import time

# Define a signal handler
def signal_handler(signum, frame):
    print(f"Received signal {signum}. Performing action!")

# Use SIGBREAK instead of SIGUSR1
signal.signal(signal.SIGBREAK, signal_handler)

print("Target script is running. Waiting for a signal...")
try:
    while True:
        time.sleep(1)  # Simulate doing something and wait for signals
except KeyboardInterrupt:
    print("Script terminated.")
