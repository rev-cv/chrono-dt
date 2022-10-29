import sys
from datetime import datetime

class chrono_catcher(object):
	"""Задает дату в chrono"""
	def __init__(self):
		super(chrono_catcher, self).__init__()

		self.ObjectRequirement = {
			"ms": "требование текущего времени в милисекундах",
			"ns": "требование текущего времени в наносекундах",
			"s": "требование текущего времени в UnixEpoch",
			"UTC": "требование текущего времени в UnixEpoch",
			"utc": "требование текущего времени в UnixEpoch",
			"dt": "требование текущего времени в python datetime",
			"datetime": "требование текущего времени в python datetime",
			"date": "требование текущего времени в python date",
			"tuple": "требование текущего времени в python tuple",
			"QDT": "требование текущего времени в QDateTime",
			"QDateTime": "требование текущего времени в QDateTime",
		}
	
	def set(self, 
			y = None, 
			m = None, 
			d = None, 
			H = None, 
			M = None, 
			S = None, 
		):
		type_y = type(y)

		if y is False:
			# no filling chrono
			# chrono(False) — такая конструкция нужна
			# чтобы миновать довольно тяжеловесный метод .set()
			# и перейти к специализированным функциям типа setUnixEpoch
			pass

		elif y is None:
			# datetime now
			self.setNow()

		elif type_y is int:
			if type(m) is int and type(d) is int:
				# скорее всего передана дата цифрами 2021, 11, 5
				# дата может прийти лишь полностью
				self.setDate(y, m, d)

				type_H = type(H)
				type_M = type(M)
				type_S = type(S)

				if type_H is int and type_M is int and type_S is int:
					# время передано полностью
					self.setTime(H, M, S)

				elif type_H is int and type_M is int:
					# передано время без секунд
					# секунды присваиваются автоматически — 0
					self.setTime(H, M, 0)

				elif type_H is int:
					# передано время без минут и секунд
					# секунды и минуты присваиваются автоматически
					self.setTime(H, 0, 0)

			else:
				# скорее всего передана дата в UnixEpoch
				pass

		elif type_y is str:
			# if y in self.RelativeIndication.keys():
			# 	#имеется указание на дату
			# 	self.RelativeIndication.get(y)()
			# 	pass
			if y.lower() == "now":
				self.setNow()
			elif y in self.ObjectRequirement.keys():
				# требуется возвратить текущее время, но не chrono
				self.setNow()
			else:
				# разбирает строку в которой предположительно имеется
				# последовательность y, m, d, H, M, S
				# при этом эта последовательность может быть разделена
				# любыми символами в любом количестве
				# или разделение может не быть вовсе
				# Например, обработаются обе строки
				# 2022-12-12 04:12:55
				# 20221212041255
				date, time = self.deconstruction_date(y)
				self.setTupleDate(*date)
				self.setTupleTime(*time)

		elif isinstance(y, datetime):
			self.setDT(y)

		elif isinstance(y, self.chrono):
			# является ли объект chrono
			self.setChrono(y)

		elif type_y is tuple or type_y is list:
			#Предположительно содержит (year, month, day, hour, minute, second)
			self.setDateTime(*y)

		# elif isinstance(y, QDateTime):
		# 	# является ли объект QDateTime
		# 	pass

		# elif isinstance(y, QDate):
		# 	# является ли объект QDate
		# 	pass

		# 	if isinstance(m, QTime):
		# 		# является ли объект QTime
		# 		pass

		elif 'PyQt5.QtCore.QDateTime' in str(type_y):
			# так сделано, чтобы не импортировать PyQt до того пока действительно не будет нужен
			self.setQDateTime(y)

		elif 'PyQt5.QtCore.QDate' in str(type_y):
			# так сделано, чтобы не импортировать PyQt до того пока действительно не будет нужен
			self.setQDate(y)
			if 'PyQt5.QtCore.QTime' in str(type(type_m)):
				self.setQTime(m)

		return self

	def setTupleDate(self, y, m, d):
		# без вариантов приходит дата в виде цифр
		# задается без проверки
		self.y, self.m, self.d = y, m, d
		return self

	def setTupleTime(self, H, M, S):
		# без вариантов приходит время в виде цифр
		# задается без проверки
		self.H, self.M, self.S = H, M, S
		return self

	def setDate(self, y, m = 1, d = 1):
		self._isDate(y, m, d, isGenerateError=True)
		self.y, self.m, self.d = y, m, d
		return self

	def setTime(self, H = 0, M = 0, S = 0):
		self._isTime(H, M, S, isGenerateError=True)
		self.H, self.M, self.S = H, M, S
		return self

	def setDateTime(self, y = 1992, m = 11, d = 30, H = 0, M = 5, S = 0):
		self._isDate(y, m, d, isGenerateError=True)
		self._isTime(H, M, S, isGenerateError=True)
		self.y, self.m, self.d = y, m, d
		self.H, self.M, self.S = H, M, S
		return self

	def setDT(self, dt):
		self.y = dt.year
		self.m = dt.month
		self.d = dt.day
		self.H = dt.hour
		self.M = dt.minute
		self.S = dt.second
		return self

	def setD(self, d):
		self.y, self.m, self.d = d.year, d.month, d.day
		return self

	def setString(self, string, *args):
		# Принимает строку и аргументы с помощью которых из строки будет извлечена дата/время
		# setString(string, "year", "month", "day", "hour", "minute", "second")
		# setString(string, "ymdHMS") #устанавливает относительную позицию
		pass

	def setNow(self):
		dt = datetime.now()
		self.y = dt.year
		self.m = dt.month
		self.d = dt.day
		self.H = dt.hour
		self.M = dt.minute
		self.S = dt.second
		self.MS = dt.microsecond
		return self

	def setUnixEpoch(self, UnixEpoch):
		pass

	def setISO(self, string):
		pass

	def setReGex(self, string, regex):
		pass

	def setChrono(self, ch):
		self.y = ch.y
		self.m = ch.m
		self.d = ch.d
		self.H = ch.H
		self.M = ch.M
		self.S = ch.S
		self.tz = ch.tz
		return self

	def setQDate(self, qd):
		if 'QDate' not in sys.modules:
			from PyQt5.QtCore import QDateTime
		self.y = qd.year()
		self.m = qd.month()
		self.d = qd.day()
		return self

	def setQTime(self, qt):
		if 'QTime' not in sys.modules:
			from PyQt5.QtCore import QTime
		self.H = qt.hour()
		self.M = qt.minute()
		self.S = qt.second()
		return self

	def setQDateTime(self, qdt):
		if 'QDateTime' not in sys.modules:
			from PyQt5.QtCore import QDateTime
		self.setQDate(qdt.date())
		self.setQTime(qdt.time())		
		return self

	def setTZ(self, tz):
		# задает TimeZone без изменения состояния времения 
		return self.setTimeZone(tz)

	def setTimeZone(self, tz):
		# задает TimeZone без изменения состояния времения
		# в отличии от .toTimeZone()
		if tz.lower() == "local":
			self.tz = self.getLocalTimeZone()
		elif tz.lower() == "utc":
			self.tz = "UTC"
		elif tz in self.getAllTimeZone():
			self.tz = tz
		else:
			raise "Временная зона неизвесна!"
		return self

	def setDateTimeISO(self, iso_str): 
		#2020-05-14T08:20:30 — всегда UTC
		self.deconstruction_date(iso_str)
		self.tz = 'UTC'
		return self

