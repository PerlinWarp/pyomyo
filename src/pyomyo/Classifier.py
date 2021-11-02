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

from pyomyo import Myo, emg_mode

SUBSAMPLE = 3
K = 15

class Classifier(object):
	'''A wrapper for nearest-neighbor classifier that stores
	training data in vals0, ..., vals9.dat.'''

	def __init__(self, name="Classifier", color=(0,200,0)):
		# Add some identifiers to the classifier to identify what model was used in different screenshots
		self.name = name
		self.color = color

		for i in range(10):
			with open('data/vals%d.dat' % i, 'ab') as f: pass
		self.read_data()

	def store_data(self, cls, vals):
		with open('data/vals%d.dat' % cls, 'ab') as f:
			f.write(pack('8H', *vals))

		self.train(np.vstack([self.X, vals]), np.hstack([self.Y, [cls]]))

	def read_data(self):
		X = []
		Y = []
		for i in range(10):
			X.append(np.fromfile('data/vals%d.dat' % i, dtype=np.uint16).reshape((-1, 8)))
			Y.append(i + np.zeros(X[-1].shape[0]))

		self.train(np.vstack(X), np.hstack(Y))

	def delete_data(self):
		for i in range(10):
			with open('data/vals%d.dat' % i, 'wb') as f: pass
		self.read_data()

	def train(self, X, Y):
		self.X = X
		self.Y = Y
		self.model = None

	def nearest(self, d):
		dists = ((self.X - d)**2).sum(1)
		ind = dists.argmin()
		return self.Y[ind]

	def classify(self, d):
		if self.X.shape[0] < K * SUBSAMPLE: return 0
		return self.nearest(d)

class MyoClassifier(Myo):
	'''Adds higher-level pose classification and handling onto Myo.'''

	def __init__(self, cls, tty=None, mode=emg_mode.PREPROCESSED, hist_len=25):
		Myo.__init__(self, tty, mode=mode)
		# Add a classifier
		self.cls = cls
		self.hist_len = hist_len
		self.history = deque([0] * self.hist_len, self.hist_len)
		self.history_cnt = Counter(self.history)
		self.add_emg_handler(self.emg_handler)
		self.last_pose = None

		self.pose_handlers = []

	def emg_handler(self, emg, moving):
		y = self.cls.classify(emg)
		self.history_cnt[self.history[0]] -= 1
		self.history_cnt[y] += 1
		self.history.append(y)

		r, n = self.history_cnt.most_common(1)[0]
		if self.last_pose is None or (n > self.history_cnt[self.last_pose] + 5 and n > self.hist_len / 2):
			self.on_raw_pose(r)
			self.last_pose = r

	def add_raw_pose_handler(self, h):
		self.pose_handlers.append(h)

	def on_raw_pose(self, pose):
		for h in self.pose_handlers:
			h(pose)

	def run_gui(self, hnd, scr, font, w, h):
		# Handle keypresses
		for ev in pygame.event.get():
			if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
				raise KeyboardInterrupt()
			elif ev.type == KEYDOWN:
				if K_0 <= ev.key <= K_9:
					# Labelling using row of numbers
					hnd.recording = ev.key - K_0
				elif K_KP0 <= ev.key <= K_KP9:
					# Labelling using Keypad
					hnd.recording = ev.key - K_Kp0
				elif ev.unicode == 'r':
					hnd.cl.read_data()
				elif ev.unicode == 'e':
					print("Pressed e, erasing local data")
					self.cls.delete_data()
			elif ev.type == KEYUP:
				if K_0 <= ev.key <= K_9 or K_KP0 <= ev.key <= K_KP9:
					# Don't record incoming data
					hnd.recording = -1

		# Plotting
		scr.fill((0, 0, 0), (0, 0, w, h))
		r = self.history_cnt.most_common(1)[0][0]

		for i in range(10):
			x = 0
			y = 0 + 30 * i
			# Set the barplot color
			clr = self.cls.color if i == r else (255,255,255)

			txt = font.render('%5d' % (self.cls.Y == i).sum(), True, (255,255,255))
			scr.blit(txt, (x + 20, y))

			txt = font.render('%d' % i, True, clr)
			scr.blit(txt, (x + 110, y))

			# Plot the barchart plot
			scr.fill((0,0,0), (x+130, y + txt.get_height() / 2 - 10, len(self.history) * 20, 20))
			scr.fill(clr, (x+130, y + txt.get_height() / 2 - 10, self.history_cnt[i] * 20, 20))

		pygame.display.flip()

def pack(fmt, *args):
	return struct.pack('<' + fmt, *args)

def unpack(fmt, *args):
	return struct.unpack('<' + fmt, *args)

def text(scr, font, txt, pos, clr=(255,255,255)):
	scr.blit(font.render(txt, True, clr), pos)


class EMGHandler(object):
	def __init__(self, m):
		self.recording = -1
		self.m = m
		self.emg = (0,) * 8

	def __call__(self, emg, moving):
		self.emg = emg
		if self.recording >= 0:
			self.m.cls.store_data(self.recording, emg)

class Live_Classifier(Classifier):
	'''
	General class for all Sklearn classifiers
	Expects something you can call .fit and .predict on
	'''
	def __init__(self, classifier, name="Live Classifier", color=(0,55,175)):
		self.model = classifier
		Classifier.__init__(self, name=name, color=color)

	def train(self, X, Y):
		self.X = X
		self.Y = Y

		if self.X.shape[0] > 0 and self.Y.shape[0] > 0: 
			self.model.fit(self.X, self.Y)

	def classify(self, emg):
		if self.X.shape[0] == 0 or self.model == None:
			# We have no data or model, return 0
			return 0

		x = np.array(emg).reshape(1,-1)
		pred = self.model.predict(x)
		return int(pred[0])

if __name__ == '__main__':
	pygame.init()
	w, h = 800, 320
	scr = pygame.display.set_mode((w, h))
	font = pygame.font.Font(None, 30)

	m = MyoClassifier(Classifier())
	hnd = EMGHandler(m)
	m.add_emg_handler(hnd)
	m.connect()

	m.add_raw_pose_handler(print)

	# Set Myo LED color to model color
	m.set_leds(m.cls.color, m.cls.color)
	# Set pygame window name
	pygame.display.set_caption(m.cls.name)

	try:
		while True:
			m.run()
			m.run_gui(hnd, scr, font, w, h)

	except KeyboardInterrupt:
		pass
	finally:
		m.disconnect()
		print()
		pygame.quit()
