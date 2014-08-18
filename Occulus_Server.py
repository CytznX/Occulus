
import SimpleHTTPServer
import SocketServer
import os


class OcculusResourceServer():
	def __init__(self, baseDir=None, portNum=8000):

		#Change To base directory that needs to be hosted
		if not baseDir is None:
			os.chdir(baseDir)

		self._PORT = portNum

		self._Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

		#Open Up a socket server and tell it to handle reqests untill .shutdown() is falled
		self._httpd = SocketServer.TCPServer(("", self._PORT), self._Handler)
		self._httpd.serve_forever()

	def __del__(self):
		self._httpd.shutdown()
