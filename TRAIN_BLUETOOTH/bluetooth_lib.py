"""
loop
    If not first bluetooth run
        Compare weights to bluetooth reference and identify largest delta
        Make change to simulated network to better align with the bluetooth reference
    Else
        Bring reference city network and timing into bluetooth run area
    
    Simulated Network
    If not first bluetooth run
        If simulated network is closer to bluetooth, keep new   
    else
        keep new
"""
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'TRAIN_COMMON_LIB'))
import basic_utilities

def bluetooth_training():
    print(">> In Bluetooth_Training")
    while True:
        if basic_utilities.check_queue_has_command("STOP", "out/command_queue.txt", 1): 
            print(">> Execution interrupted (BLUETOOTH)")
            sys.exit()
        print(">> Exit Bluetooth_Training")
        time.sleep(5)
        break