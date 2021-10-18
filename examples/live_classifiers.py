from collections import Counter, deque
import struct
import sys
import time

import pygame
from pygame.locals import *
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from sklearn.naive_bayes import GaussianNB

from pyomyo import Myo, emg_mode
from simple_classifier import Classifier, MyoClassifier, EMGHandler

class Live_Classifier(Classifier):
	'''
	General class for all Sklearn classifiers
	Expects something you can call .fit and .predict on
	'''
	def __init__(self, classifier, name="Live Classifier", color=(0,55,175)):
		self.model = classifier
		# Add some identifiers to the classifier to identify what model was used in different screenshots
		self.name = name
		self.color = color
		Classifier.__init__(self)

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

class SVM_Classifier(Live_Classifier):
	'''
	Live implimentation of an SVM Classifier
	'''
	def __init__(self):
		Live_Classifier.__init__(self, None, "SVM", (100,0,100))

	def train(self, X, Y):
		self.X = X
		self.Y = Y
		try:
			if self.X.shape[0] > 0: 
				clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))
				#clf = make_pipeline(StandardScaler(), SVC(kernel="linear", C=0.025))

				clf.fit(self.X, self.Y)
				self.model = clf
		except:
			# SVM Errors when we only have data for 1 class.
			self.model = None

	def classify(self, emg):
		if self.X.shape[0] == 0 or self.model == None:
			# We have no data or model, return 0
			return 0

		x = np.array(emg).reshape(1,-1)
		pred = self.model.predict(x)
		return int(pred[0])


class DC_Classifier(Live_Classifier):
	'''
	Live implimentation of Decision Trees
	'''
	def __init__(self):
		Live_Classifier.__init__(self, DecisionTreeClassifier(), name="DC_Classifier", color=(212,175,55))

class XG_Classifier(Live_Classifier):
	'''
	Live implimentation of XGBoost
	'''
	def __init__(self):
		Live_Classifier.__init__(self, XGBClassifier(), name="xgboost", color=(0,150,150))

class LR_Classifier(Live_Classifier):
	'''
	Live implimentation of Logistic Regression
	'''
	def __init__(self):
		Live_Classifier.__init__(self, None, name="LR", color=(100,0,100))

	def train(self, X, Y):
		self.X = X
		self.Y = Y
		try:
			if self.X.shape[0] > 0: 
				self.model = LogisticRegression()
				self.model.fit(self.X, self.Y)
		except:
			# LR Errors when we only have data for 1 class.
			self.model = None

	def classify(self, emg):
		if self.X.shape[0] == 0 or self.model == None:
			# We have no data or model, return 0
			return 0

		x = np.array(emg).reshape(1,-1)
		pred = self.model.predict(x)
		return int(pred[0])


def text(scr, font, txt, pos, clr=(255,255,255)):
	scr.blit(font.render(txt, True, clr), pos)

if __name__ == '__main__':
	pygame.init()
	w, h = 800, 320
	scr = pygame.display.set_mode((w, h))
	font = pygame.font.Font(None, 30)

	#m = MyoClassifier(SVM_Classifier(), mode=emg_mode.PREPROCESSED)
	#m = MyoClassifier(LR_Classifier(), mode=emg_mode.PREPROCESSED)
	# Live classifier example
	model = GaussianNB()
	m = MyoClassifier(Live_Classifier(model, name="NB", color=(50,0,50)))

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

			r = m.history_cnt.most_common(1)[0][0]

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
						m.cls.delete_data()
				elif ev.type == KEYUP:
					if K_0 <= ev.key <= K_9 or K_KP0 <= ev.key <= K_KP9:
						# Don't record incoming data
						hnd.recording = -1

			# Plotting
			scr.fill((0, 0, 0), (0, 0, w, h))

			for i in range(10):
				x = 0
				y = 0 + 30 * i
				# Set the barplot color
				clr = m.cls.color if i == r else (255,255,255)

				txt = font.render('%5d' % (m.cls.Y == i).sum(), True, (255,255,255))
				scr.blit(txt, (x + 20, y))

				txt = font.render('%d' % i, True, clr)
				scr.blit(txt, (x + 110, y))

				# Plot the barchart plot
				scr.fill((0,0,0), (x+130, y + txt.get_height() / 2 - 10, len(m.history) * 20, 20))
				scr.fill(clr, (x+130, y + txt.get_height() / 2 - 10, m.history_cnt[i] * 20, 20))

			pygame.display.flip()

	except KeyboardInterrupt:
		pass
	finally:
		m.disconnect()
		print()
		pygame.quit()
