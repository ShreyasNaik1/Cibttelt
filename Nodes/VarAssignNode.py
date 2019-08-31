
class VarAssignNode:
	def __init__(self, varToken, valNode):
		self.varToken = varToken
		self.valNode = valNode

		self.startPos = self.varToken.startPos
		self.endPos = self.valNode.endPos
