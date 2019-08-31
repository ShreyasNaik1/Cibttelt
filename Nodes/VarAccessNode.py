
class VarAccessNode:
	def __init__(self, varToken):
		self.varToken = varToken

		self.startPos = self.varToken.startPos
		self.endPos = self.varToken.endPos
