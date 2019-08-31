

class StrNode:
	def __init__(self, token):
		self.token = token

		self.startPos = self.token.startPos
		self.endPos = self.token.endPos

	def __repr__(self):
		return '{}'.format(self.token)
