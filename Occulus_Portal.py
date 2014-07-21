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
		self._Run_Flag = True
		self._RecordVideo = False

		#Heres how i create those file viewer dialog boxes
		Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
		filename =  askopenfilename(initialdir = self._CurrentHaarXML)# show an "Open" dialog box and return the path to the selected file
		
		#Create the Video Interfaces
		self._MainCaptureIterFace = cv2.VideoCapture(0)

		#Calculates FPS
		self._LastImageCapture = datetime.datetime.now()


	
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

		#Create Temporary holding variable for Shared Recs Variable Clone
		_tmpRecs = []


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

				#<<<<<<<----------------------------------------------------<<<< FIX ME!!!!
				pass
				

			#Write Video out to selected file
			if self._RecordVideo:
				_videoOut.write(output_img)

			#Display image
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
				#-----------------------------------------
				#Make sure to join all threads Bellow
				#-----------------------------------------

				print "Le fin"

			#IF F is pressed do some basic Haar recognition
			elif x & 0xFF == ord('h'):
				print "U press the Haar detect button"

			elif x & 0xFF == ord('n'):
				#Get New Filter
				#Ask for new file
				filename =  askopenfilename(initialdir = self.Resources_Root_Folder+"haarFilter_Face_Basic/")# show an "Open" dialog box and return the path to the selected file
				print "new file requested", filename

			#If M is pressed use multi haarfilters in selected dir
			elif x & 0xFF == ord('m'):
				dirname = askdirectory(initialdir=self.Resources_Root_Folder, title='Select your pictures folder')
				print "The Directory name: ", dirname



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

