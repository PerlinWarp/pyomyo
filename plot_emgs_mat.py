import multiprocessing
import mpl_toolkits.mplot3d as plt3d
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np

from myo_serial import MyoRaw

print("EPILEPSY WARNING")
print("The plot updates fast, press ctrl+c to stop")

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
	m = MyoRaw(raw=False, filtered=True)
	m.connect()
	
	def add_to_queue(emg, movement):
		q.put(emg)

	def print_battery(bat):
			print("Battery level:", bat)

	# Orange logo and bar LEDs
	m.set_leds([128, 0, 0], [128, 0, 0])
	# Vibrate to know we connected okay
	m.vibrate(1)
	m.add_battery_handler(print_battery)
	m.add_emg_handler(add_to_queue)

	"""worker function"""
	while True:
		try:
			m.run()
		except KeyboardInterrupt:
			print("Worker Stopped")
			quit()


# ------------ Plot Setup ---------------
fig = plt.figure()
axm = fig.add_subplot()

myox = [2048,128,128,128,128,128,128,128]
rects  = axm.bar(list(range(1,9)), myox)

def animate(i):
	myox = [128,128,128,128,128,128,128,128]

	# Myo Plot
	while not(q.empty()):
		myox = list(q.get())
		print(myox)
	
	for rect, yi in zip(rects, myox):
		rect.set_height(yi)

	return rects

def main():
	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
	try:
		plt.show()
	except KeyboardInterrupt:
		quit()

if __name__ == '__main__':
	# Start Myo Process
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	main()