import Queue
import threading
import time

#Thread that watches Everything... Litterally
class OcculusOverloard(threading.Thread):
	
	#Meh its a variable cause i wanted to see if i can auto scale sleeptime
	self._sleepTime = 0
	self._Run_Flag = True
	self._CurrentRunningThreads = []

	def __init__(self,):
		threading.Thread.__init__(self)

	#yuuuuuuuuuuuuuuuuuuup.... the runner...
	def run(self):
		
		#Stay operational so long as the program is running
		while self._Run_Flag:

			#If the arrays empty wait sometime
			if self._CurrentRunningThreads == []:
				
				self._sleepTime+=0.03
				time.sleep(self._sleepTime)
			else:
				if not self._sleepTime == 0:
					self._sleepTime-=0.01

				#Itterate through all availible threads
				for DetectionThreadM in self._CurrentRunningThreads:

					#If the Thread is dead... Remove it from List
					if not DetectionThreadM.isAlive():
						self._CurrentRunningThreads.remove(DetectionThreadM)

				#Go to sleep... <3 ... <3 ... <3
				time.sleep(self._sleepTime)

		#When we want to quit the program iterate acrross all reamining running threads and call .join()
		for DetectionThreadM in self._CurrentRunningThreads:
			DetectionThreadM.join()