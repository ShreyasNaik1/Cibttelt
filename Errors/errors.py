import sys

sys.path.insert(0, '../')
from string_with_arrows import *


class Error:
	def __init__(self, startPos, endPos, errorName, details):
		self.startPos = startPos
		self.endPos = endPos
		self.errorName = errorName
		self.details = details
	
	def printStr(self):
		result  = '{}: {}\n'.format(self.errorName, self.details)
		result += 'File {}, line {}'.format(self.startPos.fname, self.startPos.ln + 1)
		result += '\n\n' + string_with_arrows(self.startPos.fcontent, self.startPos, self.endPos)
		return result
