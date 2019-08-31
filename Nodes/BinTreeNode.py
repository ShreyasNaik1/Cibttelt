
class BinTreeNode:
	def __init__(self, left, oper, right):
		self.left = left
		self.oper = oper
		self.right = right

		self.startPos = self.left.startPos
		self.endPos = self.right.endPos

	def __repr__(self):
		return '({}, {}, {})'.format(self.left, self.oper, self.right)
