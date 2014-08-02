"""
Original This skript innitialized the Occulus Program,
Now its used to Hold/define some usefull user made image Analysis Algorithimss

Created By: CitizenX
Python 2.7
"""

#Necisary Imports
import cv2


#CALCULATES_A_"DIFFERENCE"_IMAGE________________
def diffImg(t0, t1, t2):

	d1 = cv2.absdiff(t2, t1)
	d2 = cv2.absdiff(t1, t0)
	return cv2.bitwise_and(d1, d2)
