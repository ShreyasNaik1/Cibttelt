
class CallNode:
	def __init__(self, callNode, args):
		self.callNode = callNode
		self.args = args

		self.startPos = self.callNode.startPos

		if len(self.args) > 0:
			self.endPos = self.args[len(self.args) - 1].endPos
		else:
			self.endPos = self.callNode.endPos
