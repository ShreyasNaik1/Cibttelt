
class RTResult:
	def __init__(self):
		self.reset()

	def reset(self):
		self.value = None
		self.error = None
		self.returnVal = None
		self.contLoop = False
		self.breakLoop = False

	def register(self, res):
		self.error = res.error
		self.returnVal = res.returnVal
		self.contLoop = res.contLoop
		self.breakLoop = res.breakLoop
		return res.value

	def success(self, value):
		self.reset()
		self.value = value
		return self

	def SuccRet(self, value):
		self.reset()
		self.returnVal = value
		return self
	
	def SuccCont(self):
		self.reset()
		self.contLoop = True
		return self

	def SuccBreak(self):
		self.reset()
		self.breakLoop = True
		return self

	def failure(self, error):
		self.reset()
		self.error = error
		return self

	def shouldReturn(self):
		return (
			self.error or
			self.returnVal or
			self.contLoop or
			self.breakLoop
		)