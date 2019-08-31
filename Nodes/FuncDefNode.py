
class FuncDefNode:
	def __init__(self, varToken, args, body, shouldReturn):
		self.varToken = varToken
		self.args = args
		self.body = body
		self.shouldReturn = shouldReturn

		if self.varToken:
			self.startPos = self.varToken.startPos
		elif len(self.args) > 0:
			self.startPos = self.args[0].startPos
		else:
			self.startPos = self.body.startPos

		self.endPos = self.body.endPos
