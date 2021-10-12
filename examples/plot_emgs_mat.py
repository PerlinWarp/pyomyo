import multiprocessing
import queue
import numpy as np
import mpl_toolkits.mplot3d as plt3d
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.cm import get_cmap

from pyomyo import Myo, emg_mode

print("Press ctrl+pause/break to stop")

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
QUEUE_SIZE = 100
SENSORS = 8
subplots = []
lines = []
# Set the size of the plot
plt.rcParams["figure.figsize"] = (4,8)
# using the variable axs for multiple Axes
fig, subplots = plt.subplots(SENSORS, 1)
fig.canvas.manager.set_window_title("8 Channel EMG plot")
fig.tight_layout()
# Set each line to a different color

name = "tab10" # Change this if you have sensors > 10
cmap = get_cmap(name)  # type: matplotlib.colors.ListedColormap
colors = cmap.colors  # type: list

for i in range(0,SENSORS):
	ch_line,  = subplots[i].plot(range(QUEUE_SIZE),[0]*(QUEUE_SIZE), color=colors[i])
	lines.append(ch_line)

emg_queue = queue.Queue(QUEUE_SIZE)

def animate(i):
	# Myo Plot
	while not(q.empty()):
		myox = list(q.get())
		if (emg_queue.full()):
			emg_queue.get()
		emg_queue.put(myox)

	channels = np.array(emg_queue.queue)

	if (emg_queue.full()):
		for i in range(0,SENSORS):
			channel = channels[:,i]
			lines[i].set_ydata(channel)
			subplots[i].set_ylim(0,max(1024,max(channel)))

if __name__ == '__main__':
	# Start Myo Process
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	while(q.empty()):
		# Wait until we actually get data
		continue
	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
	def on_close(event):
		p.terminate()
		raise KeyboardInterrupt
		print("On close has ran")
	fig.canvas.mpl_connect('close_event', on_close)

	try:
		plt.show()
	except KeyboardInterrupt:
		plt.close()
		p.close()
		quit()