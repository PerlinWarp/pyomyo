import multiprocessing
from pyomyo import Myo, emg_mode
import time

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
	m = Myo(mode=emg_mode.FILTERED)
	m.connect()
	
	def print_battery(bat):
		print("Battery level:", bat)

	m.add_battery_handler(print_battery)

	 # Orange logo and bar LEDs
	m.set_leds([255, 255, 0], [128, 0, 0])
	# Vibrate to know we connected okay
	m.vibrate(1)
	time.sleep(0.05)

	# m.vibrate_ds(600, 128)
	# time.sleep(0.05)
	# m.vibrate_ds(600, 255)
	# time.sleep(0.05)
	# m.vibrate_ds(600, 128)
	# time.sleep(0.05)
	# m.vibrate_ds(600, 64)

	# m.vibrate(1)
	# time.sleep(0.05)
	# #m.run()

	s = [128,20,30,80,50,255]
	d = 1000
	m.vibrate_six_array(d,s)

	# time.sleep(0.01)
	# for i in range(0,10):
	# 	time.sleep(0.01)
	# 	#m.vibrate2(1,i)
	# m.run()
	# time.sleep(1)
	# print("aaa")

	"""worker function"""
	while True:
	 	m.run()
	print("Worker Stopped")

# -------- Main Program Loop -----------
if __name__ == "__main__":
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	try:
		while True:
			while not(q.empty()):
				emg = list(q.get())
				print(emg)

	except KeyboardInterrupt:
		print("Quitting")
		quit()