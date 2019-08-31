from BaseFunction import * 

import sys
sys.path.insert(0, '../' + '../' + './Value')
from Value import *


sys.path.append('../' + '../')
from Positions import * 
from Context import *
from Interpreter import *
from RTResult import *

sys.path.insert(0, '../' + '../' + './Errors')
from errors import *
from RTError import *


class Function(BaseFunction):
	def __init__(self, name, body, argName, shouldReturn):
		super().__init__(name)
		self.body = body
		self.argName = argName
		self.shouldReturn = shouldReturn

	def execute(self, args):
		res = RTResult()
		interpreter = Interpreter()
		execCtX = self.GenNewContext()

		res.register(self.carefulPopulateArg(self.argName, args, execCtX))
		if res.shouldReturn(): return res

		value = res.register(interpreter.visit(self.body, execCtX))
		if res.shouldReturn() and res.returnVal == None: return res

		retVal = (value if self.shouldReturn else None) or res.returnVal or Number.null
		return res.success(retVal)

	def copy(self):
		copy = Function(self.name, self.body, self.argName, self.shouldReturn)
		copy.setContext(self.context)
		copy.setPosition(self.startPos, self.endPos)
		return copy

	def __repr__(self):
		return "<function {self.name}>"
