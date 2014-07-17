"""
pyClass I use for testing and recording some image analysis filters

Created By: Citizenx
"""

#Some 
import time, datetime
import os
import numpy as np
import cv2, cv

import threading

from Tkinter import Tk
from tkFileDialog import askopenfilename
from tkFileDialog import askdirectory

class OculusMaximus():

	def __init__(self, showOutput = True, haarDetectInterval = 2):

		#Capture Some Initialization
		self._showOutput = showOutput
		self._haarDetectInterval = haarDetectInterval

		#Some Default Resoure Folder Stuff
		self.Videos_Root_Folder = "vid/"
		self.Images_Root_Folder = "img/"
		self.Resources_Root_Folder = "res/"

		self.DispImageLock = threading.Lock()
		self.CurrentHaarRecsLock = threading.Lock()

		#Keeps Track of Current Haar Wavelet
		self._CurrentHaarXML = self.Resources_Root_Folder+"haarFilter_Face_Basic/"

		#Check to see if record directorys exists
		for checkDirectory in [ self.Videos_Root_Folder, self.Images_Root_Folder, self.Resources_Root_Folder]:
			if not os.path.isdir(checkDirectory):
				os.makedirs(checkDirectory)
				print "No "+checkDirectory+" Directory... EmptyOne Created"

		#Sets some initial class Flag Variables & Counters
		self._haarDetect_Flag = False
		self._haarMulti_Flag = False
		self._haarCounter = 0
		self._haarCurrentRects = []

		self._Run_Flag = True
		self._RecordVideo = False
		
		#Variable to keep track of last image capture
		self._LastImageCapture = datetime.datetime.now()		

		#Heres how i create those file viewer dialog boxes
		Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
		filename =  askopenfilename(initialdir = self._CurrentHaarXML)# show an "Open" dialog box and return the path to the selected file
		
		#default haar Rec Directory
		if os.path.isfile(filename):

			self._haarRecFilterFlag = (True, None)
			self._haarRecogFilter = filename
			self._CurrentHaarXML = filename
		
		elif os.path.isfile(self.Resources_Root_Folder+"haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"):
			print "WOOPC Something woonkie happened with your haar filter selection...\nhad to default to: "+self.Resources_Root_Folder+"haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"
			self._haarRecFilterFlag = (True, None)
			self._haarRecogFilter = self.Resources_Root_Folder+"haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"
		
		else :
			self._haarRecFilterFlag = (False, "File Doesnt Exist")

		#Pull in the cascade feature template we want to use
		try:
			self.cascade = cv2.CascadeClassifier(self._haarRecogFilter)
		except Exception, e:
			self._haarRecFilterFlag = (False, e)


		#Create the Video Interfaces
		self._MainCaptureIterFace = cv2.VideoCapture(0)
		

	def RunDetectionThread(self, orig_img, output_img):

		orig_img = cv2.GaussianBlur(orig_img, (5,5), 0)
	
		if self._haarCounter%self._haarDetectInterval==0:
			tempRecs, img = self.haarDetect(orig_img)

			self.CurrentHaarRecsLock.acquire()
			try:
				self._haarCurrentRects = tempRecs
			finally:
				self.CurrentHaarRecsLock.release()

	def haarDetect(self, img):
	    rects = self.cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))

	    if len(rects) == 0:
	        return [], img
	    rects[:, 2:] += rects[:, :2]
	    return rects, img

	#Draw Rectangles on a image
	def box(self, rects, img):
		for x1, y1, x2, y2 in rects:
			cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
	

	#NOT DONE YET
	def compare(self, rects, img):
		crop_img = img[y1:y2, x1:x2, :] 
		
	def run(self):

		#Check If i want output shown
		if self._showOutput:
			cv2.namedWindow("OutPut "+str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)))+" "
							+str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)))) #Create The Output Window

		#Initializ some counter variables 
		_vidcount = 0
		_imgcount = 0

		#Variable used to store open Output video file reference
		_videoOut = None


		currentCaptureTime = datetime.datetime.now()

		while(self._Run_Flag):

			#Capture New Frame and record when you did it
			_,orig_img = self._MainCaptureIterFace.read()
			currentCaptureTime = datetime.datetime.now()
			currentFPS = 1.0/(currentCaptureTime-self._LastImageCapture).total_seconds()

			self._LastImageCapture = currentCaptureTime

			#Flip the image so its mirrored and make a copy to be used later
			orig_img = cv2.flip(orig_img, 1)
			output_img = orig_img.copy()

			if (self._haarDetect_Flag == True):
				t = threading.Thread(target=self.RunDetectionThread, args = (orig_img.copy(),output_img))
				t.start()

				self.CurrentHaarRecsLock.acquire()
				try:
					self.box(self._haarCurrentRects, output_img)
					self._haarCounter+=1
				finally:
					self.CurrentHaarRecsLock.release()

			if self._RecordVideo:
				_videoOut.write(output_img)


			if self._showOutput:

				cv2.putText(output_img, str(currentFPS),(5,int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))-10),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0))

				cv2.imshow("OutPut "+str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)))+" "
							+str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))) ,output_img)

			#I Never rember what wait key does 
			#But one of the best things is that you can pull keypresses
			x = cv2.waitKey(1)

			#If you press q baill out
			if x & 0xFF == ord('q'):
				cv2.destroyAllWindows()
				self._MainCaptureIterFace.release()
				self._Run_Flag = False

				if self._RecordVideo:
					_videoOut.release()

				print "Bailing Out... Cya!!!"

			#IF F is pressed do some basic Haar recognition
			elif x & 0xFF == ord('h'):
				if self._haarRecFilterFlag[0]:
					self._haarDetect_Flag = not self._haarDetect_Flag

					#value_when_true if condition else value_when_false
					print "Haar Filter Tracking " + ("on" if self._haarDetect_Flag else "off")
				else:
					print "Nope Sry... Something went wrong with Resource: "+self._haarRecogFilter, self._haarRecFilterFlag[1]

			elif x & 0xFF == ord('n'):

				#Ask for new file
				filename =  askopenfilename(initialdir = self.Resources_Root_Folder+"haarFilter_Face_Basic/")# show an "Open" dialog box and return the path to the selected file
		
				#Make sure file exists
				if os.path.isfile(filename):

					self._haarRecFilterFlag = (True, None)
					self._haarRecogFilter = filename
				
				elif os.path.isfile(self.Resources_Root_Folder+"haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"):
					print "WOOPC Something woonkie happened with your haar filter selection...\nhad to default to: "+self.Resources_Root_Folder+"haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"
					self._haarRecFilterFlag = (True, None)
					self._haarRecogFilter = self.Resources_Root_Folder+"haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"
				
				else :
					self._haarRecFilterFlag = (False, "File Doesnt Exist")

				#Pull in the cascade feature template we want to use
				try:
					self.cascade = cv2.CascadeClassifier(self._haarRecogFilter)
				except Exception, e:
					self._haarRecFilterFlag = (False, e)

			#If M is pressed use multi haarfilters in selected dir
			elif x & 0xFF == ord('m'):
				if self._haarMulti_Flag[0] == False:

					dirname = askdirectory(parent=root, initialdir='/home/', title='Select your pictures folder')
					print "The Directory name: ", dirname

					if os.path.isdir(dirname):
						self._haarMulti_Flag = (True, dirname)
					else:
						self._haarMulti_Flag = (False, None)
				else:
					self._haarMulti_Flag = (False, None)


			#If Enter Is pressed Enter sart video Record
			elif x & 0xFF == ord('c'):
				if not self._RecordVideo:
					_vidcount+=1
					codec = cv.CV_FOURCC('D','I','V','X')

					size = (int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)),
							int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)))

					_videoOut = cv2.VideoWriter()
					_videoOut.open(self.Videos_Root_Folder+'OutVideo('+str(_vidcount)+').avi', codec, 30, size, 1)
					
					self._RecordVideo = True
					print "Sarted Video record"

				else:
					#Close video out File And set capture boolean to false
					_videoOut.release()
					self._RecordVideo = False

					print "Ended Video record"

			elif x == 32:
				#TSH SPACE: 1048608
				print "Catured Images", self.Images_Root_Folder+"SnapShop("+str(_imgcount)+").jpg"
				
				#Capture Image
				cv2.imwrite(self.Images_Root_Folder+"SnapShop("+str(_imgcount)+").jpg", output_img)
				
				#Inc counter Variableh
				_imgcount+=1

			#case you want to know what key you pressed
			elif x != -1:
				print "Key Press ==",x
	

	#How to make a propertry 
	#-------------------------------------- VVV RIGHT HERE!!! VVV
	#<property_name> = property(<getter_Method_Name>, <setter_Method_Name>)

if __name__ == '__main__':
	runner = OculusMaximus()
	runner.run()

