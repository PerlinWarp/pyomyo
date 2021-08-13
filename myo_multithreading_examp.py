import multiprocessing
from myo_serial import MyoRaw

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
	m = MyoRaw(raw=False, filtered=True)
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