from threading import Thread
#from threading import Lock
from queue import Empty

try:
	import queue
except ImportError:
	import Queue as queue


#See http://eyalarubas.com/python-subproc-nonblock.html
class NonBlockingStreamReader:

	def __init__(self, stream):
		'''
		stream: the stream to read from.
				Usually a process' stdout or stderr.
		'''
		self._s = stream
		self._q = queue.Queue()
		self.exception = None
		self.isEndOfStream=True
		#self.mutex = Lock()
		self._t = Thread(target=self._populateQueue, args = ())
		self._t.daemon = True
		self._t.start() #start collecting lines from the stream

	def _populateQueue(self):
		''' Collect lines from 'stream' and put them in 'quque'. '''
		self.isEndOfStream = False
		while True:
			line = self._s.readline()
			if line:
				#self.mutex.acquire()
				line_de=line.decode('utf-8').rstrip()
				#print('line_de',line_de)
				self._q.put(line_de)
				#self.mutex.release()
			else:
				#raise UnexpectedEndOfStream
				self.isEndOfStream = True
				break

	def readline(self, timeout = None):
		data = None
		try:
			#self.mutex.acquire()
			#https://docs.python.org/3/library/queue.html
			data= self._q.get(block = timeout is not None,timeout = timeout)
			if data : self._q.task_done()
			#data= self._q.get()
			
		except Empty as empt:
			#self._q.mutex.release()
			self.exception = empt
			data = None
		finally:
			#self.mutex.release()
			pass
		return data
	def hasMore(self):
		if self.isEndOfStream == True and self._q.empty() == True:
			return False
		return True
