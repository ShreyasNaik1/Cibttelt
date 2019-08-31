import sys


sys.path.insert(0, '/home/shreyasnaik/Downloads/Projects/Mylang/Value')
from Value import *


sys.path.append('/home/shreyasnaik/Downloads/Projects/Mylang')
from Positions import * 
from Context import *
from SymbolTable import *
from RTResult import * 

sys.path.insert(0, '/home/shreyasnaik/Downloads/Projects/Mylang/Errors')
from errors import *
from RTError import *



class BaseFunction(Value):
	def __init__(self, name):
		super().__init__()
		self.name = name or "<anonymous>"

	def GenNewContext(self):
		newContext = Context(self.name, self.context, self.startPos)
		newContext.symbTable = SymbolTable(newContext.parent.symbTable)
		return newContext

	def CheckArgs(self, argName, args):
		res = RTResult()

		if len(args) > len(argName):
			return res.failure(RTError(
				self.startPos, self.endPos,
				"{len(args) - len(argName)} too many args passed into {self}",
				self.context
			))
		
		if len(args) < len(argName):
			return res.failure(RTError(
				self.startPos, self.endPos,
				"{len(argName) - len(args)} too few args passed into {self}",
				self.context
			))

		return res.success(None)

	def populateArg(self, argName, args, execCtX):
		for i in range(len(args)):
			argName = argName[i]
			argVal = args[i]
			argVal.setContext(execCtX)
			execCtX.symbTable.set(argName, argVal)

	def carefulPopulateArg(self, argName, args, execCtX):
		res = RTResult()
		res.register(self.CheckArgs(argName, args))
		if res.shouldReturn(): return res
		self.populateArg(argName, args, execCtX)
		return res.success(None)
