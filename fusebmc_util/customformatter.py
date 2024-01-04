import logging

class CustomFormatter(logging.Formatter):
	"""Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

	grey = '\x1b[38;21m'
	blue = '\x1b[38;5;39m'
	yellow = '\x1b[38;5;226m'
	red = '\x1b[38;5;196m'
	bold_red = '\x1b[31;1m'
	OKGREEN = '\033[92m'
	reset = '\x1b[0m'

	def __init__(self, fmt):
		super().__init__()
		self.fmt = fmt
		self.FORMATS = {
			logging.DEBUG: self.OKGREEN + self.fmt + self.reset,
			logging.INFO: self.blue + self.fmt + self.reset,
			logging.WARNING: self.yellow + self.fmt + self.reset,
			logging.ERROR: self.red + self.fmt + self.reset,
			logging.CRITICAL: self.bold_red + self.fmt + self.reset
		}

	def format(self, record):
		log_fmt = self.FORMATS.get(record.levelno)
		formatter = logging.Formatter(log_fmt)
		return formatter.format(record)
	
	@staticmethod
	def getLogger(name='',level:int=logging.DEBUG):
		logger = logging.getLogger(name)
		#fmt = '%(asctime)s | %(levelname)8s | %(message)s'
		fmt = '%(levelname)s| %(message)s'
		stdout_handler = logging.StreamHandler()
		stdout_handler.setLevel(level)
		stdout_handler.setFormatter(CustomFormatter(fmt))
		logger.addHandler(stdout_handler)
		return logger
		
		