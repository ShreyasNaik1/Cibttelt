import sys

sys.path.insert(0, '../')
from Positions import * 
from Context import *
from RTResult import *

sys.path.insert(0, '../' + './Errors')
from errors import *
from RTError import *


class Value:
	def __init__(self):
		self.setPosition()
		self.setContext()

	def setPosition(self, startPos=None, endPos=None):
		self.startPos = startPos
		self.endPos = endPos
		return self

	def setContext(self, context=None):
		self.context = context
		return self

	def add(self, other):
		return None, self.illegalOper(other)

	def sub(self, other):
		return None, self.illegalOper(other)

	def mult(self, other):
		return None, self.illegalOper(other)

	def div(self, other):
		return None, self.illegalOper(other)

	def pow(self, other):
		return None, self.illegalOper(other)

	def compareEq(self, other):
		return None, self.illegalOper(other)

	def compareNE(self, other):
		return None, self.illegalOper(other)

	def compareLT(self, other):
		return None, self.illegalOper(other)

	def compareGT(self, other):
		return None, self.illegalOper(other)

	def compareLTE(self, other):
		return None, self.illegalOper(other)

	def compareGTE(self, other):
		return None, self.illegalOper(other)

	def andBool(self, other):
		return None, self.illegalOper(other)

	def orBool(self, other):
		return None, self.illegalOper(other)

	def notBool(self):
		return None, self.illegalOper(other)

	def execute(self, args):
		return RTResult().failure(self.illegalOper())

	def copy(self):
		raise Exception('No copy method defined')

	def isTrue(self):
		return False

	def illegalOper(self, other=None):
		if not other: other = self
		return RTError(
			self.startPos, other.endPos,
			'Illegal operation',
			self.context
		)





