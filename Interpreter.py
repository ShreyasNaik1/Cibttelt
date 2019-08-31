#######################################
# IMPORTS
#######################################

from string_with_arrows import *

import os
import math

import sys

# sys.path.insert(0, './Errors')
# from errors import *
# from InvalidSyntaxError import *
# from ExpectedCharError import *
# from IllegalCharError import *
# from RTError import *

sys.path.insert(0, './Nodes')
from BinTreeNode import *
from BreakNode import *
from CallNode import * 
from ContinueNode import *
from ForNode import *
from FuncDefNode import *
from IfNode import *
from ListNode import *
from NumNode import *
from ReturnNode import *
from StrNode import *
from UnaryOperationNode import *
from VarAccessNode import *
from VarAssignNode import *
from WhileNode import *


from constants import *
from Positions import *
from Tokens import *
from Lexer import *
from Parser import *
from RTResult import *
from Context import *
from SymbolTable import *


sys.path.insert(0, './Value')
from Value import *
from List import *
from String import *
from Number import *

sys.path.insert(0, './Value/BaseFunction')
from BaseFunction import *
from Function import * 
from BuiltInFunction import * 



Number.null = Number(0)
Number.false = "false"
Number.true = "true"
Number.math_PI = Number(math.pi)

BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.printRet    = BuiltInFunction("printRet")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.inpInt   	= BuiltInFunction("inpInt")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.isNum   	= BuiltInFunction("isNum")
BuiltInFunction.isStr  	    = BuiltInFunction("isStr")
BuiltInFunction.isList      = BuiltInFunction("isList")
BuiltInFunction.isFunc 		= BuiltInFunction("isFunc")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.len			= BuiltInFunction("len")
BuiltInFunction.run			= BuiltInFunction("run")




class Interpreter:
	def visit(self, node, context):
		methodName = 'Visit{}'.format(type(node).__name__)
		method = getattr(self, methodName, self.noVisitMethod)
		return method(node, context)

	def noVisitMethod(self, node, context):
		raise Exception('No Visit{} method defined'.format(type(node).__name__))


	def VisitNumNode(self, node, context):
		return RTResult().success(
			Number(node.token.value).setContext(context).setPosition(node.startPos, node.endPos)
		)

	def VisitStrNode(self, node, context):
		return RTResult().success(
			String(node.token.value).setContext(context).setPosition(node.startPos, node.endPos)
		)

	def VisitListNode(self, node, context):
		res = RTResult()
		elements = []

		for elemNode in node.listElements:
			elements.append(res.register(self.visit(elemNode, context)))
			if res.shouldReturn(): return res

		return res.success(
			List(elements).setContext(context).setPosition(node.startPos, node.endPos)
		)

	def VisitVarAccessNode(self, node, context):
		res = RTResult()
		varName = node.varToken.value
		value = context.symbTable.get(varName)

		if not value:
			return res.failure(RTError(
				node.startPos, node.endPos,
				"'{}' is not defined".format(varName),
				context
			))

		value = value.copy().setPosition(node.startPos, node.endPos).setContext(context)
		return res.success(value)

	def VisitVarAssignNode(self, node, context):
		res = RTResult()
		varName = node.varToken.value
		value = res.register(self.visit(node.valNode, context))
		if res.shouldReturn(): return res

		context.symbTable.set(varName, value)
		return res.success(value)

	def VisitBinTreeNode(self, node, context):
		res = RTResult()
		left = res.register(self.visit(node.left, context))
		if res.shouldReturn(): return res
		right = res.register(self.visit(node.right, context))
		if res.shouldReturn(): return res

		if node.oper.type == PLUS_T:
			result, error = left.add(right)
		elif node.oper.type == MINUS_T:
			result, error = left.sub(right)
		elif node.oper.type == MUL_T:
			result, error = left.mult(right)
		elif node.oper.type == DIV_T:
			result, error = left.div(right)
		elif node.oper.type == POW_T:
			result, error = left.pow(right)
		elif node.oper.type == EE_T:
			result, error = left.compareEq(right)
		elif node.oper.type == NE_T:
			result, error = left.compareNE(right)
		elif node.oper.type == LT_T:
			result, error = left.compareLT(right)
		elif node.oper.type == GT_T:
			result, error = left.compareGT(right)
		elif node.oper.type == LTE_T:
			result, error = left.compareLTE(right)
		elif node.oper.type == GTE_T:
			result, error = left.compareGTE(right)
		elif node.oper.sameElem(KEYWORD_T, 'AND'):
			result, error = left.andBool(right)
		elif node.oper.sameElem(KEYWORD_T, 'OR'):
			result, error = left.orBool(right)

		if error:
			return res.failure(error)
		else:
			return res.success(result.setPosition(node.startPos, node.endPos))

	def VisitUnaryOperationNode(self, node, context):
		res = RTResult()
		number = res.register(self.visit(node.node, context))
		if res.shouldReturn(): return res

		error = None

		if node.oper.type == MINUS_T:
			number, error = number.mult(Number(-1))
		elif node.oper.sameElem(KEYWORD_T, 'NOT'):
			number, error = number.notBool()

		if error:
			return res.failure(error)
		else:
			return res.success(number.setPosition(node.startPos, node.endPos))

	def VisitIfNode(self, node, context):
		res = RTResult()

		for condition, expr, returnNull in node.cases:
			condVal = res.register(self.visit(condition, context))
			if res.shouldReturn(): return res

			if condVal.isTrue():
				exprVal = res.register(self.visit(expr, context))
				if res.shouldReturn(): return res
				return res.success(Number.null if returnNull else exprVal)

		if node.elseCase:
			expr, returnNull = node.elseCase
			exprVal = res.register(self.visit(expr, context))
			if res.shouldReturn(): return res
			return res.success(Number.null if returnNull else exprVal)

		return res.success(Number.null)

	def VisitForNode(self, node, context):
		res = RTResult()
		elements = []

		startVal = res.register(self.visit(node.startVal, context))
		if res.shouldReturn(): return res

		endVal = res.register(self.visit(node.endVal, context))
		if res.shouldReturn(): return res

		if node.stepVal:
			stepVal = res.register(self.visit(node.stepVal, context))
			if res.shouldReturn(): return res
		else:
			stepVal = Number(1)

		i = startVal.value

		if stepVal.value >= 0:
			condition = lambda: i < endVal.value
		else:
			condition = lambda: i > endVal.value
		
		while condition():
			context.symbTable.set(node.varToken.value, Number(i))
			i += stepVal.value

			value = res.register(self.visit(node.body, context))
			if res.shouldReturn() and res.contLoop == False and res.breakLoop == False: return res
			
			if res.contLoop:
				continue
			
			if res.breakLoop:
				break

			elements.append(value)

		return res.success(
			Number.null if node.returnNull else
			List(elements).setContext(context).setPosition(node.startPos, node.endPos)
		)

	def VisitWhileNode(self, node, context):
		res = RTResult()
		elements = []

		while True:
			condition = res.register(self.visit(node.cond, context))
			if res.shouldReturn(): return res

			if not condition.isTrue():
				break

			value = res.register(self.visit(node.body, context))
			if res.shouldReturn() and res.contLoop == False and res.breakLoop == False: return res

			if res.contLoop:
				continue
			
			if res.breakLoop:
				break

			elements.append(value)

		return res.success(
			Number.null if node.returnNull else
			List(elements).setContext(context).setPosition(node.startPos, node.endPos)
		)

	def VisitFuncDefNode(self, node, context):
		res = RTResult()

		funcName = node.varToken.value if node.varToken else None
		body = node.body
		argName = [argName.value for argName in node.args]
		funcVal = Function(funcName, body, argName, node.shouldReturn).setContext(context).setPosition(node.startPos, node.endPos)
		
		if node.varToken:
			context.symbTable.set(funcName, funcVal)

		return res.success(funcVal)

	def VisitCallNode(self, node, context):
		res = RTResult()
		args = []

		callVal = res.register(self.visit(node.callNode, context))
		if res.shouldReturn(): return res
		callVal = callVal.copy().setPosition(node.startPos, node.endPos)

		for argNode in node.args:
			args.append(res.register(self.visit(argNode, context)))
			if res.shouldReturn(): return res

		retVal = res.register(callVal.execute(args))
		if res.shouldReturn(): return res
		retVal = retVal.copy().setPosition(node.startPos, node.endPos).setContext(context)
		return res.success(retVal)

	def VisitReturnNode(self, node, context):
		res = RTResult()

		if node.returnNode:
			value = res.register(self.visit(node.returnNode, context))
			if res.shouldReturn(): return res
		else:
			value = Number.null
		
		return res.SuccRet(value)

	def VisitContinueNode(self, node, context):
		return RTResult().SuccCont()

	def VisitBreakNode(self, node, context):
		return RTResult().SuccBreak()




