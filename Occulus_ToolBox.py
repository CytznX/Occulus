"""_____________________________________________________________________________

Original This skript innitialized the Occulus Program,
Now its used to Hold/define some usefull user made image Analysis Algorithimss

Created By: CitizenX
Python 2.7
_____________________________________________________________________________"""

#Necisary Imports
import cv2
import cv


#CALCULATES_A_"DIFFERENCE"_IMAGE________________________
#I Dont rember where i first saw this being used,stumbled across it on the
#internet somewhere. buts its really nice for showing motion/sequence movment
def diffImg(t0, t1, t2):

	d1 = cv2.absdiff(t2, t1)
	d2 = cv2.absdiff(t1, t0)
	return cv2.bitwise_and(d1, d2)


#CALCULATES_THE_DIFFERNCE_BETWEEN_2_HISTOGRAMS_AND_RETURNS_VALUE(0.0-1.0)________________
#YEAH... needed a way to compare faces, histograms seamed like the easyiest way
def Compare_2IMG_by_Histogram(passedImg1, passedImg2, comparison_Method=cv.CV_COMP_CORREL):

	#convert both images to HSV
	_img1 = cv2.cvtColor(passedImg1, cv.CV_BGR2HSV)
	_img2 = cv2.cvtColor(passedImg2, cv.CV_BGR2HSV)

	#iteratible chanles
	_color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

	#to be returned later
	bgrReturnValues = []
	hist1 = []
	hist2 = []

	#itterate accros all the color chanels
	for ch, col in enumerate(_color):

		#Calculate Histograms
		hist_item1 = cv2.calcHist([_img1], [ch], None, [256], [0, 255])
		hist_item2 = cv2.calcHist([_img2], [ch], None, [256], [0, 255])

		#Do some Normilization
		cv2.normalize(hist_item1, hist_item1, 0, 255, cv2.NORM_MINMAX)
		cv2.normalize(hist_item2, hist_item2, 0, 255, cv2.NORM_MINMAX)

		#compare
		sc = cv2.compareHist(hist_item1, hist_item2, cv.CV_COMP_CORREL)

		#addValues to return list
		bgrReturnValues.append(sc)
		hist1.append(hist_item1)
		hist2.append(hist_item2)

	return bgrReturnValues, hist1, hist2,

def Compare_Histogram_To_Img(hist1, passedImg2, comparison_Method=cv.CV_COMP_CORREL):

	#convert passed image to HSV
	_img2 = cv2.cvtColor(passedImg2, cv.CV_BGR2HSV)

	#iteratible chanles
	_color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

	#to be returned later
	bgrReturnValues = []
	hist2 = []

	#itterate accros all the color chanels
	for ch, col in enumerate(_color):

		#Calculate Histogram
		hist_item2 = cv2.calcHist([_img2], [ch], None, [256], [0, 255])

		#Do some Normilization(assumes passed histogram is already)
		cv2.normalize(hist_item2, hist_item2, 0, 255, cv2.NORM_MINMAX)

		#compare
		sc = cv2.compareHist(hist1[ch], hist_item2, cv.CV_COMP_CORREL)

		#addValue to return list
		bgrReturnValues.append(sc)
		hist2.append(hist_item2)

	return bgrReturnValues, hist2
