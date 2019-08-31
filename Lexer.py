import sys 
sys.path.insert(0, './Errors')

from errors import *
from IllegalCharError import *
from ExpectedCharError import *

from constants import *
from Tokens import *
from Positions import *

class Lexer:
	def __init__(self, fname, text):
		self.fname = fname
		self.text = text
		self.pos = Position(-1, 0, -1, fname, text)
		self.currInput = None
		self.NextInput()
	
	def NextInput(self):
		self.pos.NextInput(self.currInput)
		self.currInput = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

	def genTok(self):
		tokens = []

		while self.currInput != None:
			if self.currInput in ' \t':
				self.NextInput()
			elif self.currInput == '#':
				self.ignoreCom()
			elif self.currInput in ';\n':
				tokens.append(Token(NEWLINE_T, startPos=self.pos))
				self.NextInput()
			elif self.currInput in DIGITS:
				tokens.append(self.GenNum())
			elif self.currInput in LETTERS:
				tokens.append(self.GenIdent())
			elif self.currInput == '"':
				tokens.append(self.GenStr())
			elif self.currInput == '+':
				tokens.append(Token(PLUS_T, startPos=self.pos))
				self.NextInput()
			elif self.currInput == '-':
				tokens.append(self.GenMinusArrow())
			elif self.currInput == '*':
				tokens.append(Token(MUL_T, startPos=self.pos))
				self.NextInput()
			elif self.currInput == '/':
				tokens.append(Token(DIV_T, startPos=self.pos))
				self.NextInput()
			elif self.currInput == '^':
				tokens.append(Token(POW_T, startPos=self.pos))
				self.NextInput()
			elif self.currInput == '(':
				tokens.append(Token(LPAREN_T, startPos=self.pos))
				self.NextInput()
			elif self.currInput == ')':
				tokens.append(Token(RPAREN_T, startPos=self.pos))
				self.NextInput()
			elif self.currInput == '[':
				tokens.append(Token(LSQUARE_T, startPos=self.pos))
				self.NextInput()
			elif self.currInput == ']':
				tokens.append(Token(RSQUARE_T, startPos=self.pos))
				self.NextInput()
			elif self.currInput == '!':
				token, error = self.GenNE()
				if error: return [], error
				tokens.append(token)
			elif self.currInput == '=':
				tokens.append(self.GenE())
			elif self.currInput == '<':
				tokens.append(self.GenLeq())
			elif self.currInput == '>':
				tokens.append(self.GenGeq())
			elif self.currInput == ',':
				tokens.append(Token(COMMA_T, startPos=self.pos))
				self.NextInput()
			else:
				startPos = self.pos.copy()
				char = self.currInput
				self.NextInput()
				return [], IllegalCharError(startPos, self.pos, "'" + char + "'")

		tokens.append(Token(EOF_T, startPos=self.pos))
		return tokens, None

	def GenNum(self):
		num = ''
		checkFloat = 0
		startPos = self.pos.copy()

		while self.currInput != None and self.currInput in DIGITS + '.':
			if self.currInput == '.':
				if checkFloat == 1: break
				checkFloat += 1
			num += self.currInput
			self.NextInput()

		if checkFloat == 0:
			return Token(INT_T, int(num), startPos, self.pos)
		else:
			return Token(FLOAT_T, float(num), startPos, self.pos)

	def GenStr(self):
		string = ''
		startPos = self.pos.copy()
		newTabLine = False
		self.NextInput()

		newTabLines = {
			'n': '\n',
			't': '\t'
		}

		while self.currInput != None and (self.currInput != '"' or newTabLine):
			if newTabLine:
				string += newTabLines.get(self.currInput, self.currInput)
			else:
				if self.currInput == '\\':
					newTabLine = True
				else:
					string += self.currInput
			self.NextInput()
			newTabLine = False
		
		self.NextInput()
		return Token(STRING_T, string, startPos, self.pos)

	def GenIdent(self):
		ident = ''
		startPos = self.pos.copy()

		while self.currInput != None and self.currInput in LETTERS_DIGITS + '_':
			ident += self.currInput
			self.NextInput()

		tokenType = KEYWORD_T if ident in KEYWORDS else IDENTIFIER_T
		return Token(tokenType, ident, startPos, self.pos)

	def GenMinusArrow(self):
		tokenType = MINUS_T
		startPos = self.pos.copy()
		self.NextInput()

		if self.currInput == '>':
			self.NextInput()
			tokenType = ARROW_T

		return Token(tokenType, startPos=startPos, endPos=self.pos)

	def GenNE(self):
		startPos = self.pos.copy()
		self.NextInput()

		if self.currInput == '=':
			self.NextInput()
			return Token(NE_T, startPos=startPos, endPos=self.pos), None

		self.NextInput()
		return None, ExpectedCharError(startPos, self.pos, "'=' (after '!')")
	
	def GenE(self):
		tokenType = EQUAL_T
		startPos = self.pos.copy()
		self.NextInput()

		if self.currInput == '=':
			self.NextInput()
			tokenType = EE_T

		return Token(tokenType, startPos=startPos, endPos=self.pos)

	def GenLeq(self):
		tokenType = LT_T
		startPos = self.pos.copy()
		self.NextInput()

		if self.currInput == '=':
			self.NextInput()
			tokenType = LTE_T

		return Token(tokenType, startPos=startPos, endPos=self.pos)

	def GenGeq(self):
		tokenType = GT_T
		startPos = self.pos.copy()
		self.NextInput()

		if self.currInput == '=':
			self.NextInput()
			tokenType = GTE_T

		return Token(tokenType, startPos=startPos, endPos=self.pos)

	def ignoreCom(self):
		self.NextInput()

		while self.currInput != '\n':
			self.NextInput()

		self.NextInput()