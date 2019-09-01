from BaseFunction import *


sys.path.insert(0, '../' + '../' + './Value')
from Value import *
from Number import *
from String import *


sys.path.append('../' + '../')
from Positions import * 
from Context import *
from RTResult import *
from Interpreter import *
from SymbolTable import *
from BaseFunction import BaseFunction

sys.path.insert(0, '../' + '../' + './Errors')
from errors import *
from RTError import *

class BuiltInFunction(BaseFunction):
	def __init__(self, name):
		super().__init__(name)

	def execute(self, args):
		res = RTResult()
		execCtX = self.GenNewContext()

		methodName = 'execute_{}'.format(self.name)
		method = getattr(self, methodName, self.noVisitMethod)

		res.register(self.carefulPopulateArg(method.argName, args, execCtX))
		if res.shouldReturn(): return res

		retVal = res.register(method(execCtX))
		if res.shouldReturn(): return res
		return res.success(retVal)
	
	def noVisitMethod(self, node, context):
		raise Exception('No execute_{} method defined'.format(self.name))

	def copy(self):
		copy = BuiltInFunction(self.name)
		copy.setContext(self.context)
		copy.setPosition(self.startPos, self.endPos)
		return copy

	def __repr__(self):
		return "<built-in function {self.name}>"

	#####################################

	def execPrint(self, execCtX):
		print(str(execCtX.symbTable.get('value')))
		return RTResult().success(Number.null)
	execPrint.argName = ['value']
	
	def execPrintRet(self, execCtX):
		return RTResult().success(String(str(execCtX.symbTable.get('value'))))
	execPrintRet.argName = ['value']
	
	def execInput(self, execCtX):
		text = input()
		return RTResult().success(String(text))
	execInput.argName = []

	def execInputInt(self, execCtX):
		while True:
			text = input()
			try:
				number = int(text)
				break
			except ValueError:
				print("'{}' must be an integer. Try again!".format(text))
		return RTResult().success(Number(number))
	execInputInt.argName = []

	def execClear(self, execCtX):
		os.system('cls' if os.name == 'nt' else 'cls') 
		return RTResult().success(Number.null)
	execClear.argName = []

	def execCheckNumber(self, execCtX):
		isNum = isinstance(execCtX.symbTable.get("value"), Number)
		return RTResult().success(Number.true if isNum else Number.false)
	execCheckNumber.argName = ["value"]

	def execCheckString(self, execCtX):
		isNum = isinstance(execCtX.symbTable.get("value"), String)
		return RTResult().success(Number.true if isNum else Number.false)
	execCheckString.argName = ["value"]

	def execCheckList(self, execCtX):
		isNum = isinstance(execCtX.symbTable.get("value"), List)
		return RTResult().success(Number.true if isNum else Number.false)
	execCheckList.argName = ["value"]

	def execCheckFunc(self, execCtX):
		isNum = isinstance(execCtX.symbTable.get("value"), BaseFunction)
		return RTResult().success(Number.true if isNum else Number.false)
	execCheckFunc.argName = ["value"]

	def execAppend(self, execCtX):
		list_ = execCtX.symbTable.get("list")
		value = execCtX.symbTable.get("value")

		if not isinstance(list_, List):
			return RTResult().failure(RTError(
				self.startPos, self.endPos,
				"First argument must be list",
				execCtX
			))

		list_.elements.append(value)
		return RTResult().success(Number.null)
	execAppend.argName = ["list", "value"]

	def execPop(self, execCtX):
		list_ = execCtX.symbTable.get("list")
		index = execCtX.symbTable.get("index")

		if not isinstance(list_, List):
			return RTResult().failure(RTError(
				self.startPos, self.endPos,
				"First argument must be list",
				execCtX
			))

		if not isinstance(index, Number):
			return RTResult().failure(RTError(
				self.startPos, self.endPos,
				"Second argument must be number",
				execCtX
			))

		try:
			element = list_.elements.pop(index.value)
		except:
			return RTResult().failure(RTError(
				self.startPos, self.endPos,
				'Element at this index could not be removed from list because index is out of bounds',
				execCtX
			))
		return RTResult().success(element)
	execPop.argName = ["list", "index"]

	def execExtend(self, execCtX):
		listA = execCtX.symbTable.get("listA")
		listB = execCtX.symbTable.get("listB")

		if not isinstance(listA, List):
			return RTResult().failure(RTError(
				self.startPos, self.endPos,
				"First argument must be list",
				execCtX
			))

		if not isinstance(listB, List):
			return RTResult().failure(RTError(
				self.startPos, self.endPos,
				"Second argument must be list",
				execCtX
			))

		listA.elements.extend(listB.elements)
		return RTResult().success(Number.null)
	execExtend.argName = ["listA", "listB"]

	def execLen(self, execCtX):
		list_ = execCtX.symbTable.get("list")

		if not isinstance(list_, List):
			return RTResult().failure(RTError(
				self.startPos, self.endPos,
				"Argument must be list",
				execCtX
			))

		return RTResult().success(Number(len(list_.elements)))
	execLen.argName = ["list"]

	def execRun(self, execCtX):
		fname = execCtX.symbTable.get("fname")

		if not isinstance(fname, String):
			return RTResult().failure(RTError(
				self.startPos, self.endPos,
				"Second argument must be string",
				execCtX
			))

		fname = fname.value

		try:
			with open(fname, "r") as f:
				script = f.read()
		except Exception as e:
			return RTResult().failure(RTError(
				self.startPos, self.endPos,
				"Failed to load script \"{}\"\n".format(fname) + str(e),
				execCtX
			))

		_, error = run(fname, script)
		
		if error:
			return RTResult().failure(RTError(
				self.startPos, self.endPos,
				"Failed to finish executing script \"{}\"\n".format(fname) +
				error.printStr(),
				execCtX
			))

		return RTResult().success(Number.null)
	execRun.argName = ["fname"]
