
#USed to format to CV image
import numpy
import cv2

#USed For Connecting and converting camera image
import base64
import Image
import urllib2 


class URLCam:
	def __init__(self, addr ="http://155.31.133.115/axis-cgi/mjpg/video.cgi",DesiredRes=(704,576), username="root", password="root"):

		self.ip = ip

		#Variable Needed To Connect to camera
		self.addr=addr
		self.res = DesiredRes

		#User Name Password
		self.username = username
		self.password = password

	def connect(self):
		try:

			#Do some quick Formatting
			url = '%s?resolution=%sx%s' % (self.addr,self.res[0],self.res[1])
			ww = self.username+':'+self.password

			#WOOOOOOOOOOOOOT IM a god
			#ACTUALL THIS CODE... NOT MINE... >< ... OHWell ----------------------------------------------
			encodedstring = base64.encodestring(ww)[:-1]
			auth = "Basic %s" % encodedstring

			req = urllib2.Request(url,None, {"Authorization": auth })
			self.handle = urllib2.urlopen(req)
			#--------------------------------------------------------------------------------------

			#IF it works tell us... if not... quit
			return True
		
		except:
			return False


	def read_stream(self):
		#emptys the Buffer
		buf = ''

		#Read Stream 
		b = self.handle.readlines(45)
		
		#keeep reading in till dead
		for a in b:
			if a.startswith('Content-Length'):
				readlen = str(a).split()[1]

		#the complete image'String'
		b1 = self.handle.read(int(readlen)+4)
		return b1

	def GetFrame(self):

		#Get image Dimensions
		rx = self.res[0]
		ry = self.res[1]

		#Gets Stream in form of a string
		self.imgc = self.read_stream()
		
		#I read it in using the Python Image Library 
		buf = Image.fromstring('YCbCr',(rx,ry),self.imgc[2:], 'jpeg', 'YCbCr', None)
		con = buf.convert('RGB')

		#Pass the image off to numpt to convert into openCV 
		cv_img = numpy.array(con)

		#flips the image from RGB to BGR
		cv_img = cv_img[:, :, ::-1].copy() 

		#returns a numpy Array
		return cv_img


if __name__ == "__main__":
	ip_cam=URLCam()
	ip_cam.connect()

	while True:
		frame = ip_cam.GetFrame()
		
		cv2.imshow('IP Camera Stream', cv2.flip(frame, 0))
		k = cv2.waitKey(10)
		if k == 27: # ESC
			cv2.destroyAllWindows()
			print 'ESC pressed. Exiting ...'
			break
		elif not k==-1:
			print k