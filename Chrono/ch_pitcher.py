import pytz
from tzlocal import get_localzone
import datetime

class chrono_pitcher(object):
	"""выводит информацию из chrono"""
	def __init__(self):
		super(chrono_pitcher, self).__init__()

	def getAllTimeZone(self):
		return pytz.all_timezones

	def getLocalTimeZone(self):
		return get_localzone()

	def getOffsetByUTC(self):
		# смещение относительно UTC в часах
		if self.tz != "UTC":
			local = self.chrono(False).setDT(datetime.datetime.now())
			utc = self.chrono(False).setChrono(local).toUTC()
			delta = (local.getDateTime() - utc.getDateTime()).seconds / (60 * 60)
		return 0.0
	
	def getDateTime(self):
		return datetime.datetime(self.y, self.m, self.d, self.H, self.M, self.S)

	def getDate(self):
		return datetime.date(self.y, self.m, self.d)

	def getTupleDateTime(self):
		return (self.y, self.m, self.d, self.H, self.M, self.S, self.tz)

	def getTupleDate(self):
		return (self.y, self.m, self.d)

	def getTupleTime(self):
		return (self.H, self.M, self.S)

	def getDayYear(self):
		# получение количество деней с начала года текущей даты
		days = 1 if self.isLeapYear(self.y) and self.m > 2 else 0
		days += self.d
		for i in range(1, self.m):
			days += self._countDays[i]
		return days

	def getISO(self): 
		#всегда возвращает время в UTC
		if self.isUTC():
			return self.template(r"yyyy-MM-ddThh:mm:ss")
		else:
			return self.chrono(False).setChrono(self).toUTC().template(r"yyyy-MM-ddThh:mm:ss")

	def getUnixEpoch(self):
		# получение даты преобразованной в секунды прошедших с 1970
		# написана кастомная функция, чтобы UnixEpoch могла быть отрицательной
		# т.е. чтобы могла отображать время в секундах до 1970
		ch = self if self.tz == "UTC" else self.chrono(False).setChrono(self).toUTC()

		count_days = 0

		if ch.y >= 1970:
			count_days += ch.getDayYear() - 1
			# прибавляется часть прошедшего года
			for year in range(1970, ch.y):
				count_days += 366 if ch.isLeapYear(year) else 365

		elif ch.y < 1970:
			for year in range(1970, ch.y, -1):
				count_days -= 366 if ch.isLeapYear(year) else 365

		return (count_days * 86400) + (ch.H * 3600) + (ch.M * 60) + ch.S

	def getDecade(self):
		# получение декады месяца в которую входит текущая дата
		if self.d < 11: 
			return 1
		elif self.d < 21:
			return 2
		else: return 3

	def getDecadeByYear(self):
		# получение декады с начала года для текущей даты
		d = {3:0,2:1,1:2}
		return self.m * 3 - d[self.getDecade()]

	def getWeekday(self):
		# получить день недели для текущей даты
		day = self.d
		month = self.m
		year = self.y

		if self.isDate() is True:
			if month < 3:
				year -= 1
				month += 10
			else:
				month -= 2
			return (day + 31 * month // 12 + year + year // 4 - year // 100 + year // 400) % 7
		raise "<chrono.getWeekday()>: дата в chrono не создана!"

	def getWeekYear(self): 
		# получение недели с начала года, начиная с первого понедельника
		days_number = self.getDayYear()
		days_number -= self.getWeekday()
		week_number = 0
		while days_number > 0:
			days_number -= 7
			week_number += 1
		return week_number

'''
getLocalZone() #текущая временная зона ПК
getAllTimeZones()
getISO()
getUnixEpoch()
getDateTime()
getQDate()
getQDateTime()
getQTime()
getDayYear()
getDaysYear()
getCentury()
getCenturyRome()
getWeekYear()
getDecade()
getDecadeYear()
getTuple()
format()
getDaysMonth()
toString("yyyy-mm-dd HH:MM:SS.ZZZ")

getDays(years, month)
'''