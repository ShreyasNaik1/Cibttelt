class ForNode:
	def __init__(self, varToken, startVal, endVal, stepVal, body, returnNull):
		self.varToken = varToken
		self.startVal = startVal
		self.endVal = endVal
		self.stepVal = stepVal
		self.body = body
		self.returnNull = returnNull

		self.startPos = self.varToken.startPos
		self.endPos = self.body.endPos
