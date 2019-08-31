class Context:
	def __init__(self, dispName, parent=None, parentEntryPos=None):
		self.dispName = dispName
		self.parent = parent
		self.parentEntryPos = parentEntryPos
		self.symbTable = None