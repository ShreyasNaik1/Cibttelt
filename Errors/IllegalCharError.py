from errors import * 

class IllegalCharError(Error):
	def __init__(self, startPos, endPos, details):
		super().__init__(startPos, endPos, 'Illegal Character', details)