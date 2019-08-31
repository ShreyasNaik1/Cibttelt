
class IfNode:
	def __init__(self, cases, elseCase):
		self.cases = cases
		self.elseCase = elseCase

		self.startPos = self.cases[0][0].startPos
		self.endPos = (self.elseCase or self.cases[len(self.cases) - 1])[0].endPos

