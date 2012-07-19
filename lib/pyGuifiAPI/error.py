class GuifiApiError(Exception):
	def __init__(self, reason, response=None):
		self.reason = reason
		self.response = response

	def __str__(self):
		return self.reason
