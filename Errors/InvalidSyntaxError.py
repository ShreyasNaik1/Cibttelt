from errors import *


class InvalidSyntaxError(Error):
	def __init__(self, startPos, endPos, details=''):
		super().__init__(startPos, endPos, 'Invalid Syntax', details)