GlobalSymTable = SymbolTable()
GlobalSymTable.set("NULL", Number.null)
GlobalSymTable.set("FALSE", Number.false)
GlobalSymTable.set("TRUE", Number.true)
GlobalSymTable.set("MATH_PI", Number.math_PI)
GlobalSymTable.set("PRINT", BuiltInFunction.print)
GlobalSymTable.set("PRINT_RET", BuiltInFunction.printRet)
GlobalSymTable.set("INPUT", BuiltInFunction.input)
GlobalSymTable.set("INPUT_INT", BuiltInFunction.inpInt)
GlobalSymTable.set("CLEAR", BuiltInFunction.clear)
GlobalSymTable.set("CLS", BuiltInFunction.clear)
GlobalSymTable.set("IS_NUM", BuiltInFunction.isNum)
GlobalSymTable.set("IS_STR", BuiltInFunction.isStr)
GlobalSymTable.set("IS_LIST", BuiltInFunction.isList)
GlobalSymTable.set("IS_FUN", BuiltInFunction.isFunc)
GlobalSymTable.set("APPEND", BuiltInFunction.append)
GlobalSymTable.set("POP", BuiltInFunction.pop)
GlobalSymTable.set("EXTEND", BuiltInFunction.extend)
GlobalSymTable.set("LEN", BuiltInFunction.len)
GlobalSymTable.set("RUN", BuiltInFunction.run)

def run(fname, text):
	lexer = Lexer(fname, text)
	tokens, error = lexer.genTok()
	if error: return None, error
	
	parser = Parser(tokens)
	bTree = parser.parse()
	if bTree.error: return None, bTree.error

	interpreter = Interpreter()
	context = Context('<program>')
	context.symbTable = GlobalSymTable
	result = interpreter.visit(bTree.node, context)

	return result.value, result.error
