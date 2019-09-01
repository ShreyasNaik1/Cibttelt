import sys
sys.path.insert(0, './Errors')

from errors import * 
from InvalidSyntaxError import *
from Tokens import *

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

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None
		self.lastRegNextInpCount = 0
		self.nextInputCount = 0
		self.reverseCount = 0

	def RegisterNextInp(self):
		self.lastRegNextInpCount = 1
		self.nextInputCount += 1

	def register(self, res):
		self.lastRegNextInpCount = res.nextInputCount
		self.nextInputCount += res.nextInputCount
		if res.error: self.error = res.error
		return res.node

	def tryReg(self, res):
		if res.error:
			self.reverseCount = res.nextInputCount
			return None
		return self.register(res)

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		if not self.error or self.lastRegNextInpCount == 0:
			self.error = error
		return self

#######################################
# PARSER
#######################################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tokenIndex = -1
		self.NextInput()

	def NextInput(self):
		self.tokenIndex += 1
		self.updateToken()
		return self.currTok

	def reverse(self, amount=1):
		self.tokenIndex -= amount
		self.updateToken()
		return self.currTok

	def updateToken(self):
		if self.tokenIndex >= 0 and self.tokenIndex < len(self.tokens):
			self.currTok = self.tokens[self.tokenIndex]

	def parse(self):
		res = self.statements()
		if not res.error and self.currTok.type != EOF_T:
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Token cannot appear after previous tokens"
			))
		return res

	###################################

	def statements(self):
		res = ParseResult()
		statements = []
		startPos = self.currTok.startPos.copy()

		while self.currTok.type == NEWLINE_T:
			res.RegisterNextInp()
			self.NextInput()

		statement = res.register(self.statement())
		if res.error: return res
		statements.append(statement)

		moreStat = True

		while True:
			newlineCount = 0
			while self.currTok.type == NEWLINE_T:
				res.RegisterNextInp()
				self.NextInput()
				newlineCount += 1
			if newlineCount == 0:
				moreStat = False
			
			if not moreStat: break
			statement = res.tryReg(self.statement())
			if not statement:
				self.reverse(res.reverseCount)
				moreStat = False
				continue
			statements.append(statement)

		return res.success(ListNode(
			statements,
			startPos,
			self.currTok.endPos.copy()
		))

	def statement(self):
		res = ParseResult()
		startPos = self.currTok.startPos.copy()

		if self.currTok.sameElem(KEYWORD_T, 'RETURN'):
			res.RegisterNextInp()
			self.NextInput()

			expr = res.tryReg(self.expr())
			if not expr:
				self.reverse(res.reverseCount)
			return res.success(ReturnNode(expr, startPos, self.currTok.startPos.copy()))
		
		if self.currTok.sameElem(KEYWORD_T, 'CONTINUE'):
			res.RegisterNextInp()
			self.NextInput()
			return res.success(ContinueNode(startPos, self.currTok.startPos.copy()))
			
		if self.currTok.sameElem(KEYWORD_T, 'BREAK'):
			res.RegisterNextInp()
			self.NextInput()
			return res.success(BreakNode(startPos, self.currTok.startPos.copy()))

		expr = res.register(self.expr())
		if res.error:
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected 'RETURN', 'CONTINUE', 'BREAK', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
			))
		return res.success(expr)

	def expr(self):
		res = ParseResult()

		if self.currTok.sameElem(KEYWORD_T, 'var'):
			res.RegisterNextInp()
			self.NextInput()

			if self.currTok.type != IDENTIFIER_T:
				return res.failure(InvalidSyntaxError(
					self.currTok.startPos, self.currTok.endPos,
					"Expected identifier"
				))

			varName = self.currTok
			res.RegisterNextInp()
			self.NextInput()

			if self.currTok.type != EQUAL_T:
				return res.failure(InvalidSyntaxError(
					self.currTok.startPos, self.currTok.endPos,
					"Expected '='"
				))

			res.RegisterNextInp()
			self.NextInput()
			expr = res.register(self.expr())
			if res.error: return res
			return res.success(VarAssignNode(varName, expr))

		node = res.register(self.BinaryTree(self.ComputeExpression, ((KEYWORD_T, 'and'), (KEYWORD_T, 'or'))))

		if res.error:
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected 'var', 'if', 'for', 'while', 'fun', int, float, identifier, '+', '-', '(', '[' or 'not'"
			))

		return res.success(node)

	def ComputeExpression(self):
		res = ParseResult()

		if self.currTok.sameElem(KEYWORD_T, 'NOT'):
			oper = self.currTok
			res.RegisterNextInp()
			self.NextInput()

			node = res.register(self.ComputeExpression())
			if res.error: return res
			return res.success(UnaryOperationNode(oper, node))
		
		node = res.register(self.BinaryTree(self.arithExpr, (EE_T, NE_T, LT_T, GT_T, LTE_T, GTE_T)))
		
		if res.error:
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected int, float, identifier, '+', '-', '(', '[', 'if', 'for', 'while', 'fun', or 'not'"
			))

		return res.success(node)

	def arithExpr(self):
		return self.BinaryTree(self.term, (PLUS_T, MINUS_T))

	def term(self):
		return self.BinaryTree(self.factor, (MUL_T, DIV_T))

	def factor(self):
		res = ParseResult()
		token = self.currTok

		if token.type in (PLUS_T, MINUS_T):
			res.RegisterNextInp()
			self.NextInput()
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOperationNode(token, factor))

		return self.power()

	def power(self):
		return self.BinaryTree(self.call, (POW_T, ), self.factor)

	def call(self):
		res = ParseResult()
		atom = res.register(self.atom())
		if res.error: return res

		if self.currTok.type == LPAREN_T:
			res.RegisterNextInp()
			self.NextInput()
			args = []

			if self.currTok.type == RPAREN_T:
				res.RegisterNextInp()
				self.NextInput()
			else:
				args.append(res.register(self.expr()))
				if res.error:
					return res.failure(InvalidSyntaxError(
						self.currTok.startPos, self.currTok.endPos,
						"Expected ')', 'var', 'if', 'for', 'while', 'fun', int, float, identifier, '+', '-', '(', '[' or 'not'"
					))

				while self.currTok.type == COMMA_T:
					res.RegisterNextInp()
					self.NextInput()

					args.append(res.register(self.expr()))
					if res.error: return res

				if self.currTok.type != RPAREN_T:
					return res.failure(InvalidSyntaxError(
						self.currTok.startPos, self.currTok.endPos,
						"Expected ',' or ')'"
					))

				res.RegisterNextInp()
				self.NextInput()
			return res.success(CallNode(atom, args))
		return res.success(atom)

	def atom(self):
		res = ParseResult()
		token = self.currTok

		if token.type in (INT_T, FLOAT_T):
			res.RegisterNextInp()
			self.NextInput()
			return res.success(NumNode(token))

		elif token.type == STRING_T:
			res.RegisterNextInp()
			self.NextInput()
			return res.success(StrNode(token))

		elif token.type == IDENTIFIER_T:
			res.RegisterNextInp()
			self.NextInput()
			return res.success(VarAccessNode(token))

		elif token.type == LPAREN_T:
			res.RegisterNextInp()
			self.NextInput()
			expr = res.register(self.expr())
			if res.error: return res
			if self.currTok.type == RPAREN_T:
				res.RegisterNextInp()
				self.NextInput()
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.currTok.startPos, self.currTok.endPos,
					"Expected ')'"
				))

		elif token.type == LSQUARE_T:
			ListExpr = res.register(self.ListExpr())
			if res.error: return res
			return res.success(ListExpr)
		
		elif token.sameElem(KEYWORD_T, 'if'):
			IfExpr = res.register(self.IfExpr())
			if res.error: return res
			return res.success(IfExpr)

		elif token.sameElem(KEYWORD_T, 'for'):
			ForExpr = res.register(self.ForExpr())
			if res.error: return res
			return res.success(ForExpr)

		elif token.sameElem(KEYWORD_T, 'while'):
			WhileExpr = res.register(self.WhileExpr())
			if res.error: return res
			return res.success(WhileExpr)

		elif token.sameElem(KEYWORD_T, 'fun'):
			FuncDef = res.register(self.FuncDef())
			if res.error: return res
			return res.success(FuncDef)

		return res.failure(InvalidSyntaxError(
			token.startPos, token.endPos,
			"Expected int, float, identifier, '+', '-', '(', '[', 'if', 'for', 'while', 'fun'"
		))

	def ListExpr(self):
		res = ParseResult()
		listElements = []
		startPos = self.currTok.startPos.copy()

		if self.currTok.type != LSQUARE_T:
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected '['"
			))

		res.RegisterNextInp()
		self.NextInput()

		if self.currTok.type == RSQUARE_T:
			res.RegisterNextInp()
			self.NextInput()
		else:
			listElements.append(res.register(self.expr()))
			if res.error:
				return res.failure(InvalidSyntaxError(
					self.currTok.startPos, self.currTok.endPos,
					"Expected ']', 'var', 'if', 'for', 'while', 'fun', int, float, identifier, '+', '-', '(', '[' or 'not'"
				))

			while self.currTok.type == COMMA_T:
				res.RegisterNextInp()
				self.NextInput()

				listElements.append(res.register(self.expr()))
				if res.error: return res

			if self.currTok.type != RSQUARE_T:
				return res.failure(InvalidSyntaxError(
					self.currTok.startPos, self.currTok.endPos,
					"Expected ',' or ']'"
				))

			res.RegisterNextInp()
			self.NextInput()

		return res.success(ListNode(
			listElements,
			startPos,
			self.currTok.endPos.copy()
		))

	def IfExpr(self):
		res = ParseResult()
		allCases = res.register(self.CasesOfIf('if'))
		if res.error: return res
		cases, elseCase = allCases
		return res.success(IfNode(cases, elseCase))

	def ElifCaseOfIf(self):
		return self.CasesOfIf('elif')
		
	def ElseCaseOfIf(self):
		res = ParseResult()
		elseCase = None

		if self.currTok.sameElem(KEYWORD_T, 'else'):
			res.RegisterNextInp()
			self.NextInput()

			if self.currTok.type == NEWLINE_T:
				res.RegisterNextInp()
				self.NextInput()

				statements = res.register(self.statements())
				if res.error: return res
				elseCase = (statements, True)

				if self.currTok.sameElem(KEYWORD_T, 'end'):
					res.RegisterNextInp()
					self.NextInput()
				else:
					return res.failure(InvalidSyntaxError(
						self.currTok.startPos, self.currTok.endPos,
						"Expected 'end'"
					))
			else:
				expr = res.register(self.statement())
				if res.error: return res
				elseCase = (expr, False)

		return res.success(elseCase)

	def ElCasesOfIf(self):
		res = ParseResult()
		cases, elseCase = [], None

		if self.currTok.sameElem(KEYWORD_T, 'elif'):
			allCases = res.register(self.ElifCaseOfIf())
			if res.error: return res
			cases, elseCase = allCases
		else:
			elseCase = res.register(self.ElseCaseOfIf())
			if res.error: return res
		
		return res.success((cases, elseCase))

	def CasesOfIf(self, chooseBorC):
		res = ParseResult()
		cases = []
		elseCase = None

		if not self.currTok.sameElem(KEYWORD_T, chooseBorC):
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected '{chooseBorC}'"
			))

		res.RegisterNextInp()
		self.NextInput()

		condition = res.register(self.expr())
		if res.error: return res

		if not self.currTok.sameElem(KEYWORD_T, 'then'):
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected 'then'"
			))

		res.RegisterNextInp()
		self.NextInput()

		if self.currTok.type == NEWLINE_T:
			res.RegisterNextInp()
			self.NextInput()

			statements = res.register(self.statements())
			if res.error: return res
			cases.append((condition, statements, True))

			if self.currTok.sameElem(KEYWORD_T, 'end'):
				res.RegisterNextInp()
				self.NextInput()
			else:
				allCases = res.register(self.ElCasesOfIf())
				if res.error: return res
				newCases, elseCase = allCases
				cases.extend(newCases)
		else:
			expr = res.register(self.statement())
			if res.error: return res
			cases.append((condition, expr, False))

			allCases = res.register(self.ElCasesOfIf())
			if res.error: return res
			newCases, elseCase = allCases
			cases.extend(newCases)

		return res.success((cases, elseCase))

	def ForExpr(self):
		res = ParseResult()

		if not self.currTok.sameElem(KEYWORD_T, 'for'):
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected 'FOR'"
			))

		res.RegisterNextInp()
		self.NextInput()

		if self.currTok.type != IDENTIFIER_T:
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected identifier"
			))

		varName = self.currTok
		res.RegisterNextInp()
		self.NextInput()

		if self.currTok.type != EQUAL_T:
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected '='"
			))
		
		res.RegisterNextInp()
		self.NextInput()

		startVal = res.register(self.expr())
		if res.error: return res

		if not self.currTok.sameElem(KEYWORD_T, 'to'):
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected 'to'"
			))
		
		res.RegisterNextInp()
		self.NextInput()

		endVal = res.register(self.expr())
		if res.error: return res

		if self.currTok.sameElem(KEYWORD_T, 'step'):
			res.RegisterNextInp()
			self.NextInput()

			stepVal = res.register(self.expr())
			if res.error: return res
		else:
			stepVal = None

		if not self.currTok.sameElem(KEYWORD_T, 'then'):
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected 'then'"
			))

		res.RegisterNextInp()
		self.NextInput()

		if self.currTok.type == NEWLINE_T:
			res.RegisterNextInp()
			self.NextInput()

			body = res.register(self.statements())
			if res.error: return res

			if not self.currTok.sameElem(KEYWORD_T, 'end'):
				return res.failure(InvalidSyntaxError(
					self.currTok.startPos, self.currTok.endPos,
					"Expected 'end'"
				))

			res.RegisterNextInp()
			self.NextInput()

			return res.success(ForNode(varName, startVal, endVal, stepVal, body, True))
		
		body = res.register(self.statement())
		if res.error: return res

		return res.success(ForNode(varName, startVal, endVal, stepVal, body, False))

	def WhileExpr(self):
		res = ParseResult()

		if not self.currTok.sameElem(KEYWORD_T, 'while'):
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected 'while'"
			))

		res.RegisterNextInp()
		self.NextInput()

		condition = res.register(self.expr())
		if res.error: return res

		if not self.currTok.sameElem(KEYWORD_T, 'then'):
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected 'then'"
			))

		res.RegisterNextInp()
		self.NextInput()

		if self.currTok.type == NEWLINE_T:
			res.RegisterNextInp()
			self.NextInput()

			body = res.register(self.statements())
			if res.error: return res

			if not self.currTok.sameElem(KEYWORD_T, 'end'):
				return res.failure(InvalidSyntaxError(
					self.currTok.startPos, self.currTok.endPos,
					"Expected 'end'"
				))

			res.RegisterNextInp()
			self.NextInput()

			return res.success(WhileNode(condition, body, True))
		
		body = res.register(self.statement())
		if res.error: return res

		return res.success(WhileNode(condition, body, False))

	def FuncDef(self):
		res = ParseResult()

		if not self.currTok.sameElem(KEYWORD_T, 'fun'):
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected 'fun'"
			))

		res.RegisterNextInp()
		self.NextInput()

		if self.currTok.type == IDENTIFIER_T:
			varToken = self.currTok
			res.RegisterNextInp()
			self.NextInput()
			if self.currTok.type != LPAREN_T:
				return res.failure(InvalidSyntaxError(
					self.currTok.startPos, self.currTok.endPos,
					"Expected '('"
				))
		else:
			varToken = None
			if self.currTok.type != LPAREN_T:
				return res.failure(InvalidSyntaxError(
					self.currTok.startPos, self.currTok.endPos,
					"Expected identifier or '('"
				))
		
		res.RegisterNextInp()
		self.NextInput()
		args = []

		if self.currTok.type == IDENTIFIER_T:
			args.append(self.currTok)
			res.RegisterNextInp()
			self.NextInput()
			
			while self.currTok.type == COMMA_T:
				res.RegisterNextInp()
				self.NextInput()

				if self.currTok.type != IDENTIFIER_T:
					return res.failure(InvalidSyntaxError(
						self.currTok.startPos, self.currTok.endPos,
						"Expected identifier"
					))

				args.append(self.currTok)
				res.RegisterNextInp()
				self.NextInput()
			
			if self.currTok.type != RPAREN_T:
				return res.failure(InvalidSyntaxError(
					self.currTok.startPos, self.currTok.endPos,
					"Expected ',' or ')'"
				))
		else:
			if self.currTok.type != RPAREN_T:
				return res.failure(InvalidSyntaxError(
					self.currTok.startPos, self.currTok.endPos,
					"Expected identifier or ')'"
				))

		res.RegisterNextInp()
		self.NextInput()

		if self.currTok.type == ARROW_T:
			res.RegisterNextInp()
			self.NextInput()

			body = res.register(self.expr())
			if res.error: return res

			return res.success(FuncDefNode(
				varToken,
				args,
				body,
				True
			))
		
		if self.currTok.type != NEWLINE_T:
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected '->' or newline"
			))

		res.RegisterNextInp()
		self.NextInput()

		body = res.register(self.statements())
		if res.error: return res

		if not self.currTok.sameElem(KEYWORD_T, 'end'):
			return res.failure(InvalidSyntaxError(
				self.currTok.startPos, self.currTok.endPos,
				"Expected 'end'"
			))

		res.RegisterNextInp()
		self.NextInput()
		
		return res.success(FuncDefNode(
			varToken,
			args,
			body,
			False
		))

	###################################

	def BinaryTree(self, func_a, ops, func_b=None):
		if func_b == None:
			func_b = func_a
		
		res = ParseResult()
		left = res.register(func_a())
		if res.error: return res

		while self.currTok.type in ops or (self.currTok.type, self.currTok.value) in ops:
			oper = self.currTok
			res.RegisterNextInp()
			self.NextInput()
			right = res.register(func_b())
			if res.error: return res
			left = BinTreeNode(left, oper, right)

		return res.success(left)