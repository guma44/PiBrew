import threading
import time



class MyThread(threading.Thread):

	def __init__(self, param):
		super(MyThread, self).__init__()
		self.param = param
		self._stop = threading.Event()

	def set_param(self, newparam):
		self.param = newparam

	def run(self):
		while not self.is_stopped():
			print self.param
			time.sleep(1)

	def stop(self):
		print "Thread stopped"
		self._stop.set()

	def is_stopped(self):
		return self._stop.isSet()

try:
	thread = MyThread(0)
	thread.start()
	for i in range(1, 5):
		thread.set_param(i)
		time.sleep(4)
finally:
	thread.stop()

