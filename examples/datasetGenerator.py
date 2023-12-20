import pygame
from pygame.locals import *
import multiprocessing
import numpy as np
from pyomyo import Myo, emg_mode
import csv
import pandas as pd

# Initial definitions
samples = 100
columns = samples + 1
rows = 8
totalSamples = samples * 8
totalColumns = totalSamples + 1
dimensions = (rows, columns)
dimensions2 = (rows, columns - 1)

arraySize = (samples * rows) + 1
signal_header = np.zeros((arraySize), dtype='object')

# Fill the signal header with its names
for i in range(0, totalColumns):
    if(i == totalColumns - 1):
        signal_header[i] = "gesture"
    else:
        signal_header[i] = "sample_" + str(i)

# Arrays to store EMG data for each channel
channel_0 = []
channel_1 = []
channel_2 = []
channel_3 = []
channel_4 = []
channel_5 = []
channel_6 = []
channel_7 = []

quantSamples = 0

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
    m = Myo(mode=emg_mode.PREPROCESSED)
    m.connect()

    def add_to_queue(emg, movement):
        q.put(emg)

    m.add_emg_handler(add_to_queue)

    def print_battery(bat):
        print("Battery level:", bat)

    m.add_battery_handler(print_battery)

    # Orange logo and bar LEDs
    m.set_leds([128, 0, 0], [128, 0, 0])
    # Vibrate to know we connected okay
    m.vibrate(1)

    """worker function"""
    while True:
        m.run()
    print("Worker Stopped")

# -------- Main Program Loop -----------
if __name__ == "__main__":
    # User input for the type of gesture
    label = input("Enter type of gesture: ")
    p = multiprocessing.Process(target=worker, args=(q,))
    p.start()

    try:
        

        while quantSamples < 100:
            while not(q.empty()):
                emg = list(q.get())
                channel_0.append(emg[0])
                channel_1.append(emg[1])
                channel_2.append(emg[2])
                channel_3.append(emg[3])
                channel_4.append(emg[4])
                channel_5.append(emg[5])
                channel_6.append(emg[6])
                channel_7.append(emg[7])

                quantSamples += 1

        # Concatenate all channels into one horizontal array
        arrayLine = np.concatenate((channel_0, channel_1, channel_2, channel_3, channel_4, channel_5, channel_6, channel_7), axis=None)
        gestureArray = np.vstack([arrayLine,gestureArray])# stack lines of signal
        # Append label to the end of the array
        arrayLine = np.append(arrayLine, label)

        
        


    except KeyboardInterrupt:
        print("Quitting")
        pygame.quit()
        quit()
