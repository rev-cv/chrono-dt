
class chrono_catcher(object):
	"""Задает дату в chrono"""
	def __init__(self, arg):
		super(chrono_catcher, self).__init__()
		self.arg = arg
	
	def set(self, y, m, d, H, M, S, MS):
		type_y = type(y)

		if y is False:
			# no filling chrono
			pass
		elif y is None:
			# datetime now
			pass
		elif type_y is int:
			if type(m) is int and type(s) is int:
				# скорее всего передана дата цифрами 2021, 11, 5
				self.setDate(y, m, d)

				if 

				if type(H) is int:
					# переданы так же часы
					pass

				if type(M) is int:
					# переданы так же минуты
					pass

				if type(S) is int:
					# переданы так же секунды
					pass

				if type(MS) is int:
					# переданы так же милисекунды
					pass
			else:
				# скорее всего передана дата в UnixEpoch
				pass

		elif type_y is str:
			if y in self.RelativeIndication.keys():
				#имеется указание на год
				pass
			elif y in self.ObjectRequirement.keys():
				# требуется дата без создания chrono
				pass
			else:
				pass

		elif isinstance(y, chrono):
			# является ли объект chrono
			pass

		elif type_y is tuple:
			#Предположительно содержит (year, month, day, hour, minute, second)
			pass

		elif isinstance(y, QDateTime):
			# является ли объект QDateTime
			pass

		elif isinstance(b, QDate):
			# является ли объект QDate
			pass

			if isinstance(m, QTime):
				# является ли объект QTime
				pass

	def setTupleDate(self, y, m, s):
		# без вариантов приходит дата в виде цифр

	def setTupleTime(self, H, M, S):
		# без вариантов приходит время в виде цифр
		pass

	def setDate(self, y, m, d):
		pass

	def setTime(self, H, M, S):
		pass

	def setDateTime(self, y, m, d, H, M, S):
		self.set(y, m, d, H, M, S)

	def setString(self, string, *args):
		# Принимает строку и аргументы с помощью которых из строки будет извлечена дата/время
		# setString(string, "year", "month", "day", "hour", "minute", "second")
		# setString(string, "ymdHMS") #устанавливает относительную позицию
		pass

	def setNow(self):
		pass

	def setUnixEpoch(self, UnixEpoch):
		pass

	def setISO(self, string):
		pass

	def setReGex(self, string, regex):
		pass

	def setChrono(self, chrono):
		pass

	def setQDate(self, QDate):
		pass

	def setQTime(self, QTime):
		pass

	def setQdateTime(self, QDateTime):
		pass

