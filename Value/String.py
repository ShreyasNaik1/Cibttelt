from Value import *

import sys
sys.path.insert(0, '../')
from Positions import * 
from Context import *

sys.path.insert(0, '../' + './Errors')
from errors import *
from RTError import *


class String(Value):
	def __init__(self, value):
		super().__init__()
		self.value = value

	def add(self, other):
		if isinstance(other, String):
			return String(self.value + other.value).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def mult(self, other):
		if isinstance(other, Number):
			return String(self.value * other.value).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def isTrue(self):
		return len(self.value) > 0

	def copy(self):
		copy = String(self.value)
		copy.setPosition(self.startPos, self.endPos)
		copy.setContext(self.context)
		return copy

	def __str__(self):
		return self.value

	def __repr__(self):
		return '"{}"'.format(self.value)