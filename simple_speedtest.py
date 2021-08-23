# SpeedTest
import time
import pygame
import multiprocessing

from myo_serial import MyoRaw

pygame.init()
 
carryOn = True

# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

m = MyoRaw(raw=False, filtered=True)
m.connect()

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
start_time = time.time()

try:
	while carryOn:
		while not(q.empty()):
			# Get the new data from the Myo queue
			emg = list(q.get())
			data.append(emg)
			print(len(data))
except KeyboardInterrupt:
	print("Quitting")
	m.set_leds([50, 255, 128], [50, 255, 128])
	m.disconnect()

	end_time = time.time()
	print(f"{len(data)} measurements in {end_time-start_time} seconds.")
	freq = len(data)/(end_time-start_time)
	print(f"Giving a frequency of {freq} Hz")
	quit()