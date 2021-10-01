'''
Instructions:
1. Run python dino_jump.py - This launches the training tool.
2. Click on the pygame window thats opened to make sure windows sends the keypresses to that process.
3. Relax the Myo arm, and with your other hand press 0 - This labels the incoming data as class 0
4. Make a fist with your hand and press 1, to label the fist as 1.
5. Try making a closed and open fist and watching the bars change.
6. Once you've gathered enough data, exit the pygame window. This saves the data in data/vals0.dat and vals1.dat
7. If you make a mistake and wrongly classify data, delete vals0 and vals1 and regather
8. If your happy it works, change TRAINING_MODE to False.
9. Goto https://trex-runner.com/ and rerun dino_jump.py with TRAINING_MODE set to false.
10. Click in the brower to start the game and tell windows to send keypresses there
11. Try making a fist and seeing if the dino jumps

If it doesn't work, feel free to let me know in the discord: 
https://discord.com/invite/mG58PVyk83

- PerlinWarp
'''


import sys
sys.path.append('../')

import pygame
from pygame.locals import *
from pynput.keyboard import Key, Controller
from pyomyo import Myo, emg_mode
import pyomyo.simple_classifier as sc

TRAINING_MODE = True

def dino_handler(pose):
	print("Pose detected", pose)
	if ((pose == 1) and (TRAINING_MODE == False)):
		for i in range(0,10):
			# Press and release space
			keyboard.press(Key.space)
			keyboard.release(Key.space)


if __name__ == '__main__':
	keyboard = Controller()

	pygame.init()
	w, h = 800, 320
	scr = pygame.display.set_mode((w, h))
	font = pygame.font.Font(None, 30)

	m = sc.MyoClassifier(sc.Classifier())
	hnd = sc.EMGHandler(m)
	m.add_emg_handler(hnd)
	m.connect()

	m.add_raw_pose_handler(dino_handler)

	try:
		while True:
			m.run()

			r = m.history_cnt.most_common(1)[0][0]

			for ev in pygame.event.get():
				if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
					raise KeyboardInterrupt()
				elif ev.type == KEYDOWN:
					if K_0 <= ev.key <= K_9:
						hnd.recording = ev.key - K_0
					elif K_KP0 <= ev.key <= K_KP9:
						hnd.recording = ev.key - K_Kp0
					elif ev.unicode == 'r':
						hnd.cl.read_data()
				elif ev.type == KEYUP:
					if K_0 <= ev.key <= K_9 or K_KP0 <= ev.key <= K_KP9:
						hnd.recording = -1

			scr.fill((0, 0, 0), (0, 0, w, h))

			for i in range(10):
				x = 0
				y = 0 + 30 * i

				clr = (0,200,0) if i == r else (255,255,255)

				txt = font.render('%5d' % (m.cls.Y == i).sum(), True, (255,255,255))
				scr.blit(txt, (x + 20, y))

				txt = font.render('%d' % i, True, clr)
				scr.blit(txt, (x + 110, y))


				scr.fill((0,0,0), (x+130, y + txt.get_height() / 2 - 10, len(m.history) * 20, 20))
				scr.fill(clr, (x+130, y + txt.get_height() / 2 - 10, m.history_cnt[i] * 20, 20))

			pygame.display.flip()

	except KeyboardInterrupt:
		pass
	finally:
		m.disconnect()
		print()
		pygame.quit()