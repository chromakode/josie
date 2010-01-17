class Error(Exception):
	pass

class VersionError(Error):
	"""Raised when an insufficient program version is present"""
	def __init__(self, current, required):
		self.current = current
		self.required = required
	def __str__(self):
		return "%s (Require %s)" % (self.current, self.required)

class FileFormatError(Error):
	"""Raised when """
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return self.message
