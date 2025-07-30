import multiprocessing
import queue
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.gridspec import GridSpec

from pyomyo import Myo, emg_mode

print("Press ctrl+pause/break to stop")

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
	m = Myo(mode=emg_mode.PREPROCESSED)
	m.connect()
	
	def add_to_queue(quat, acc, gyro):
		imu_data = acc + gyro  # Combine accelerometer and gyroscope data
		q.put(imu_data)

	def print_battery(bat):
			print("Battery level:", bat)

	# Purple logo and bar LEDs
	m.set_leds([128, 0, 255], [128, 0, 255])
	# Vibrate to know we connected
	m.vibrate(1)
	m.add_battery_handler(print_battery)
	m.add_imu_handler(add_to_queue)

	while True:
		try:
			m.run()
		except:
			print("Worker Stopped")
			quit()

# ------------ Plot Setup ---------------
QUEUE_SIZE = 100
SENSORS = 6  # 3 accelerometer + 3 gyroscope channels
CHANNEL_LABELS = ['X', 'Y', 'Z', 'X', 'Y', 'Z']
AXIS_COLORS = ['red', 'green', 'blue']  # X=red, Y=green, Z=blue
subplots = []
lines = []
# Set the size of the plot
plt.rcParams["figure.figsize"] = (12,12)
# Custom GridSpec for visual separation between accelerometer and gyroscope
gs = GridSpec(7, 1, height_ratios=[1, 1, 1, 0.5, 1, 1, 1], hspace=0.3)
fig = plt.figure()
fig.canvas.manager.set_window_title("6 Channel IMU plot (Accelerometer + Gyroscope)")

x_data = np.arange(QUEUE_SIZE)

# Create subplots manually with the custom grid
subplots = []
subplot_indices = [0, 1, 2, 4, 5, 6]  # Skip index 3 for empty space

for i, gs_idx in enumerate(subplot_indices):
	subplot = fig.add_subplot(gs[gs_idx])
	subplots.append(subplot)

# Create plots for each channel
for i in range(SENSORS):
	# Use axis colors: X=red, Y=green, Z=blue for all groups
	color = AXIS_COLORS[i % 3]
	ch_line, = subplots[i].plot(x_data, np.zeros(QUEUE_SIZE), color=color, linewidth=2)
	lines.append(ch_line)
	subplots[i].set_ylabel(CHANNEL_LABELS[i], fontweight='bold')
	subplots[i].grid(True, alpha=0.3)
	
	# Add titles to the first subplot of each group
	if i == 0:  # First accelerometer channel
		subplots[i].set_title('ACCELEROMETER', fontsize=16, fontweight='bold', pad=20)
	elif i == 3:  # First gyroscope channel
		subplots[i].set_title('GYROSCOPE', fontsize=16, fontweight='bold', pad=20)

fig.tight_layout()

from collections import deque
imu_deque = deque(maxlen=QUEUE_SIZE)

def animate(frame):
	# Process all available data from multiprocessing queue
	data_updated = False
	while not q.empty():
		imu_data = q.get()
		imu_deque.append(imu_data)
		data_updated = True
	
	# Only update plots if we have new data and sufficient data points
	if data_updated and len(imu_deque) >= QUEUE_SIZE:
		channels = np.array(imu_deque)
		
		for i in range(SENSORS):
			channel = channels[:, i]
			lines[i].set_ydata(channel)
			
			ch_min, ch_max = np.min(channel), np.max(channel)
			subplots[i].set_ylim(min(-2500, ch_min), max(2500, ch_max))

if __name__ == '__main__':
	# Start Myo Process
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	while q.empty():
		# Wait until we get data
		pass
	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2, cache_frame_data=False)
	
	def on_close(event):
		p.terminate()
		raise KeyboardInterrupt
	fig.canvas.mpl_connect('close_event', on_close)

	try:
		plt.show()
	except KeyboardInterrupt:
		plt.close()
		p.close()
		quit()