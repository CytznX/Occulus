"""_____________________________________________________________________________
pyClass I use for testing and recording some image analysis filters

Created By: Citizenx
Python 2.7
_____________________________________________________________________________"""

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

	def __init__(self, showOutput=True, interface=1, motionSensitivity=(3, 3)):

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
		self._MotionDetect_Flag = False
		self._haarMulti_Flag = False
		self._Run_Flag = True
		self._RecordVideo = False

		#autosave class variables
		self._AutoSave = False
		self._VideoStartTime = None
		self._LastMotion = None
		self._runlength = 5

		#show debug print statments for auto save
		self._debug = False

		#Store defaults/main vars
		self._Motionsensitivity = motionSensitivity

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

		self._codec = cv.CV_FOURCC('D', 'I', 'V', 'X')

		self._size = (int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)),
						int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)))

		#Calculates FPS
		self._LastImageCapture = datetime.datetime.now()

		if not self._MainCaptureIterFace.isOpened():
				self.endRun("Capture Interface: "+str(interface)+" Could Not be opened")

	#Draw Rectangles on a image
	def box(self, rectsContainer, img, color=(127, 255, 0)):
		for rects in rectsContainer:
			for x1, y1, x2, y2 in rects:
				cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

	def endRun(self, Reason=""):
		cv2.destroyAllWindows()
		self._MainCaptureIterFace.release()
		self._Run_Flag = False
		self._ThreadOverLoard.stop()

		if self._RecordVideo:
			_videoOut.release()

		#Signals Main Vid Thread is done... and where waiting on subthreads
		print "Bailing Out...\n"+Reason+"\nCya!!!"

		#-----------------------------------------
		#Make sure to join all threads Bellow
		#-----------------------------------------
		self._ThreadOverLoard.join()  # Wait for the Overloard to close out clean

		#One Last Final Goodbye
		print "Le fin"

	def run(self):

		#Check If i want output shown
		if self._showOutput:
			cv2.namedWindow("OutPut "+str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)))+" "
							+ str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))))

		#Variable used to store open Output video file reference
		_videoOut = None

		while(self._Run_Flag):

			#Capture New Frame and record when you did it
			_, orig_img = self._MainCaptureIterFace.read()

			#Bail out i
			if (_ is False):
				self.endRun("something went wrong could not grab frame from capture interface")
				break

			#Comput Fps
			_currentCaptureTime = datetime.datetime.now()
			currentFPS = 1.0/(_currentCaptureTime-self._LastImageCapture).total_seconds()
			self._LastImageCapture = _currentCaptureTime

			#Flip the image so its mirrored and make a copy to be used later
			orig_img = cv2.flip(orig_img, 1)
			output_img = orig_img.copy()

			#I pass original because the overloard makes an internal copy that it passes off to its subthreads
			self._ThreadOverLoard.addFrame(orig_img)

			#Captures haar analysis... if any
			_Temp = self._ThreadOverLoard.getInfo()

			#Captures motiion analysis... if any
			_Temp2 = self._ThreadOverLoard.getLatestMotionAnalysis()

			if self._haarDetect_Flag:
				#Draw The Box around detected faces
				self.box(self._ThreadOverLoard.getLatestHaarAnalysis(), output_img)

			#Display image
			if self._showOutput:

				_DispText = "FPS: %02d" % (currentFPS)

				if self._haarDetect_Flag or self._MotionDetect_Flag:
					_DispText += " #Threads: %d SleepTime: %.2f" % _Temp

					if self._MotionDetect_Flag:
						_DispText2 = ""

						if _Temp2 is None:
							_DispText2 = "Initializing..."
						else:
							_Temp2 = (_Temp2[0][0], _Temp2[1][0])
							_DispText2 = " Mean: %.2f Deviation: %.2f" % _Temp2

						cv2.putText(output_img, _DispText2, (5, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0))

				cv2.putText(output_img, _DispText, (5, int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))-10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0))

			#Write Video out to selected file
			if self._RecordVideo:
				_videoOut.write(output_img)

			#if auto record is active
			if self._AutoSave and not _Temp2 is None:

				#if Theres no video recording
				if self._VideoStartTime is None:

					#If theres Motion
					if _Temp2[0] > self._Motionsensitivity[0] or _Temp2[1] > self._Motionsensitivity[1]:

						#record video StartTime and determine subdirectory
						self._LastFrameTime = datetime.datetime.now()
						self._VideoStartTime = datetime.datetime.now()

						#subdir
						_subDir = self.Videos_Root_Folder+"autoCapture/"+self._LastFrameTime.strftime("%B_%d_%Y/")

						#Create a video writer
						self._Video = cv2.VideoWriter()

						#more debud
						if self._debug:
							print _subDir+self._LastFrameTime.strftime("%H:%M:%S")

						#make the sub-dir
						if not os.path.isdir(_subDir):
							os.makedirs(_subDir)

						#OPen Video
						self._Video.open(_subDir+self._LastFrameTime.strftime("(%H:%M:%S)")+'.avi', self._codec, 30, self._size, 1)

						#Meh... more debug
						if self._debug:
							print "started SaveRecording"

				#Else if where recording and still see motion
				elif (not _Temp2 is None) and (_Temp2[0] > self._Motionsensitivity[0] or _Temp2[1] > self._Motionsensitivity[1]):

					#New startime... and write frame
					self._LastFrameTime = datetime.datetime.now()
					self._LastMotion = datetime.datetime.now()
					self._Video.write(output_img)

					#Debug!!!!!
					if self._debug:
						print "Wrote a frame"

				elif (datetime.datetime.now()-self._LastMotion).total_seconds() <= self._runlength:
					self._Video.write(output_img)
					self._LastFrameTime = datetime.datetime.now()
					if self._debug:
						print "wrote a frame... but no motion... " + str((self._LastFrameTime-self._VideoStartTime).total_seconds())

				else:

					#close the video file "save"
					self._Video.release()

					#Wipe the Vars clean
					self._Video = None
					self._LastFrameTime = None
					self._VideoStartTime = None
					self._LastMotion = None

					#Debug out
					if self._debug:
						print "Closed video"

			if not self._VideoStartTime is None:
				if _Temp2[0] > self._Motionsensitivity[0] or _Temp2[1] > self._Motionsensitivity[1]:
					cv2.circle(output_img, (int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))-12, 12), 10, (0, 255, 0), -1)
				else:
					cv2.circle(output_img, (int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))-12, 12), 10, (0, 0, 255), -1)
				cv2.circle(output_img, (int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))-12, 12), 10, (0, 0, 0), 2)

			cv2.imshow("OutPut "+str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)))+" "
								+ str(int(self._MainCaptureIterFace.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))), output_img)

			#I Never rember what wait key does
			#But one of the best things is that you can pull keypresses
			x = cv2.waitKey(1)

			#If you press q baill out
			if x & 0xFF == ord('q'):
				self.endRun()

			elif x & 0xFF == ord('r'):
				self._AutoSave = not self._AutoSave
				print "Auto Record " + ("on" if self._AutoSave else "off")

			#IF h is pressed do some basic Haar recognition
			elif x & 0xFF == ord('h'):
				if self._XML_isValid[0]:
					self._haarDetect_Flag = not self._haarDetect_Flag

					self._ThreadOverLoard.setFlags(self._haarDetect_Flag, self._MotionDetect_Flag)
					#value_when_true if condition else value_when_false
					print "Haar Filter Tracking " + ("on" if self._haarDetect_Flag else "off")
				else:
					print "---Nope Sry... Something went wrong with XML Resource---\n", self._XML_isValid

			elif x & 0xFF == ord('m'):

				self._MotionDetect_Flag = not self._MotionDetect_Flag

				self._ThreadOverLoard.setFlags(self._haarDetect_Flag, self._MotionDetect_Flag)
				#value_when_true if condition else value_when_false
				print "Haar Motion Tracking " + ("on" if self._MotionDetect_Flag else "off")

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
			elif x & 0xFF == ord('d'):
				dirname = askdirectory(initialdir=self.Resources_Root_Folder, title='Select A Directory Folder')
				print "The Directory name: ", dirname

			#If Enter Is pressed Enter sart video Record
			elif x & 0xFF == ord('c'):
				if not self._RecordVideo:

					print "Video recordkey pressed"
					_tmpDir = "manualCapture/"+datetime.datetime.now().strftime("%B_%d_%Y/")

					#make the sub-dir
					if not os.path.isdir(self.Videos_Root_Folder+_tmpDir):
						os.makedirs(self.Videos_Root_Folder+_tmpDir)

					print "tmp directory created"

					_videoOut = cv2.VideoWriter()

					print "writer initialiazed"
					_videoOut.open(self.Videos_Root_Folder+_tmpDir+"manualCap("+datetime.datetime.now().strftime("%H:%M:%S")+").avi", self._codec, 30, self._size, 1)

					self._RecordVideo = True
					print "Sarted Video record"

				else:
					#Close video out File And set capture boolean to false
					_videoOut.release()
					self._RecordVideo = False

					print "Ended Video record"

			elif x == 32 or x == 1048608:
				#TSH SPACE: 1048608

				_tmpDir = "manualCapture/"+datetime.datetime.now().strftime("%B_%d_%Y/")

				#make the sub-dir
				if not os.path.isdir(self.Images_Root_Folder+_tmpDir):
					os.makedirs(self.Images_Root_Folder+_tmpDir)

				print "Catured Images", self.Images_Root_Folder+_tmpDir+"SnapShop"+datetime.datetime.now().strftime("(%H:%M:%S)")+".jpg"

				#Capture Image
				cv2.imwrite(self.Images_Root_Folder+_tmpDir+"SnapShop"+datetime.datetime.now().strftime("(%H:%M:%S)")+".jpg", output_img)

			#case you want to know what key you pressed
			elif x != -1:
				print "Key Press ==", x


	#How to make a propertry
	#-------------------------------------- VVV RIGHT HERE!!! VVV
	#<property_name> = property(<getter_Method_Name>, <setter_Method_Name>)

if __name__ == '__main__':
	runner = OculusMaximus()
	runner.run()
