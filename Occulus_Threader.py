"""
This Script Manages Thread Overloard class wich controlls all image analyisis threads

Created By: CitizenX
Python 2.7
"""


#Importing Necisary moduals
import os
import threading
import time
import cv2

#Not needed yet but might
import datetime
import numpy as np

#Grab a que to better handle exclusive access
from Queue import Queue


#Thread class that watches Everything... Litterally
class OcculusOverloard(threading.Thread):

	#Deh constructor... Muhahaha
	def __init__(self, haarDetectInterval=1, ResRoot="res/", DefaultFilter="haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"):

		#Innitials As Thread
		threading.Thread.__init__(self)

		#Store Some Innit Variables
		self._haarDetectInterval = haarDetectInterval
		self.Resources_Root_Folder = ResRoot
		self._DefaultHaarFilter = ResRoot+DefaultFilter

		#Meh its a variable cause i wanted to see if i can auto scale sleeptime
		self._sleepTimeMain = 1

		#The Threads RunFlag
		self._Run_Flag = True

		#Stores Current DetectionThreads
		self._CurrentRunningThreads = []

		#Concurency and Effiecientcy stuff for haar detection threads
		self._CurrentHaarRecsLock = threading.Lock()  # IdK if i should declare this variable as "hidden" or not... =/
		self._haarCurrentRects = ([], 0)
		self._haarCounter = 0

		#The Filter Flag for determine har filter validity and the current haarXML file
		self._CurrentHaarXML = None
		self._haarRecFilterFlag = False

		#Thread Printer Managment
		self._ToBePrinted = Queue()
		self._PrintLock = threading.Lock()  # Dont think ill need this... but will see

	def newFilter(self, filename):

		#Check if passed filename is valid
		if os.path.isfile(filename):

			self._haarRecFilterFlag = (True, filename)
			self._CurrentHaarXML = filename

		#else notify user and my use default file
		elif os.path.isfile(self._DefaultHaarFilter):
			self._ToBePrinted.put("WOOPC Something woonkie happened with your haar filter selection...\nhad to default to: "+self._DefaultHaarFilter)
			self._haarRecFilterFlag = (True, self._DefaultHaarFilter)

		#else notify user and my use default file
		else:
			self._ToBePrinted.put("UH-OH... Something realy bad has happend, no default haar filter either")
			self._haarRecFilterFlag = (False, None)
			self._CurrentHaarXML = None

		#Pull in the cascade feature template we want to use
		try:
			self.cascade = cv2.CascadeClassifier(self._haarRecFilterFlag[1])
		except Exception, e:
			self._haarRecFilterFlag = (False, e)

		return self._haarRecFilterFlag

	def addFrame4Haar(self, img):

		#Checks To see if you have Actual Filter Loaded in
		if self._haarRecFilterFlag[0]:

			#Little salt and pepper i added for low power machines
			if self._haarCounter % self._haarDetectInterval == 0:

				#Create New Detection Thread
				threading.Thread(target=self._DetectionSubThread, args = (img.copy(), self._haarCounter)).start()  # Start the Thread....

			#Inc the Haar counter
			self._haarCounter += 1

	def getInfo(self):
		return threading.active_count(), self._sleepTimeMain

	#Used To Get Total Analysis
	def getLatestHaarAnalysis(self):

		#Creates a storage container
		returnRecs = []

		#Grab Key
		self._CurrentHaarRecsLock.acquire()

		#Throw latest in greatest... =)
		try:
			returnRecs = self._haarCurrentRects[0]

		finally:
			self._CurrentHaarRecsLock.release()

		#return the container
		return returnRecs

	def getCurrentHaarXML(self):
		return self._haarRecFilterFlag[1]

	def _DetectionSubThread(self, passed_img, haarCount):

		#Perform a simple blur before Haar Analysis
		passed_img = cv2.GaussianBlur(passed_img, (5, 5), 0)

		#Perform Haar Analysis
		rects = self.cascade.detectMultiScale(passed_img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20, 20))

		#If the list isnt empty do some formating and add it to master
		if not len(rects) == 0:
			rects[:, 2:] += rects[:, :2]

		self._CurrentHaarRecsLock.acquire()

		try:
			if(haarCount > self._haarCurrentRects[1]):
				self._haarCurrentRects = (rects, haarCount)

			else:
				self._ToBePrinted.put("Collision At HaarCount: "+str(haarCount))

		finally:
			self._CurrentHaarRecsLock.release()

	def stop(self):
		self._Run_Flag = False

	#yuuuuuuuuuuuuuuuuuuup.... the runner...
	def run(self):

		#Stay operational so long as the program is running
		while self._Run_Flag:

						#If There is something to be Printed Lock the array
			if self._ToBePrinted.empty():
				self._sleepTimeMain += 0.01
			else:
				if self._sleepTimeMain >= 0.01:
					self._sleepTimeMain -= 0.01

				#Print the first element of array
				print self._ToBePrinted.get()

			#else Sleep the Thread and wait....
			time.sleep(self._sleepTimeMain)
