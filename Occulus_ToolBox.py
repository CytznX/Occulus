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

#compares an already calculated histogram to a passe dimg
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


#DOES NOT WORK...
#SURF and SIFT opperation are includded in "nonfree" libraries
#Unfortuanaly Iam real cheap... =p
def surfDetect(img=None, imgPath=None):

	if not img is None:
		_im2 = img
	elif not imgPath is None:
		_im2 = cv2.imread(imgPath)
	else:
		return None

	_im = cv2.cvtColor(_im2, cv2.COLOR_BGR2GRAY)
	_surfDetector = cv2.FeatureDetector_create("SURF")
	_surfDescriptorExtractor = cv2.DescriptorExtractor_create("SURF")
	_keypoints = _surfDetector.detect(_im)
	_keypoints, _descriptors = _surfDescriptorExtractor.compute(_im, _keypoints)

	return _keypoints, _descriptors


def matchTemplate(img, template, method):

	#Possible Methods___________________
	#['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR','cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

	method = eval(method)
	w, h = template.shape[::-1]

	# Apply template Matching
	res = cv2.matchTemplate(img, template, method)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

	# If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
	if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
			top_left = min_loc
	else:
			top_left = max_loc
	bottom_right = (top_left[0] + w, top_left[1] + h)

	return top_left, bottom_right
