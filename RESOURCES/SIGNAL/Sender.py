import os
import signal

# Replace this with the PID of the target script
target_pid = int(input("Enter the PID of the target script: "))

# Use SIGBREAK instead of SIGUSR1
os.kill(target_pid, signal.SIGBREAK)
print(f"Signal SIGBREAK sent to process {target_pid}.")
