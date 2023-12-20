import multiprocessing
import numpy as np
import pandas as pd
import os
import time

from pyomyo import Myo, emg_mode

# Modify the data_worker function to initialize 'collect' and concatenate along axis 0
def data_worker(mode, seconds, gesture, filepath, choice):
    collect = True  # Initialize 'collect' variable

    # ------------ Myo Setup ---------------
    m = Myo(mode=mode)
    m.connect()

    myo_data = [[] for _ in range(8)]  # Initialize eight empty lists for channels

    def add_to_queue(emg, movement):
        for i in range(8):
            myo_data[i].append(emg[i])

    m.add_emg_handler(add_to_queue)

    def print_battery(bat):
        print("Battery level:", bat)

    m.add_battery_handler(print_battery)

    # Its go time
    m.set_leds([0, 128, 0], [0, 128, 0])
    # Vibrate to know we connected okay
    m.vibrate(1)

    print(f"Data Worker started to collect for {gesture} gesture")
    print("Please perform the gesture within the next " + str(seconds) + " seconds.")
    # Start collecting data.
    start_time = time.time()

    while collect:
        if time.time() - start_time < seconds:
            m.run()
        else:
            collect = False
            collection_time = time.time() - start_time
            print(f"Finished collecting for {gesture} gesture.")
            print(f"Collection time: {collection_time}")
            print(len(myo_data[0]), "frames collected for each channel")

            # Concatenate all channels into one array along axis 0
            LineArray = np.concatenate(myo_data, axis=0)

            # Add the number corresponding to the gesture label at the end of LineArray
            label_number = int(choice)
            gesture_label = f"Gesture_{label_number}"

            # Concatenate the gesture label at the end of LineArray
            LineArray = np.concatenate([LineArray, np.array([label_number])])

            # Save the concatenated array horizontally to a CSV file
            np.savetxt(filepath, LineArray.reshape(1, -1), delimiter=',', header=','.join([f"Sample_{i}" for i in range(len(LineArray)-1)]) + ',Gesture', comments='', fmt='%f')
            print("CSV Saved at: ", filepath)

# -------- Main Program Loop -----------
if __name__ == '__main__':
    seconds_per_gesture = 3

    # Allow the user to choose the gesture
    print("Choose a gesture to record:")
    print("0. Relaxed")
    print("1. Fist")
    print("2. Spock")
    print("3. Pointing")

    choice = input("Enter the number corresponding to the gesture: ")
    
    gesture_mapping = {
        '1': 'relaxed',
        '2': 'fist',
        '3': 'spock',
        '4': 'pointing',
    }

    chosen_gesture = gesture_mapping.get(choice)
    if chosen_gesture:
        iteration = input("Enter the iteration number: ")
        file_name = f"{chosen_gesture}_iteration{iteration}_{seconds_per_gesture}_seconds_emg.csv"
        file_path = os.path.join("datasets", file_name)
        mode = emg_mode.PREPROCESSED
        p = multiprocessing.Process(target=data_worker, args=(mode, seconds_per_gesture, chosen_gesture, file_path, choice))
        p.start()
        p.join()  # Wait for the process to finish
    else:
        print("Invalid choice. Please choose a valid number.")
