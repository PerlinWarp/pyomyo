# SpeedTest
import time
import multiprocessing

from myo_serial import MyoRaw

PLOT = True
carryOn = True
RAW = False
FILTERED = True

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

m = MyoRaw(raw=RAW, filtered=FILTERED)
m.connect()
print(f"Connected to Myo using raw={RAW}, filtered={FILTERED}.")

def worker(q):
	def add_to_queue(emg, movement):
		q.put(emg)

	m.add_emg_handler(add_to_queue)

	"""worker function"""
	while carryOn:
		m.run(1)
	print("Worker Stopped")

def print_battery(bat):
	print("Battery level:", bat)

m.add_battery_handler(print_battery)

 # Orange logo and bar LEDs
m.set_leds([128, 0, 0], [128, 0, 0])
# Vibrate to know we connected okay
m.vibrate(1)

# -------- Main Program Loop -----------
p = multiprocessing.Process(target=worker, args=(q,))
p.start()

data = []
n_points = 50
freqs = []

start_time = time.time()
last_n = start_time

try:
	while carryOn:
		while not(q.empty()):
			# Get the new data from the Myo queue
			emg = list(q.get())
			data.append(emg)

			data_points = len(data)
			if (data_points % n_points == 0):
				time_s = time.time()
				print(f"{data_points} points, {n_points} in {time_s-last_n}")
				freq = n_points/(time_s-last_n)
				print(f"Giving a frequency of {freq} Hz")
				last_n = time.time()
				freqs.append(freq)


except KeyboardInterrupt:
	print("Quitting")
	m.set_leds([50, 255, 128], [50, 255, 128])
	m.disconnect()

	end_time = time.time()
	print(f"{len(data)} measurements in {end_time-start_time} seconds.")
	freq = len(data)/(end_time-start_time)
	print(f"Giving a frequency of {freq} Hz")
	print(f"Myo using raw={RAW}, filtered={FILTERED}.")

	if (PLOT):
		import numpy as np
		import matplotlib.pyplot as plt
		x_ticks = np.array(range(1, len(freqs)+1)) * n_points 
		plt.plot(x_ticks,freqs)
		plt.title("Myo Frequency Plot")
		plt.xlabel(f"Number of values sent, measured every {n_points}")
		plt.ylabel('Frequency')
		plt.show()