from ch_transformator import transformator_chrono

class chrono(chrono_transformator):
	"""docstring for chrono"""
	def __init__(self, y=None, m=None, d=None, H=None, M=None, S=None, 
		MS = None, shift=None, UTC=False, tz=None, auto=True):
		super(chrono, self).__init__()
		self.y = None
		self.m = None
		self.d = None
		self.H = None
		self.M = None
		self.S = None
		self.MS = round(dt.microsecond / 1000)
		self.tz = None
		

if __name__ == '__main__':
	a = chrono()
	a.setTS()

	print(a.y)