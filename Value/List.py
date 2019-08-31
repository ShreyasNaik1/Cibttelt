from Value import *
import sys
sys.path.insert(0, '../')
from Positions import * 
from Context import *

sys.path.insert(0, '../' + './Errors')
from errors import *
from RTError import *


class List(Value):
	def __init__(self, elements):
		super().__init__()
		self.elements = elements

	def add(self, other):
		newList = self.copy()
		newList.elements.append(other)
		return newList, None

	def sub(self, other):
		if isinstance(other, Number):
			newList = self.copy()
			try:
				newList.elements.pop(other.value)
				return newList, None
			except:
				return None, RTError(
					other.startPos, other.endPos,
					'Element at this index could not be removed from list because index is out of bounds',
					self.context
				)
		else:
			return None, Value.illegalOper(self, other)

	def mult(self, other):
		if isinstance(other, List):
			newList = self.copy()
			newList.elements.extend(other.elements)
			return newList, None
		else:
			return None, Value.illegalOper(self, other)

	def div(self, other):
		if isinstance(other, Number):
			try:
				return self.elements[other.value], None
			except:
				return None, RTError(
					other.startPos, other.endPos,
					'Element at this index could not be retrieved from list because index is out of bounds',
					self.context
				)
		else:
			return None, Value.illegalOper(self, other)
	
	def copy(self):
		copy = List(self.elements)
		copy.setPosition(self.startPos, self.endPos)
		copy.setContext(self.context)
		return copy

	def __str__(self):
		return ", ".join([str(x) for x in self.elements])

	def __repr__(self):
		return '[{", "}]'.join([repr(x) for x in self.elements])
