import tensorflow as tf
import pandas as pd
# Setup plotting
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tomlkit import boolean
import sys
from threading import Lock, Thread
from matplotlib import pyplot as plt
import numpy as np
from collections import deque
import matplotlib._color_data as mcd
import matplotlib.patches as mpatch
import keyboard  # Install with: pip install keyboard

import multiprocessing
import numpy as np
from pyomyo import Myo, emg_mode
import csv
import pandas as pd
# Load the trained model
model = tf.keras.models.load_model("gesturePredictor_RNN.model")
print("model loaded")

# Using real time data
# Todo
# 1 capture data
# 2 put it into a moving window pandas array
# 3 make the std scale of the array
# 4 make a single prediction
# Set TensorFlow logging level to ERROR (suppressing warnings)
import logging
tf.get_logger().setLevel(logging.ERROR)



data = []

samples =150
columns= samples 
rows = 8
totalSamples = samples*8
dimensions = (rows,columns)
arraySize = (samples*rows)+1

# Arrays to store EMG data for each channel
channel_0 = []
channel_1 = []
channel_2 = []
channel_3 = []
channel_4 = []
channel_5 = []
channel_6 = []
channel_7 = []

labelArray =np.zeros(1)
dimensions_f = (0,arraySize)
gestureArray=np.empty(dimensions_f)
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

    # m.add_battery_handler(print_battery)

    # Orange logo and bar LEDs
    m.set_leds([128, 0, 0], [128, 0, 0])
    # Vibrate to know we connected okay
    m.vibrate(1)

    """worker function"""
    while True:
        m.run()
    print("Worker Stopped")

#Real time classification
print("collecting samples, please make the gesture")
if __name__ == "__main__":
    
    p = multiprocessing.Process(target=worker, args=(q,))
    p.start()
    while 1:
        channel_0 = []
        channel_1 = []
        channel_2 = []
        channel_3 = []
        channel_4 = []
        channel_5 = []
        channel_6 = []
        channel_7 = []
        quantSamples = 0
        while quantSamples < samples :
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
        
        # mean = arrayLine.mean(axis=0)
        # std = arrayLine.std(axis=0)

        # # Convert mean to int32 before subtraction
        # mean_int32 = mean.astype(np.int32)
        # arrayLine -= mean_int32

        # # Ensure arrayLine has dtype float64 for division
        # arrayLine = arrayLine.astype(np.float64)

        # arrayLine /= std

        Single_gesture = arrayLine.reshape(1, samples * 8)
        # scaler = StandardScaler()
        # single_gesture_scaled = scaler.fit_transform(Single_gesture)
        # print(Single_gesture)
        # print("Single_gesture shape : " + str(Single_gesture.shape))
        # print("Single_gesture type : " + str(type(Single_gesture)))
        a = 0

        prediction = model.predict(Single_gesture)
        class_names = ['Relaxed','Fist','Spock','Pointing']
        predicted_class = class_names[np.argmax(prediction[0])]
        print("Previsão:", predicted_class)
        # Press keys based on the predicted gesture
        if predicted_class == 'Relaxed':
            keyboard.press_and_release('1')
        elif predicted_class == 'Fist':
            keyboard.press_and_release('2')
        elif predicted_class == 'Spock':
            keyboard.press_and_release('3')
        elif predicted_class == 'Pointing':
            keyboard.press_and_release('4')
        




