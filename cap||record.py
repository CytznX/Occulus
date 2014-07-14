"""
pyClass I use for testing and recording some image analysis filters

Created By: Citizenx
"""

#Some 
import time
import os
import numpy as np
import cv2
import cv


class OculusMaximus():

	def __init__(self):

		#Some Default Resoure Folder Stuff
		self.Videos_Root_Folder = "vid/"
		self.Images_Root_Folder = "img/"
		self.Resources_Root_Folder = "res/"

		#Check to see if record directorys exists
		for checkDirectory in [ self.Videos_Root_Folder, self.Images_Root_Folder, self.Resources_Root_Folder]:

			if not os.path.isdir(checkDirectory):
				os.makedirs(checkDirectory)
				print "No "+checkDirectory+" Directory... EmptyOne Created"


		self._FacialDetect_Flag = False
		self._Run_Flag = True
		
		#default facial REc Directory
		if os.path.isfile(self.Resources_Root_Folder+"haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"):
			self._FacialRecFilterFlag = (True, None)
			self.FaceRecogFilter = self.Resources_Root_Folder+"haarFilter_Face_Basic/haarcascade_frontalface_alt.xml"

		else :
			self._FacialRecFilterFlag = (False, "File Doesnt Exist")

		#Pull in the cascade feature template we want to use
		try:
			self.cascade = cv2.CascadeClassifier(self.FaceRecogFilter)
		except Exception, e:
			self._FacialRecFilterFlag = (False, e)


		#Create the Video Interfaces
		self._MainCaptureIterFace = cv2.VideoCapture(0)
		

	def detectFaces(self, img):
	    rects = self.cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))

	    if len(rects) == 0:
	        return [], img
	    rects[:, 2:] += rects[:, :2]
	    return rects, img

	def box(self, rects, img):
		for x1, y1, x2, y2 in rects:
			cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
	
	def compare(self, rects, img):
		crop_img = img[y1:y2, x1:x2, :] 
		
	def run(self):


		cv2.namedWindow("OutPut")
		_faceCounter = 0
		

		while(self._Run_Flag):

			_,orig_img = self._MainCaptureIterFace.read()
			orig_img = cv2.flip(orig_img, 1)
			output_img = orig_img.copy()

			if (self._FacialDetect_Flag == True):

				orig_img = cv2.GaussianBlur(orig_img, (5,5), 0)
			
				if _faceCounter%2==0:
					rects, img = self.detectFaces(orig_img)
					
				self.box(rects, output_img)
				_faceCounter+=1

			cv2.imshow("OutPut",output_img)

			#I Never rember what wait key does 
			#But one of the best things is that you can pull keypresses
			x = cv2.waitKey(1)

			#If you press q baill out
			if x & 0xFF == ord('q'):
				cv2.destroyAllWindows()
				self._MainCaptureIterFace.release()
				self._Run_Flag = False
				print "Bailing Out... Cya!!!"

			#IF F is pressed do some basic facial recognition
			elif x & 0xFF == ord('f'):
				if self._FacialRecFilterFlag[0]:
					self._FacialDetect_Flag = not self._FacialDetect_Flag

					#value_when_true if condition else value_when_false
					print "Face Tracking " + ("on" if self._FacialDetect_Flag else "off")
				else:
					print "Nope Sry... Something went wrong with Resource: "+self.FaceRecogFilter, self._FacialRecFilterFlag[1]

			#case you want to know what key you pressed
			elif x != -1:
				print "Key PRess ==",x


if __name__ == '__main__':
	runner = OculusMaximus()
	runner.run()

