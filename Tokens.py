from Positions import *


INT_T				= 'INT'
FLOAT_T    	= 'FLOAT'
STRING_T			= 'STRING'
IDENTIFIER_T	= 'IDENTIFIER'
KEYWORD_T		= 'KEYWORD'
PLUS_T     	= 'PLUS'
MINUS_T    	= 'MINUS'
MUL_T      	= 'MUL'
DIV_T      	= 'DIV'
POW_T				= 'POW'
EQUAL_T					= 'EQ'
LPAREN_T   	= 'LPAREN'
RPAREN_T   	= 'RPAREN'
LSQUARE_T    = 'LSQUARE'
RSQUARE_T    = 'RSQUARE'
EE_T					= 'EE'
NE_T					= 'NE'
LT_T					= 'LT'
GT_T					= 'GT'
LTE_T				= 'LTE'
GTE_T				= 'GTE'
COMMA_T			= 'COMMA'
ARROW_T			= 'ARROW'
NEWLINE_T		= 'NEWLINE'
EOF_T				= 'EOF'

KEYWORDS = [
	'var',
	'and',
	'or',
	'not',
	'if',
	'elif',
	'else',
	'for',
	'to',
	'step',
	'while',
	'fun',
	'then',
	'end',
	'return',
	'continue',
	'break',
]

class Token:
	def __init__(self, type_, value=None, startPos=None, endPos=None):
		self.type = type_
		self.value = value

		if startPos:
			self.startPos = startPos.copy()
			self.endPos = startPos.copy()
			self.endPos.NextInput()

		if endPos:
			self.endPos = endPos.copy()

	def sameElem(self, type_, value):
		return self.type == type_ and self.value == value
	
	def __repr__(self):
		if self.value: return '{}:{}'.format(self.type, self.value)
		return '{}'.format(self.type)