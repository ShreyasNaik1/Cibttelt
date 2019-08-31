
class UnaryOperationNode:
	def __init__(self, oper, node):
		self.oper = oper
		self.node = node

		self.startPos = self.oper.startPos
		self.endPos = node.endPos

	def __repr__(self):
		return '({}, {})'.format(self.oper, self.node)
