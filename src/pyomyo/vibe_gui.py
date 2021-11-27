'''
To do, remove it from continuous send to a button based approach
can probably do it in a single thread
'''
import time
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

from pyomyo import Myo, emg_mode

RESET_SCALE = True
a0 = 128

# ------------ Myo Setup ---------------
q = multiprocessing.Array('i', range(6))

def worker(q):
	m = Myo(mode=emg_mode.PREPROCESSED)
	m.connect()
	# Orange logo and bar LEDs
	m.set_leds([128, 0, 128], [0, 128, 128])
	# Vibrate to know we connected okay
	m.vibrate(1)

	"""worker function"""
	while True:
		# Vibrate the Myo
		d = 1000
		amps = q[:]
		print("Queue", q[:])
		m.vibrate_six_array(d,amps)
		time.sleep(d/1000)
		m.run()

# ------------ Plot Setup ---------------
if __name__ == "__main__":
	# Start Myo Process
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()
	# ------------ Plot Setup ---------------
	fig = plt.figure("Vibration Waveform",figsize=(10, 10), dpi=100)

	# Slider setup
	axcolor = 'lightgoldenrodyellow'
	axamp = plt.axes([0.25, 0.30, 0.65, 0.03], facecolor=axcolor)
	ax_thumb = plt.axes([0.25, 0.25, 0.65, 0.03], facecolor=axcolor)
	ax_index = plt.axes([0.25, 0.20, 0.65, 0.03], facecolor=axcolor)
	ax_middle = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)
	ax_ring = plt.axes([0.25, 0.10, 0.65, 0.03], facecolor=axcolor)
	ax_pinky = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)
	# Add the sliders
	samp = Slider(axamp, '1', 0, 255, valinit=a0)
	sthumb = Slider(ax_thumb, '2', 0, 255, valinit=a0)
	sindex = Slider(ax_index, '3', 0, 255, valinit=a0)
	smiddle = Slider(ax_middle, '4', 0, 255, valinit=a0)
	sring = Slider(ax_ring, '5', 0, 255, valinit=a0)
	spinky = Slider(ax_pinky, '6', 0, 255, valinit=a0)

	def update(val):
		# Read the sliders
		amps = [int(samp.val), int(sthumb.val), int(sindex.val), int(smiddle.val), int(sring.val), int(spinky.val)]
		for i in range(0,6):
			q[i] = amps[i]
		print(amps)

		fig.canvas.draw_idle()

	samp.on_changed(update)
	sthumb.on_changed(update)
	sindex.on_changed(update)
	smiddle.on_changed(update)
	sring.on_changed(update)
	spinky.on_changed(update)

	plt.show()
