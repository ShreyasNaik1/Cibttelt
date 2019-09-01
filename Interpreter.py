from string_with_arrows import string_with_arrows  

import os

import sys

# sys.path.insert(0, './Errors')
# from import errors  
# from import InvalidSyntaxError  
# from import ExpectedCharError  
# from import IllegalCharError  
# from import RTError  

sys.path.insert(0, './Nodes')
from BinTreeNode import BinTreeNode  
from BreakNode import BreakNode  
from CallNode import CallNode   
from ContinueNode import ContinueNode  
from ForNode import ForNode   
from FuncDefNode import FuncDefNode  
from IfNode import IfNode   
from ListNode import ListNode   
from NumNode import NumNode  
from ReturnNode import ReturnNode  
from StrNode import StrNode  
from UnaryOperationNode import UnaryOperationNode  
from VarAccessNode import VarAccessNode  
from VarAssignNode import VarAssignNode  
from WhileNode import WhileNode  


from constants import * 
from Positions import Position 
from Tokens import *
from Lexer import Lexer 
from Parser import Parser
from RTResult import RTResult
from Context import Context  


sys.path.insert(0, './Value')
from Value import Value 
from List  import List 
from String  import String
from Number  import Number

sys.path.insert(0, './Value/BaseFunction')
from BaseFunction import BaseFunction

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
		elif node.oper.sameElem(KEYWORD_T, 'and'):
			result, error = left.andBool(right)
		elif node.oper.sameElem(KEYWORD_T, 'or'):
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
		elif node.oper.sameElem(KEYWORD_T, 'not'):
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

