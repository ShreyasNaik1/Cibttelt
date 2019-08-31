class Position:
	def __init__(self, idx, ln, col, fname, fcontent):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.fname = fname
		self.fcontent = fcontent

	def NextInput(self, currInput=None):
		self.idx += 1
		self.col += 1

		if currInput == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copy(self):
		return Position(self.idx, self.ln, self.col, self.fname, self.fcontent)