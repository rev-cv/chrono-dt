
class chrono_transformator(object):
	"""Изменяет внутреннее состояние chrono"""
	def __init__(self):
		super(chrono_transformator, self).__init__()
		self.RelativeIndication = {
			"now": self.setNow,
			"today": self.setNow,
			"tomorrow": partial(self.shift, **{"d": 1}),
			"yesterday": partial(self.shift, **{"d": -1}),
			"last day": partial(self.shift, **{"d": -1}),
			"next day": partial(self.shift, **{"d": 1}),

			"next week": partial(self.shift, **{"w": 1}),
			"last week": partial(self.shift, **{"w": -1}),
			
			"next decade": partial(self.shift, **{"d": 10}),
			"last decade": partial(self.shift, **{"d": -10}),

			"next month": partial(self.shift, **{"m": 1}),
			"last month": partial(self.shift, **{"m": -1}),

			"next year": partial(self.shift, **{"y": 1}),
			"last year": partial(self.shift, **{"y": -1}),
		}


		tomorrow, today, yesterday, a week ago, in a week, next week, last week

	def setTS(self, string):
		# Time Shift
		# вставка времени или текстовой команды смещения
		# пример: "00:25 +45"
		self.y = 2025

	def shiftTC(self, string):
		# Text Command
		# задание смещения текстовыми командами
		# пример: "+40d +45m -5h 4w" 
		pass

	def shiftRI(self, string):
		# Relative Indication
		func = self.RelativeIndication.get(string, False)
		if func is not None:
			func()

	def shift(self, y=None, m=None, w=None, d=None, H=None, M=None, S=None):
		pass

	def toTimeZone(self, TimeZone):
		pass

	def toUTC(self):
		pass

	def toLocal(self):
		pass




	# Имеются ли консенсус по поводу измерения даты на других солнечных объектах?
	# Год на Марсе все так же равняется 365/+1 суткам или 669 соло?
	# Если год на Марсе измеряется в соло, то какой тогда сегодня год на Марсе?

	# def toMars(self):
	# def toMoon(self):

