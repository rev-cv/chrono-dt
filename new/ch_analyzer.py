try:
	from PyQt5.QtCore import QDate, QTime, QDateTime
except:
	QDate, QTime, QDateTime = None

class chrono_analyzer(object):
	"""Анализирует поступающие и хранящиеся данные."""
	def __init__(self):
		super(chrono_analyzer, self).__init__()
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

	def isDate(self, y, m, d):
		# является ли переданные значения датой?
		# правильно ли кол-во месяцев и кол-во дней в месяце?
		pass

	def isTime(self, H, M, S):
		# является переданные значения временем?
		pass

	def isDateTime(self, y, m, d, H, M, S):
		if isDate(y, m, d) and isTime(H, M, S):
			return True
		return False

	def isLeapYear(self):
		pass

	def isPart(self, pchrono):
		# является частью периода?
		pass

	def isDayBegun(self):
		# начался ли день? до тех пор пока время не больше 00:00:00 день не начался
		pass

	def isUTC(self):
		pass

	def isLocal(self):
		pass

	def isTimeZone(self, TimeZone):
		pass



Возможные варианты
chrono(2021, 1, 1, 2, 35, 45, 1425, tz = "UTC", isUTC=True, shift="", auto=True)

chrono(False) - создает незаполненный объект chrono. Самый быстрый способ создать chrono
chrono( chrono() )

chrono(QDateTime)
chrono(QDate, QTime)

chrono(datetime.datetime)
chrono(datetime.date, datetime.time)

chrono("2021-02-15")
chrono("2021-02-15", "15:45")
chrono("2021-02-15", "3:45PM")
chrono("2021, 15 November", r"%Y, %d %mE")


chrono()
ns = time.time_ns()
ms = (ns * 1e-6) - round(ns * 1e-9) / 1000
s = 0


