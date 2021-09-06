# SpeedTest
import time
import multiprocessing

from pyomyo import Myo, emg_mode

PLOT = True
MODE = emg_mode.PREPROCESSED

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
	m = Myo(mode=MODE)
	m.connect()
	#print(f"Connected to Myo using {MODE}.")

	def add_to_queue(emg, movement):
		q.put(emg)

	m.add_emg_handler(add_to_queue)

	while True:
		try:
			m.run()
		except KeyboardInterrupt:
			print("Quitting")
			m.set_leds([50, 255, 128], [50, 255, 128])
			m.disconnect()

# -------- Main Program Loop -----------
if __name__ == "__main__":
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	data = []
	n_points = 50
	freqs = []

	start_time = time.time()
	last_n = start_time

	try:
		while True:
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
		end_time = time.time()
		print(f"{len(data)} measurements in {end_time-start_time} seconds.")
		freq = len(data)/(end_time-start_time)
		print(f"Giving a frequency of {freq} Hz")
		print(f"Myo using mode {MODE}.")

		if (PLOT):
			import numpy as np
			import matplotlib.pyplot as plt
			x_ticks = np.array(range(1, len(freqs)+1)) * n_points 
			plt.plot(x_ticks,freqs)
			plt.title("Myo Frequency Plot")
			plt.xlabel(f"Number of values sent, measured every {n_points}")
			plt.ylabel('Frequency')
			plt.show()