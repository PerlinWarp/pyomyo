'''
pip install pyAudio may not work
Instead download and install a wheel from here:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

or use: 

pip install pipwin
pipwin install pyaudio

pipwin is like pip, but it installs precompiled Windows binaries provided by Christoph Gohlke.
'''

# to display in separate Tk window
import matplotlib
matplotlib.use('TkAgg')

import multiprocessing
import queue
import numpy as np

import pyaudio
import os
import struct
import matplotlib.pyplot as plt
from matplotlib import animation
from scipy.fftpack import fft
import time

from pyomyo import Myo, emg_mode

# Counts the frames
# why the list? https://stackoverflow.com/questions/25040323/unable-to-reference-one-particular-variable-declared-outside-a-function
count = [0]

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
	m = Myo(mode=emg_mode.PREPROCESSED)
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
		except:
			print("Worker Stopped")
			quit()

# ------------ Plot Setup ---------------
# ------------ Audio Setup ---------------
# constants
CHUNK = 1024                 # samples per frame
FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
CHANNELS = 1                 # single channel for microphone
RATE = 44100                 # samples per second
# Signal range is -32k to 32k
# limiting amplitude to +/- 4k
AMPLITUDE_LIMIT = 1000
freq = 50
QUEUE_SIZE = CHUNK
emg_queue = queue.Queue(QUEUE_SIZE)

fig, (ax1, ax2) = plt.subplots(2, figsize=(15, 7))
# variable for plotting
x = np.arange(0,QUEUE_SIZE)          # samples (waveform)
xf = np.linspace(0, RATE, CHUNK)     # frequencies (spectrum)

# create a line object with random data
line, = ax1.plot(x, np.random.rand(QUEUE_SIZE), '-', lw=2)

# create semilogx line for spectrum, to plot the waveform as log not lin
line_fft, = ax2.semilogx(xf, np.random.rand(CHUNK), '-', lw=2)

# format waveform axes
ax1.set_title('EMG Waveform')
ax1.set_xlabel('samples')
ax1.set_ylabel('Amplitude')
ax1.set_ylim(0, AMPLITUDE_LIMIT)
ax1.set_xlim(0, QUEUE_SIZE)
plt.setp(ax1, xticks=[0, CHUNK], yticks=[0, AMPLITUDE_LIMIT])

# format spectrum axes
ax2.set_xlim(20, RATE / 2)
print('stream started')

def on_close(evt):
	print("Closing")
	p.terminate()

	# calculate average frame rate
	frame_rate = count[0] / (time.time() - start_time)
	
	print('stream stopped')
	print('average frame rate = {:.0f} FPS'.format(frame_rate))
	raise KeyboardInterrupt	
	quit()


def animate(i):
	# Myo Plot
	while not(q.empty()):
		myox = list(q.get())

		print("EMG:", myox)
		if (emg_queue.full()):
			emg_queue.get()
		emg_queue.put(myox)

	channels = np.array(emg_queue.queue)

	if (emg_queue.full()):
		print("Started plot")
		ch = channels[:,0]
		print(ch.shape)
	else:
		# We dont have enough to fill the screen
		# Get some mock data
		ch = np.arange(0,QUEUE_SIZE-emg_queue.qsize())
		if (emg_queue.qsize() > 1):
			# Append the real data onto the end
			partial_queue = np.array(emg_queue.queue)[:,0]
			ch = np.append(ch, partial_queue)


	# Update the plotted line
	line.set_ydata(ch)
	# compute FFT and update line
	yf = fft(ch)
	# The fft will return complex numbers, so np.abs will return their magnitude
	line_fft.set_ydata(np.abs(yf[0:CHUNK])  / (512 * CHUNK))

	# Update the number of frames
	count[0] += 1

if __name__ == '__main__':
	# Start Myo Process
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	while(q.empty()):
		# Wait until we actually get data
		continue

	start_time = time.time()

	try:
		anim = animation.FuncAnimation(fig, animate, blit=False, interval=1)
		fig.canvas.mpl_connect('close_event',  on_close)
		plt.show()
	except KeyboardInterrupt:
		plt.close()
		p.close()
		quit()	