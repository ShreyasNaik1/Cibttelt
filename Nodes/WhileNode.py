
class WhileNode:
	def __init__(self, cond, body, returnNull):
		self.cond = cond
		self.body = body
		self.returnNull = returnNull

		self.startPos = self.cond.startPos
		self.endPos = self.body.endPos
