"""
pyClass I use for testing and recording some image analysis filters

Created By: Citizenx
"""

#Some Basic imports
import datetime
import os
import cv2
import cv

#Some Renamed Import
from Tkinter import Tk
from tkFileDialog import askopenfilename
from tkFileDialog import askdirectory

import Occulus_Threader


class OculusMaximus():

	def __init__(self, showOutput=True, interface=0):

		#Capture Some Initialization
		self._showOutput = showOutput

		#Some Default Resoure Folder Stuff
		self.Videos_Root_Folder = "vid/"
		self.Images_Root_Folder = "img/"
		self.Resources_Root_Folder = "res/"

		#Keeps Track of Current Haar Wavelet
		self._CurrentHaarXML = self.Resources_Root_Folder+"haarFilter_Face_Basic/"

		#Check to see if record directorys exists
		for checkDirectory in [self.Videos_Root_Folder, self.Images_Root_Folder, self.Resources_Root_Folder]:
			if not os.path.isdir(checkDirectory):
				os.makedirs(checkDirectory)
				print "No "+checkDirectory+" Directory... EmptyOne Created"

		#Sets some initial class Flag Variables & Counters
		self._haarDetect_Flag = False
		self._haarMulti_Flag = False
		self._Run_Flag = True
		self._RecordVideo = False

		#Start The Overloard
		self._ThreadOverLoard = Occulus_Threader.OcculusOverloard()
		self._ThreadOverLoard.start()

		#Heres how i create those file viewer dialog boxes
		Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing

		#Uncoment the back half to prompt at initialization
		_filename = ""  # = askopenfilename(initialdir=self._CurrentHaarXML, title='Select Your Initial Haar Filter')  # show an "Open" dialog box and return the path to the selected file
		self._XML_isValid = self._ThreadOverLoard.newFilter(_filename)

		if self._XML_isValid[0]:
			self._CurrentHaarXML = _filename
		else:
			print "---Something Bad Happend While Loading Haar XML---\n", self._XML_isValid[1]

		#Create the Video Interfaces
		self._MainCaptureIterFace = cv2.VideoCapture(interface)

		#Calculates FPS
		self._LastImageCapture = datetime.datetime.now()

	#Draw Rectangles on a image
	def box(self, rectsContainer, img, color=(127, 255, 0)):
		for rects in rectsContainer:
			for x1, y1, x2, y2 in rects:
				cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

	def run(self):

		#Check If i want output shown
		if self._showOutput:
			cv2.namedWindow("OutPut "+str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)))+" "
							+ str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))))

		#Initializ some counter variables
		_vidcount = 0
		_imgcount = 0

		#Variable used to store open Output video file reference
		_videoOut = None

		_cap = True

		while(self._Run_Flag):

			if _cap:

				#Capture New Frame and record when you did it
				_, orig_img = self._MainCaptureIterFace.read()

				#Comput Fps
				_currentCaptureTime = datetime.datetime.now()
				currentFPS = 1.0/(_currentCaptureTime-self._LastImageCapture).total_seconds()
				self._LastImageCapture = _currentCaptureTime

				#Flip the image so its mirrored and make a copy to be used later
				orig_img = cv2.flip(orig_img, 1)
				output_img = orig_img.copy()

				if self._haarDetect_Flag:

					#I pass original because the overloard makes an internal copy that it passes off to its subthreads
					self._ThreadOverLoard.addFrame4Haar(orig_img)
					self.box(self._ThreadOverLoard.getLatestHaarAnalysis(), output_img)

				#Display image
				if self._showOutput:

					_DispText = "FPS: %02d" % (currentFPS)

					if self._haarDetect_Flag:
						Temp = self._ThreadOverLoard.getInfo()
						_DispText += " #Threads: %d SleepTime: %.2f" % Temp

					cv2.putText(output_img, _DispText, (5, int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))-10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0))

					cv2.imshow("OutPut "+str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)))+" "
								+ str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))), output_img)

					_cap = False

			#Write Video out to selected file
			if self._RecordVideo:
				_videoOut.write(output_img)

			#I Never rember what wait key does
			#But one of the best things is that you can pull keypresses
			x = cv2.waitKey(1)

			#If you press q baill out
			if x & 0xFF == ord('q'):
				cv2.destroyAllWindows()
				self._MainCaptureIterFace.release()
				self._Run_Flag = False
				self._ThreadOverLoard.stop()

				if self._RecordVideo:
					_videoOut.release()

				#Signals Main Vid Thread is done... and where waiting on subthreads
				print "Bailing Out... Cya!!!"

				#-----------------------------------------
				#Make sure to join all threads Bellow
				#-----------------------------------------
				self._ThreadOverLoard.join()  # Wait for the Overloard to close out clean

				#One Last Final Goodbye
				print "Le fin"

			elif x & 0xFF == ord('j'):
				_cap = True

			#IF F is pressed do some basic Haar recognition
			elif x & 0xFF == ord('h'):
				if self._XML_isValid[0]:
					self._haarDetect_Flag = not self._haarDetect_Flag

					#value_when_true if condition else value_when_false
					print "Haar Filter Tracking " + ("on" if self._haarDetect_Flag else "off")
				else:
					print "---Nope Sry... Something went wrong with XML Resource---\n", self._XML_isValid

			#If N is Pressed... Load in new XML file
			elif x & 0xFF == ord('n'):

				#Ask for new file
				_filename = askopenfilename(initialdir=self.Resources_Root_Folder+"haarFilter_Face_Basic/", title='Select Your Haar Filter')
				print "new file requested", _filename

				#Checks if were valid
				self._XML_isValid = self._ThreadOverLoard.newFilter(_filename)

				#If where valid... Bailout
				if self._XML_isValid[0]:
					self._CurrentHaarXML = _filename
				else:
					print "---Something Bad Happend While Loading Haar XML---\n", self._XML_isValid[1]

			#If M is pressed use multi haarfilters in selected dir
			elif x & 0xFF == ord('m'):
				dirname = askdirectory(initialdir=self.Resources_Root_Folder, title='Select A Directory Folder')
				print "The Directory name: ", dirname

			#If Enter Is pressed Enter sart video Record
			elif x & 0xFF == ord('c'):
				if not self._RecordVideo:
					_vidcount += 1
					codec = cv.CV_FOURCC('D', 'I', 'V', 'X')

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
				_imgcount += 1

			#case you want to know what key you pressed
			elif x != -1:
				print "Key Press ==", x


	#How to make a propertry
	#-------------------------------------- VVV RIGHT HERE!!! VVV
	#<property_name> = property(<getter_Method_Name>, <setter_Method_Name>)

if __name__ == '__main__':
	runner = OculusMaximus()
	runner.run()
