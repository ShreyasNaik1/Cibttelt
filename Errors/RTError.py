from errors import *

import sys

sys.path.insert(0, '../')
from string_with_arrows import *

class RTError(Error):
	def __init__(self, startPos, endPos, details, context):
		super().__init__(startPos, endPos, 'Runtime Error', details)
		self.context = context

	def printStr(self):
		result  = self.genTraceback()
		result += '{}: {}'.format(self.errorName, self.details)
		result += '\n\n' + string_with_arrows(self.startPos.fcontent, self.startPos, self.endPos)
		return result

	def genTraceback(self):
		result = ''
		pos = self.startPos
		ctx = self.context

		while ctx:
			result = '  File {}, line {}, in {}\n'.format(pos.fname, str(pos.ln + 1), ctx.dispName) + result
			pos = ctx.parentEntryPos
			ctx = ctx.parent

		return 'Traceback (most recent call last):\n' + result