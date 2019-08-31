from errors import *


class ExpectedCharError(Error):
	def __init__(self, startPos, endPos, details):
		super().__init__(startPos, endPos, 'Expected Character', details)
