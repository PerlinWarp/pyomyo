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
from pyomyo.Classifier import Live_Classifier, MyoClassifier, EMGHandler

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


if __name__ == '__main__':
	pygame.init()
	w, h = 800, 320
	scr = pygame.display.set_mode((w, h))
	font = pygame.font.Font(None, 30)

	# SVM Example
	m = MyoClassifier(SVM_Classifier(), mode=emg_mode.PREPROCESSED)
	# Logistic Regression Example
	#m = MyoClassifier(LR_Classifier(), mode=emg_mode.PREPROCESSED)
	# Live classifier example
	#model = GaussianNB()
	#m = MyoClassifier(Live_Classifier(model, name="NB", color=(255,165,50)))

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
