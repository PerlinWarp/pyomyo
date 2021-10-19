'''
The MIT License (MIT)
Copyright (c) 2020 PerlinWarp
Copyright (c) 2014 Danny Zhu

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from collections import Counter, deque
import struct
import sys
import time

import pygame
from pygame.locals import *
import numpy as np
from sklearn import neighbors

from pyomyo import Myo, emg_mode
from pyomyo.Classifier import Classifier, MyoClassifier, EMGHandler

SUBSAMPLE = 3
K = 15

class KNN_Classifier(Classifier):
	'''Live implimentation of SkLearns KNN'''

	def __init__(self):
		Classifier.__init__(self)

	def train(self, X, Y):
		self.X = X
		self.Y = Y
		self.model = None
		if self.X.shape[0] >= K * SUBSAMPLE:
			self.model = neighbors.KNeighborsClassifier(n_neighbors=K, algorithm='kd_tree')
			self.model.fit(self.X[::SUBSAMPLE], self.Y[::SUBSAMPLE])

	def classify(self, emg):
		x = np.array(emg).reshape(1,-1)
		if self.X.shape[0] < K * SUBSAMPLE: 
			return 0

		pred = self.model.predict(x)
		return int(pred[0])

def text(scr, font, txt, pos, clr=(255,255,255)):
	scr.blit(font.render(txt, True, clr), pos)

if __name__ == '__main__':
	pygame.init()
	w, h = 800, 320
	scr = pygame.display.set_mode((w, h))
	font = pygame.font.Font(None, 30)

	m = MyoClassifier(KNN_Classifier(), mode=emg_mode.PREPROCESSED)
	hnd = EMGHandler(m)
	m.add_emg_handler(hnd)
	m.connect()

	m.add_raw_pose_handler(print)

	try:
		while True:
			m.run()

			r = m.history_cnt.most_common(1)[0][0]

			# Handle keypresses
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
					elif ev.unicode == 'e':
						print("Pressed e, erasing local data")
						m.cls.delete_data()
				elif ev.type == KEYUP:
					if K_0 <= ev.key <= K_9 or K_KP0 <= ev.key <= K_KP9:
						hnd.recording = -1

			# Plotting
			scr.fill((0, 0, 0), (0, 0, w, h))

			for i in range(10):
				x = 0
				y = 0 + 30 * i

				clr = (0,200,0) if i == r else (255,255,255)

				txt = font.render('%5d' % (m.cls.Y == i).sum(), True, (255,255,255))
				scr.blit(txt, (x + 20, y))

				txt = font.render('%d' % i, True, clr)
				scr.blit(txt, (x + 110, y))

				# Plot the history of predicitons
				scr.fill((0,0,0), (x+130, y + txt.get_height() / 2 - 10, len(m.history) * 20, 20))
				scr.fill(clr, (x+130, y + txt.get_height() / 2 - 10, m.history_cnt[i] * 20, 20))

				if m.cls.model is not None:
					print("emg", hnd.emg)
					x = np.array(hnd.emg).reshape(1,-1)
					dists, inds = m.cls.model.kneighbors(x)
					for i, (d, ind) in enumerate(zip(dists[0], inds[0])):
						y = m.cls.Y[SUBSAMPLE*ind]
						print("y", y)
						text(scr, font, '%d %6d' % (y, d), (650, 20 * i))


			pygame.display.flip()

	except KeyboardInterrupt:
		pass
	finally:
		m.disconnect()
		print()
		pygame.quit()
