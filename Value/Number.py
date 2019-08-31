from Value import *
import sys
sys.path.insert(0, '../')
from Positions import * 
from Context import *

sys.path.insert(0, '../' + './Errors')
from errors import *
from RTError import *

class Number(Value):
	def __init__(self, value):
		super().__init__()
		self.value = value

	def add(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def sub(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def mult(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def div(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RTError(
					other.startPos, other.endPos,
					'Division by zero',
					self.context
				)

			return Number(self.value / other.value).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def pow(self, other):
		if isinstance(other, Number):
			return Number(self.value ** other.value).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def compareEq(self, other):
		if isinstance(other, Number):
			return Number(int(self.value == other.value)).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def compareNE(self, other):
		if isinstance(other, Number):
			return Number(int(self.value != other.value)).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def compareLT(self, other):
		if isinstance(other, Number):
			return Number(int(self.value < other.value)).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def compareGT(self, other):
		if isinstance(other, Number):
			return Number(int(self.value > other.value)).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def compareLTE(self, other):
		if isinstance(other, Number):
			return Number(int(self.value <= other.value)).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def compareGTE(self, other):
		if isinstance(other, Number):
			return Number(int(self.value >= other.value)).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def andBool(self, other):
		if isinstance(other, Number):
			return Number(int(self.value and other.value)).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def orBool(self, other):
		if isinstance(other, Number):
			return Number(int(self.value or other.value)).setContext(self.context), None
		else:
			return None, Value.illegalOper(self, other)

	def notBool(self):
		return Number(1 if self.value == 0 else 0).setContext(self.context), None

	def copy(self):
		copy = Number(self.value)
		copy.setPosition(self.startPos, self.endPos)
		copy.setContext(self.context)
		return copy

	def isTrue(self):
		return self.value != 0

	def __str__(self):
		return str(self.value)
	
	def __repr__(self):
		return str(self.value)
