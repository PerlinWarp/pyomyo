import multiprocessing
from pyomyo import Myo, emg_mode
import os

def cls():
	# Clear the screen in a cross platform way
	# https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
    os.system('cls' if os.name=='nt' else 'clear')

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
	m = Myo(mode=emg_mode.FILTERED)
	m.connect()
	
	def add_to_queue(quat, acc, gyro):
		imu_data = [quat, acc, gyro]
		q.put(imu_data)

	m.add_imu_handler(add_to_queue)
	
	# Orange logo and bar LEDs
	m.set_leds([128, 128, 0], [128, 128, 0])
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
				imu = list(q.get())
				quat, acc, gyro = imu
				print("Quaternions:", quat)
				print("Acceleration:", acc)
				print("Gyroscope:", gyro)
				cls()

	except KeyboardInterrupt:
		print("Quitting")
		quit()