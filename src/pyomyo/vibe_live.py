import pygame
import multiprocessing
from pyomyo import Myo, emg_mode
import time

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
	m = Myo(mode=emg_mode.FILTERED)
	m.connect()

	# Orange logo and bar LEDs
	m.set_leds([128, 0, 0], [128, 0, 0])
	# Vibrate to know we connected okay
	m.vibrate(1)
	
	while True:
		while not(q.empty()):
			v = q.get()
			print("Queue", v)
			m.vibrate2(100, v)
			print(q.qsize())
			#time.sleep(1)
	print("Worker Stopped")

# -------- Main Program Loop -----------
if __name__ == "__main__":
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	pygame.init()

	# Set up the drawing window
	WINDOW_Y = 800
	MOUSE_DOWN = False
	screen = pygame.display.set_mode([300, WINDOW_Y])

	# Run until the user asks to quit
	running = True
	while running:

		# Did the user click the window close button?
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				p.terminate()
				running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				MOUSE_DOWN = True
				mouse_presses = pygame.mouse.get_pressed()
				if mouse_presses[0]:
					print("Left Mouse key was clicked")
			elif event.type == pygame.MOUSEBUTTONUP:
				MOUSE_DOWN = False
		# Fill the background with white
		screen.fill((255, 255, 255))

		# Draw a solid blue circle in the center
		(mouse_x,mouse_y) = pygame.mouse.get_pos()
		pygame.draw.circle(screen, (0, 0, 255), (mouse_x, mouse_y), 10)

		if MOUSE_DOWN:
			# Add vibration to queue
			q.put(((mouse_y*255))//WINDOW_Y)

		# Flip the display
		pygame.display.flip()

	# Done! Time to quit.
	pygame.quit()