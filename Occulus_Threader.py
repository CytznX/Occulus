"""
This Script Manages Thread Overloard class wich controlls all image analyisis threads

Created By: CitizenX
Python 2.7
"""


#Importing Necisary moduals
import os
import threading
import time
import datetime
import cv2
import Occulus_ToolBox


#Not needed yet but might
import numpy as np

#Grab a que to better handle exclusive access
from Queue import Queue


#Thread class that watches Everything... Litterally
class OcculusOverloard(threading.Thread):

	#Deh constructor... Muhahaha
	def __init__(self, ResRoot="res/", DefaultFilter="haarFilter_Face_Basic/haarcascade_frontalface_alt.xml", HaarThread=False, MotionThread=False):

		#Innitials As Thread
		threading.Thread.__init__(self)

		#Store Some Innit Variables
		self.Resources_Root_Folder = ResRoot
		self._DefaultHaarFilter = ResRoot+DefaultFilter

		#Meh its a variable cause i wanted to see if i can auto scale sleeptime
		self._sleepTimeMain = 1

		#The Threads RunFlag
		self._Run_Flag = True

		#Stores Current DetectionThreads
		self._CurrentRunningThreads = []

		#Concurency and Effiecientcy stuff for haar detection threads
		self._CurrentHaarRecsLock = threading.Lock()
		self._haarCurrentRects = []

		#The Filter Flag for determine har filter validity and the current haarXML file
		self._haarRecFilterFlag = (False, None)

		#Haar analysis flag to add thread
		self._addHaarThread = HaarThread

		#Motion analysis flag to add thread
		self.addMotionThread = MotionThread

		#Cascade variable for haar analysis
		self._cascade = None

		#sets up location for storing motion images
		self._motionImageQue = (None, None, None)
		self._motionOutput = None
		self._motionOutputLock = threading.Lock()

		#Thread Printer Managment
		self._ToBePrinted = Queue()
		self._PrintLock = threading.Lock()  # Dont think ill need this... but will see

	def setFlags(self, HaarFlag, MotionFlag):
		self._addHaarThread = HaarFlag
		self.addMotionThread = MotionFlag

	def newFilter(self, filename):

		#Check if passed filename is valid
		if os.path.isfile(filename):
			self._haarRecFilterFlag = (True, filename)

		#else notify user and my use default file
		elif os.path.isfile(self._DefaultHaarFilter):
			self._ToBePrinted.put("WOOPC Something woonkie happened with your haar filter selection...\nhad to default to: "+self._DefaultHaarFilter)
			self._haarRecFilterFlag = (True, self._DefaultHaarFilter)

		#else notify user and my use default file
		else:
			self._ToBePrinted.put("UH-OH... Something realy bad has happend, no default haar filter either")
			self._haarRecFilterFlag = (False, None)

		#Pull in the cascade feature template we want to use
		try:
			self._cascade = cv2.CascadeClassifier(self._haarRecFilterFlag[1])
		except Exception, e:
			self._haarRecFilterFlag = (False, e)

		return self._haarRecFilterFlag

	def addFrame(self, img):

		#Checks To see if you have Actual Filter Loaded in
		if self._haarRecFilterFlag[0] and self._addHaarThread:

			#Create New Detection Thread
			threading.Thread(target=self._HaarDetectionSubThread, args=(img.copy(), self._cascade)).start()  # Start the Thread....

		#checks Motion analysis flag to add thread
		if self.addMotionThread:

			#Create Motion Thread
			threading.Thread(target=self._MotionDetectionSubThread, args=(img.copy(),)).start()  # Start the Thread....

	def getInfo(self):
		return threading.active_count(), self._sleepTimeMain

	#Used To Get Motion Analysis
	def getLatestMotionAnalysis(self, frames=False):
		if frames:
			return self._motionOutput, self._motionImageQue
		else:
			return self._motionOutput

	#Used To Get Haar Analysis
	def getLatestHaarAnalysis(self):

		#Creates a storage container
		returnRecs = []

		#Grab Key
		self._CurrentHaarRecsLock.acquire()

		#Throw latest in greatest... =)
		try:
			returnRecs = self._haarCurrentRects
			self._haarCurrentRects = []

		finally:
			self._CurrentHaarRecsLock.release()

		#Debug
		#self._ToBePrinted.put("RR Len: " + str(len(returnRecs)))

		#return the container
		return returnRecs

	def getCurrentHaarXML(self):
		return self._haarRecFilterFlag[1]

	def _HaarDetectionSubThread(self, passed_img, cascade):

		#Perform a simple blur before Haar Analysis
		passed_img = cv2.GaussianBlur(passed_img, (5, 5), 0)

		#Perform Haar Analysis
		rects = cascade.detectMultiScale(passed_img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20, 20))

		#If the list isnt empty do some formating and add it to master
		if not len(rects) == 0:
			rects[:, 2:] += rects[:, :2]
		else:
			rects = []

		#Aquire The Lock and do our bizzz
		self._CurrentHaarRecsLock.acquire()
		try:
			self._haarCurrentRects.append(rects)
		finally:
			self._CurrentHaarRecsLock.release()

	#Thread that calculates motion Image
	def _MotionDetectionSubThread(self, passed_img):

		self._motionImageQue = (cv2.cvtColor(passed_img, cv2.COLOR_RGB2GRAY), self._motionImageQue[0], self._motionImageQue[1])

		if not (self._motionImageQue[0] is None or self._motionImageQue[1] is None or self._motionImageQue[2] is None):

			#Record When anaylsis took places
			_TimeOfFram = datetime.datetime.now()

			#Find a motion picture
			_motionPic = Occulus_ToolBox.diffImg(self._motionImageQue[0], self._motionImageQue[1], self._motionImageQue[2])

			#grean the mean and standard deviation of the "Motion" pic
			_mean, _deviation = cv2.meanStdDev(_motionPic)
			_mean = sum(_mean)
			_deviation = sum(_deviation)

			#if some were the most current analysisis upload to main
			if(self._motionOutput is None or _TimeOfFram > self._motionOutput[2]):
				self._motionOutputLock.acquire()
				self._motionOutput = (_mean, _deviation, _TimeOfFram)
				self._motionOutputLock.release()

#If we want to kill the threader
	def stop(self):
		self._Run_Flag = False

	#yuuuuuuuuuuuuuuuuuuup.... the runner...
	def run(self):

		#Stay operational so long as the program is running
		while self._Run_Flag:

						#If There is something to be Printed Lock the array
			if self._ToBePrinted.empty():
				self._sleepTimeMain += 0.1
			else:
				if self._sleepTimeMain >= 0.1:
					self._sleepTimeMain -= 0.1

				#Print the first element of array
				print self._ToBePrinted.get()

			#else Sleep the Thread and wait....
			time.sleep(self._sleepTimeMain)
