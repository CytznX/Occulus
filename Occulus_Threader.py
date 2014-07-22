
import os
import threading
import time, datetime
import numpy as np
import cv2, cv

#Thread that watches Everything... Litterally
class OcculusOverloard(threading.Thread):

	#Deh constructor... Muhahaha
	def __init__(self, haarDetectInterval=1, ResRoot = "res/", DefaultFilter = "haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"):
		
		#Innitials As Thread
		threading.Thread.__init__(self)
		
		#Store Some Innit Variables
		self._haarDetectInterval = haarDetectInterval
		self.Resources_Root_Folder = ResRoot
		self._DefaultHaarFilter = ResRoot+DefaultFilter

		#Meh its a variable cause i wanted to see if i can auto scale sleeptime
		self._sleepTimeMain = 1
		self._sleepTimePrinter = 1

		#The Threads RunFlag
		self._Run_Flag = True

		#Stores Current DetectionThreads
		self._CurrentRunningThreads = []

		#Concurency and Effiecientcy stuff for haar detection threads
		self._CurrentHaarRecsLock = threading.Lock()#IdK if i should declare this variable as "hidden" or not... =/
		self._haarCurrentRects = ([],0)
		self._haarCounter = 0

		#The Filter Flag for determine har filter validity and the current haarXML file
		self._CurrentHaarXML = None
		self._haarRecFilterFlag = False

		#Thread Printer Managment
		self._ToBePrinted = []
		self._PrintLock = threading.Lock() #Dont think ill need this... but will see
		self._PrinterThread = threading.Thread(target=self._PrinterSubThread, args = ())
		self._PrinterThread.start()

	def newFilter(self, filename):

		#default haar Rec Directory
		if os.path.isfile(filename):

			self._haarRecFilterFlag = (True, None)
			self._haarRecogFilter = filename
			self._CurrentHaarXML = filename
		
		elif os.path.isfile(self.Resources_Root_Folder+"haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"):
			print "WOOPC Something woonkie happened with your haar filter selection...\nhad to default to: "+self.Resources_Root_Folder+"haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"
			self._haarRecFilterFlag = (True, None)
			self._haarRecogFilter = self._DefaultHaarFilter
		
		else :
			self._haarRecFilterFlag = (False, "File Doesnt Exist")
			self._CurrentHaarXML = None

		#Pull in the cascade feature template we want to use
		try:
			self.cascade = cv2.CascadeClassifier(self._haarRecogFilter)
		except Exception, e:
			self._haarRecFilterFlag = (False, e)

		return self._haarRecFilterFlag

	def addFrame4Haar(self, img):

		#Checks To see if you have Actual Filter Loaded in
		if self._haarRecFilterFlag[0]:

			#Little salt and pepper i added for low power machines
			if self._haarCounter%self._haarDetectInterval==0:

				#Create New Detection Thread
				t = threading.Thread(target=self._DetectionSubThread, args = (img.copy(), self._haarCounter))
				t.start() #Start the Thread....

				#Add the Thread to current watch list
				self._CurrentRunningThreads.append(t)

			#Inc the Haar counter
			self._haarCounter +=1

	def getInfo(self):
		return len(self._CurrentRunningThreads), self._sleepTimeMain

	def getLatestHaarAnalysis(self):
		
		returnRecs = []
		self._CurrentHaarRecsLock.acquire()

		try:
			returnRecs = self._haarCurrentRects[0]

		finally:
			self._CurrentHaarRecsLock.release()

		return returnRecs

	def getCurrentHaarXML(self):
		return self._CurrentHaarXML

	def _PrinterSubThread(self):
  
		#While Our Program is running
		while self._Run_Flag:

			#If There is something to be Printed Lock the array
			while not self._ToBePrinted == []:
	
				#Print the first element of array
				print self._ToBePrinted.pop(0)

			#else Sleep the Thread and wait....
			time.sleep(1)

	def _DetectionSubThread(self, passed_img, haarCount):

		#Perform a simple blur before Haar Analysis
		passed_img = cv2.GaussianBlur(passed_img, (5,5), 0)
	
		#Perform Haar Analysis
		rects = self.cascade.detectMultiScale(passed_img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))

		#If the list isnt empty do some formating and add it to master
		if not len(rects) == 0:
			rects[:, 2:] += rects[:, :2]

		self._CurrentHaarRecsLock.acquire()

		try:
			if(haarCount>self._haarCurrentRects[1]):
				self._haarCurrentRects = (rects, haarCount)

			else:
				self._ToBePrinted.append("Collision At HaarCount: "+str(haarCount))

		finally:
			self._CurrentHaarRecsLock.release()

	def stop(self):
		self._Run_Flag = False

	#yuuuuuuuuuuuuuuuuuuup.... the runner...
	def run(self):
		
		#Stay operational so long as the program is running
		while self._Run_Flag:

			#If the arrays empty wait sometime
			if self._CurrentRunningThreads == []:
				self._sleepTimeMain+=0.03
				time.sleep(self._sleepTimeMain)

			#Else I tend the flock
			else:

				#If the s
				if self._sleepTimeMain >= 0.01:
					self._sleepTimeMain-=0.01

				#Itterate through all availible threads
				for DetectionThreadM in self._CurrentRunningThreads:

					#If the Thread is dead... Remove it from List
					if not DetectionThreadM.isAlive():
						self._CurrentRunningThreads.remove(DetectionThreadM)

				#Go to sleep... <3 ... <3 ... <3
				time.sleep(self._sleepTimeMain)

		#When we want to quit the program iterate acrross all reamining running threads and call .join()
		for DetectionThreadM in self._CurrentRunningThreads:
			DetectionThreadM.join()

		self._PrinterThread.join()