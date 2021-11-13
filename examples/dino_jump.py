'''
Instructions:
0. Install pynput and XGboost e.g. pip install pynput xgboost
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

import pygame
from pygame.locals import *
from pynput.keyboard import Key, Controller
from pyomyo import Myo, emg_mode
from pyomyo.Classifier import Live_Classifier, MyoClassifier, EMGHandler
from xgboost import XGBClassifier

TRAINING_MODE = False

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

	# Make an ML Model to train and test with live
	# XGBoost Classifier Example
	model = XGBClassifier(eval_metric='logloss')
	clr = Live_Classifier(model, name="XG", color=(50,50,255))
	m = MyoClassifier(clr, mode=emg_mode.PREPROCESSED, hist_len=10)

	hnd = EMGHandler(m)
	m.add_emg_handler(hnd)
	m.connect()

	m.add_raw_pose_handler(dino_handler)

	# Set Myo LED color to model color
	m.set_leds(m.cls.color, m.cls.color)
	# Set pygame window name
	pygame.display.set_caption(m.cls.name)

	try:
		while True:
			# Run the Myo, get more data
			m.run()
			# Run the classifier GUI
			m.run_gui(hnd, scr, font, w, h)			

	except KeyboardInterrupt:
		pass
	finally:
		m.disconnect()
		print()
		pygame.quit()