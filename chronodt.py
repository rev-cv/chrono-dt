#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
pip install pytz, tzlocal, 
https://arrow.readthedocs.io/en/stable/
'''

from tzlocal import get_localzone
from datetime import datetime, timedelta
import pytz, sys #указывает зону времени
from re import findall, sub
from copy import deepcopy

monthsRus = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
monthsRu = ['', 'Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

monthsEng = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
monthsEn = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

format_weekdays = {
	1: ['Понедельник', 'Пн', 'Пнд', 'Monday', 'Mo', 'Mon'],
	2: ['Вторник', 'Вт', 'Втр', 'Tuesday', 'Tu', 'Tue'],
	3: ['Среда', 'Ср', 'Сре', 'Wednesday', 'We', 'Wed'],
	4: ['Четверг', 'Чт', 'Чтв', 'Thursday', 'Th', 'Thu'],
	5: ['Пятница', 'Пт', 'Птн', 'Friday', 'Fr', 'Fri'],
	6: ['Суббота', 'Сб', 'Суб', 'Saturday', 'Sa', 'Sat'],
	0: ['Воскресенье', 'Вс', 'Вск', 'Sunday', 'Su', 'Sun'],
}


class chrono(object):
	def __init__(self, arg_1=None, arg_2=None, arg_3=None, hour=None, minute=None, second=None, 
		year = None, month = None, day = None, shift=None, TimeZone = 'local'):
		super(chrono, self).__init__()
		self.unspecified_values = {
			'year': False,
			'month': False,
			'day': False,
			'hour': False,
			'minute': False,
			'second': False,
		} #непереданные значения даты

		self.year = 0
		self.month = 1
		self.day = 1
		self.hour = 0
		self.minute = 0
		self.second = 0
		if TimeZone == 'local':
			self.timezone = self.getLocalZone()
		else:
			if str(TimeZone) in pytz.all_timezones:
				self.timezone = TimeZone
			else:
				self.timezone = 'UTC'

		self.input_analysis(arg_1 = arg_1,arg_2 = arg_2,arg_3 = arg_3,
			year = year, month = month, day = day,
			hour = hour,minute = minute,second = second)

	def input_analysis(self, arg_1=None, arg_2=None, arg_3=None, 
		year = None, month = None, day = None,
		hour=None, minute=None, second=None):

		type_str = str(type(arg_1))

		if arg_1 is None: #если ничего не передано, то устанавливается текущее время
			if (year is not None or month is not None or day is not None or 
				hour is not None or minute is not None or second is not None):
				#имеются какие то указания на дату
				self.setDate(year, month, day)
				self.setTime(hour, minute, second)
			else: self.setNow()

		elif type(arg_1) is int and arg_2 is None and arg_3 is None: #ЯВЛЯЕТСЯ UNIX EPOCH
			self.setUnixEpoch(arg_1)

		elif type(arg_1) is int and type(arg_2) is int:
			#если дата передана в качестве чисел-аргументов
			self.setDate(arg_1, arg_2, arg_3)
			self.setTime(hour, minute, second)

		elif '.chrono' in type_str:
			self.setDateTimeChrono(arg_1)

		elif 'datetime.datetime' in type_str:
			self.setDateTime(arg_1)

		elif 'PyQt5.QtCore.QDateTime' in type_str:
			self.setQDateTime(arg_1)

		elif 'PyQt5.QtCore.QDate' in type_str:
			self.setQDate(arg_1)
			if 'PyQt5.QtCore.QTime' in str(type(arg_2)):
				self.setQTime(arg_2)

		elif type(arg_1) is str: #если дата передана в качестве строки
			def isISOTime(arg):
				if len(arg) == 19:
					if arg[-9] == 'T':
						return True
					else: return False
				else: return False

			if isISOTime(arg_1): 
				self.setDateTimeISO(arg_1)
			elif arg_1 == 'after': 
				pass #добавить дату после
			elif len(arg_1.split(' ')) == 6:
				self.setDateTimeStandartChrono(arg_1)
			else: self.setDateTimeStr(arg_1)

		return self

	def setNow(self):
		#находит текущую дату в соответствии с указанным self.timezone
		now = datetime.utcnow()
		self.year = now.year
		self.month = now.month
		self.day = now.day
		self.hour = now.hour
		self.minute = now.minute
		self.second = now.second
		if self.timezone != "UTC":
			tm = str(self.timezone)
			self.timezone = "UTC"
			self.toTimeZone(tzone = tm)
		self.incomplete_date_management(*[True] * 6)
		return self

	def setUnixEpoch(self, unixepoch):
		self.year = 1970
		self.month = 1
		self.day = 1
		self.hour = 0
		self.minute = 0
		self.second = 0
		self.timezone = 'UTC'
		self.shift(second = unixepoch)
		return self

	def setDate(self, year = None, month = None, day = None):
		tyear, tmonth, tday = type(year), type(month), type(day)
		if tyear is int and tmonth is int and tday is int:
			if self.check_date(year, month, day):
				self.year, self.month, self.day  = year, month, day
				self.incomplete_date_management(True, True, True)
		else:
			if tyear is int:
				if self.check_date(year, self.month, self.day):
					self.year  = year
					self.incomplete_date_management(True)
			if tmonth is int:	
				if self.check_date(self.year, month, self.day):
					self.month  = month
					self.incomplete_date_management(month = True)
			if tday is int:	
				if self.check_date(self.year, self.month, day):
					self.day = day
					self.incomplete_date_management(day = True)
		return self

	def setTime(self, hour = None, minute = None, second = None):
		thour, tmin, tsec =  type(hour), type(minute), type(second)
		if thour is int and tmin is int and tsec is int:
			if self.chack_time(hour, minute, second):
				self.hour, self.minute, self.second = hour, minute, second
				self.incomplete_date_management(hour = True, minute = True, second = True)
		elif thour is str and minute is None and second is None:
			hms = self.time_from_string(hour)
			self.hour = hms["hour"]
			self.minute = hms["min"]
			self.second = hms["second"]
		else:
			if thour is int:
				if self.chack_time(hour, self.minute, self.second):
					self.hour = hour
					self.incomplete_date_management(hour = True)
			if tmin is int:
				if self.chack_time(self.hour, minute, self.second):
					self.minute = minute
					self.incomplete_date_management(minute = True)
			if tsec is int:
				if self.chack_time(self.hour, self.minute, second):
					self.second = second
					self.incomplete_date_management(second = True)
		return self

	def setDateTimeChrono(self, cdt): #chrono date
		self.year = cdt.year
		self.month = cdt.month
		self.day = cdt.day
		self.hour = cdt.hour
		self.minute = cdt.minute
		self.second = cdt.second
		self.unspecified_values = cdt.unspecified_values
		return self

	def setDateTime(self, dt): #datetime
		self.year = dt.year
		self.month = dt.month
		self.day = dt.day
		self.hour = dt.hour
		self.minute = dt.minute
		self.second = dt.second
		self.incomplete_date_management(*[True] * 6)
		return self

	def setDateTimeISO(self, iso_str): 
		#2020-05-14T08:20:30 ВСЕГДА UTC
		self.datetime_from_string(iso_str)
		self.timezone = 'UTC'
		self.incomplete_date_management(*[True] * 6)
		return self

	def setDateTimeStandartChrono(self, string_chrono): 
		#Tue Jun 23 18:42:36 2020 Asia/Yekaterinburg
		list_date = string_chrono.split(' ')
		self.year = int(list_date[4])
		self.day = int(list_date[2])

		for i in range(1,13):
			if monthsEn[i] == list_date[1]:
				self.month = i
				break

		hms = self.time_from_string(list_date[3])
		if hms is not False:
			self.hour = hms['hour']
			self.minute = hms['min']
			self.second = hms['second']

		self.timezone = list_date[5]

		self.incomplete_date_management(*[True] * 6)

		return self

	def setDateTimeStr(self, str_date): 
		#20200514082030, 2020 05 14 08 20 30
		if str_date in ('now', 'yesterday', 'tomorrow'):
			if str_date == 'now' or str_date == "today":
				self.setNow()
			elif str_date == 'yesterday':
				self.setNow()
				self.shift(day = -1)
			elif str_date == 'tomorrow':
				self.setNow()
				self.shift(day = 1)
		else:
			self.datetime_from_string(str_date)

		return self

	def setQDate(self, qd):
		if 'QDate' not in sys.modules:
			from PyQt5.QtCore import QDate

		self.year = qd.year()
		self.month = qd.month()
		self.day = qd.day()
		self.incomplete_date_management(True, True, True)

		return self

	def setQDateTime(self, qdt):
		if 'QDateTime' not in sys.modules:
			from PyQt5.QtCore import QDateTime
		self.setQDate(qdt.date())
		self.setQTime(qdt.time())
		return self

	def setQTime(self, qt):
		if 'QTime' not in sys.modules:
			from PyQt5.QtCore import QTime

		self.hour = qt.hour()
		self.minute = qt.minute()
		self.second = qt.second()

		self.incomplete_date_management(False, False, False, True, True, True)
		return self

	def shift(self, year = 0, month = 0, day = 0, hour = 0, minute = 0, second = 0, week = 0):
		#Если указан год, месяц, то находится следующая дата +следующего года или месяца
		delta_seconds = second + (minute * 60) + (hour * 3600) +  (day * 86400) + (week * 604800)
		dd = self.getDateTime()
		td = timedelta(seconds = delta_seconds)
		self.setDateTime(dd + td)

		if month != 0:
			self.month += month
			if self.month < 1:
				while self.month < 1:
					self.month += 12
					self.year -= 1
			elif self.month > 12:
				while self.month > 12:
					self.month -= 12
					self.year += 1

		if year != 0:
			self.year += year

		d = 1 if self.check_leap_year(self.year) else 0
		count_days = {1:31,2:28+d,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

		if self.day > count_days[self.month]: 
			self.day = count_days[self.month]

		return self

	def shiftTC(self, shift):
		#+1y -1y 23mo -23mo 3d -3d +1h 25m 1w
		dict_for_shift = {'year':0, 'month':0, 'day':0, 'hour':0, 'minute':0, 'second':0, 'week':0}
		shift = ' {} '.format(shift.lower())
		y  = findall(r'([- +]\d+)y', shift)
		mo = findall(r'([- +]\d+)mo', shift)
		d  = findall(r'([- +]\d+)d', shift)
		h  = findall(r'([- +]\d+)h', shift)
		m  = findall(r'([- +]\d+)m ', shift)
		s  = findall(r'([- +]\d+)s', shift)
		w  = findall(r'([- +]\d+)w', shift)
		m.extend(findall(r'([- +]\d+)[ ]', shift))

		if len(y) != 0: dict_for_shift['year'] = sum([int(x) for x in y])
		if len(mo)!= 0: dict_for_shift['month'] = sum([int(x) for x in mo])
		if len(d) != 0: dict_for_shift['day'] = sum([int(x) for x in d])
		if len(h) != 0: dict_for_shift['hour'] = sum([int(x) for x in h])
		if len(m) != 0: dict_for_shift['minute'] = sum([int(x) for x in m])
		if len(s) != 0: dict_for_shift['second'] = sum([int(x) for x in s])
		if len(w) != 0: dict_for_shift['week'] = sum([int(x) for x in w])

		return self.shift(**dict_for_shift)

	def shiftTextCommand(self, shift):
		return self.shiftTC(shift = shift)

	def getLocalZone(self): 
		#текущая временная зона ПК
		return get_localzone()

	def getActiveTimeZone(self): 
		#выбранная временная зона в объекте chrono
		return self.timezone

	def getAllTimeZones(self):
		return pytz.all_timezones

	def getISO(self): #всегда возвращает время в UTC
		if self.isUTC():
			return self.format('%Y-%m0-%d0T%H0:%M0:%S0')
		else:
			return chrono(self, TimeZone = self.timezone).toUTC().format('%Y-%m0-%d0T%H0:%M0:%S0')
			
	def getUnixEpoch(self):
		chrono_date = self if self.timezone == "UTC" else chrono(self, TimeZone = self.timezone).toUTC()

		count_days = chrono_date.getDayYear() - 1
		if chrono_date.year >= 1970:
			for year in range(1970, chrono_date.year):
				if chrono_date.check_leap_year(year): 
					count_days += 366
				else: count_days += 365
		elif chrono_date.year < 1970:
			for year in range(1970, chrono_date.year, -1):
				if chrono_date.check_leap_year(year): 
					count_days += 366
				else: count_days += 365

		second = (count_days * 86400) + (chrono_date.hour * 3600) + (chrono_date.minute * 60) + chrono_date.second
		if chrono_date.year < 1970: second *= (-1)
		return second

	def getDateTime(self):
		return datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)

	def getQDate(self):
		if 'QDate' not in sys.modules:
			from PyQt5.QtCore import QDate

		return QDate(self.year, self.month, self.day)

	def getQDateTime(self):
		if 'QDateTime' not in sys.modules:
			from PyQt5.QtCore import QDateTime

		return QDateTime(self.getQDate(), self.getQTime())

	def getQTime(self):
		if 'QTime' not in sys.modules:
			from PyQt5.QtCore import QTime

		return QTime(self.hour, self.minute, self.second)

	def getWeekday(self):
		day = deepcopy(self.day)
		month = deepcopy(self.month)
		year = deepcopy(self.year)

		if type(month) is int and type(day) is int and type(year) is int:
			if month < 3:
				year -= 1
				month += 10
			else:
				month -= 2
			return (day + 31 * month // 12 + year + year // 4 - year // 100 + year // 400) % 7
		else: return 'error in chrono'

	def getDayYear(self): #НАХОЖДЕНИЕ ДНЯ С НАЧАЛА ГОДА
		days = 1 if self.check_leap_year(self.year) and self.month > 2 else 0
		count_days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
		days+=self.day
		for i in range(1, self.month):
			days+=count_days[i]
		return days

	def getCentury(self): #ВОЗВРАЩАЕТ ВЕК АРАБСКИМИ ЦИФРАМИ
		if self.year > 0:  return (self.year // 100)+1
		else:  return self.year // 100

	def getCenturyRome(self): #ВОЗВРАЩАЕТ ВЕК ЗАПИСАННЫЙ РИМСКИМИ ЦИФРАМИ XXI.CE
		if self.year > 0: 
			century = (self.year // 100)+1
			tc = self.converter_arabic_numerals_to_roman_numerals(century)
			text_century = '{}.CE'.format(tc)
			return text_century
		else: 
			century = self.year // 100
			tc = self.converter_arabic_numerals_to_roman_numerals(century*(-1))
			text_century = '{}.BC'.format(tc)
			return text_century

	def getWeekYear(self): 
		#ОПРЕДЕЛЕНИЯ НЕДЕЛИ ГОДА С ПЕРВОГО ПОНЕДЕЛЬНИКА ГОДА
		days_number = self.getDayYear()
		days_number -= self.getWeekday()
		week_number = 0
		while days_number > 0:
			days_number -= 7
			week_number += 1
		return week_number

	def toLocal(self): 
		#переводит время объекта chrono в локальное
		self.toTimeZone(self.getLocalZone())
		return self

	def toUTC(self): 
		#переводит время объекта chrono в UTC
		self.toTimeZone('UTC')
		return self

	def toTimeZone(self, tzone = 'UTC'): 
		#переводит время объекта chrono в указанную временную зону
		tzone = str(tzone)
		tz = pytz.timezone(str(self.timezone))
		now_datetime = tz.localize(self.getDateTime())
		to_tz = pytz.timezone(tzone)
		new_datetime = now_datetime.astimezone(to_tz)
		self.setDateTime(new_datetime)
		self.timezone = tzone
		return self

	def isUTC(self): 
		#возвращает True, если время содержится в UTC
		if self.timezone == 'UTC':
			return True
		else: 
			return False

	def check_date(self, year, month, day, hour = 0, minute = 0, second = 0):
		for x in year, month, day, hour, minute, second:
			if type(x) is not int: return False
		if month > 12 or month < 1: return False
		if self.check_count_days_in_month(year, month, day) is not True: return False
		return True

	def chack_time(self, hour, minute, second):
		if hour >= 0 and hour < 24 and minute >= 0 and minute < 60 and second >= 0 and second < 60: 
			return True
		else: return False

	def check_count_days_in_month(self, year, month, day):
		#ЯВЛЯЕТСЯ ЛИ УКАЗАННОЕ КОЛ-ВО ДНЕЙ В ЭТОМ МЕСЯЦЕ ВЕРНЫМ (С УЧЕТОМ ВИСОКОСТНОСТИ)?
		if month in [1, 3, 5, 7, 8, 10, 12] and day <=31: return True
		elif month in [4, 6, 9, 11] and day < 31: return True
		elif month == 2 and self.check_leap_year(year) is False and day < 29: return True
		elif month == 2 and self.check_leap_year(year) is True and day <= 29: return True
		else: return False

	def check_leap_year(self, year):
		#ЯВЛЯЕТСЯ ЛИ ГОД ВИСОКОСНЫМ?
		if year % 4 == 0:
			if year % 100 != 0: return True
			else:
				if year % 400 == 0: return True
				else: return False
		else: return False

	def incomplete_date_management(self, year = None, month = None, day = None, 
		hour = None, minute = None, second = None):
		#управление неполной датой
		#добавляет в словарь self.unspecified_values значения, которые дата не содержит
		#убирает из словарь self.unspecified_values значения, которые дата содержит
		names = ['year', 'month', 'day', 'hour', 'minute', 'second']
		values = [year, month, day, hour, minute, second]
		for name, value in zip(names, values):
			if value != None and (value is True or value is False):
				self.unspecified_values[name] = value

	def isLocal(self): 
		#возвращает True, если время локальное
		if self.timezone == self.getLocalZone():
			return True
		else: 
			return False

	def isDate(self):
		return self.check_date(self.year, self.month, self.day)

	def isTime(self):
		return self.chack_time(self.hour, self.minute, self.second)

	def isDateTime(self):
		if self.isDate() and self.isTime(): return True
		else: return False

	def format(self, temp = r"%a %b %d %H0:%M0:%S0 %Y %Z"):
		regex = r'%HMS0' 
		if regex in temp:
			text_str = self.format(r'%H0:%M0:%S0')
			temp = sub(regex, text_str, temp)

		regex = r'%HMS'
		if regex in temp:
			text_str = self.format(r'%H:%M:%S')
			temp = sub(regex, text_str, temp)

		regex = r'%YMD0'
		if regex in temp:
			text_str = self.format(r'%Y-%m0-%d0')
			temp = sub(regex, text_str, temp)

		regex = r'%YMD_'
		if regex in temp:
			text_str = self.format(r'%Y_%m0.%d0.')
			temp = sub(regex, text_str, temp)

		regex = r'%YMD'
		if regex in temp:
			text_str = self.format(r'%Y-%m-%d')
			temp = sub(regex, text_str, temp)

		regex = r'%x'
		if regex in temp:
			text_str = self.format(r'%Y-%m0-%d0')
			temp = sub(regex, text_str, temp)

		regex = r'%X'
		if regex in temp:
			text_str = self.format(r'%H0:%M0:%S0')
			temp = sub(regex, text_str, temp)

		regex = r'%DEC'	#декада месяца
		if regex in temp:
			dec = 'III'
			if self.day < 11: dec = "I"
			elif self.day < 21: dec = "II"
			temp = sub(regex, f'{dec} decade of %mE', temp)

		regex = r'%QUA'	#квартал года
		if regex in temp:
			qua = 'IV'
			if self.month < 4: qua = 'I'
			elif self.month < 7: qua = "II"
			elif self.month < 10: qua = "III"
			temp = sub(regex, f'{qua} quarter %Y', temp)

		regex = r'%Y'	#полный год
		if regex in temp:
			temp = sub(regex, f'{self.year}', temp)

		regex = r'%y'#год без века
		if regex in temp:
			str_year = str(self.year)
			if len(str_year) == 4 or len(str_year) == 3:
				temp = sub(regex, f'{str_year[-2:]}', temp)
			elif len(str_year) == 2 or len(str_year) == 1:
				temp = sub(regex, f'{str_year}', temp)

		regex = r'%m0'	#номер месяца с нулем, если месяц январь-сентябрь
		if regex in temp:
			temp = sub(regex, '{:0>2}'.format(self.month), temp)

		regex = r'%mE'	#полное название месяца на английском языке
		if regex in temp:
			temp = sub(regex, '{}'.format(monthsEng[self.month]), temp)

		regex = r'%mR'	#полное название месяца на русском языке языке
		if regex in temp:
			temp = sub(regex, '{}'.format(monthsRus[self.month]), temp)

		regex = r'%mAE'	#сокращенное название месяца на английском языке
		if regex in temp:
			temp = sub(regex, '{}'.format(monthsEn[self.month]), temp)

		regex = r'%mAR'	#сокращенное название месяца на русском языке
		if regex in temp:
			temp = sub(regex, '{}'.format(monthsRu[self.month]), temp)

		regex = r'%m'	#номер месяца без нуля, если месяц январь-сентябрь
		if regex in temp:
			if self.month == 0: self.month = ''
			temp = sub(regex, '{}'.format(self.month), temp)

		regex = r'%B'	#полное название месяца на английском языке
		if regex in temp:
			temp = sub(regex, '{}'.format(monthsEng[self.month]), temp)

		regex = r'%b'	#сокращенное название месяца на английском языке
		if regex in temp:
			temp = sub(regex, '{}'.format(monthsEn[self.month]), temp)

		regex = r'%d0'	#день месяца с нулем (05) в датах между 01-09
		if regex in temp:
			temp = sub(regex, '{:0>2}'.format(self.day), temp)

		regex = r'%d'	#день месяца без нуля (05) в датах между 1-9
		if regex in temp:
			temp = sub(regex, '{}'.format(self.day), temp)

		regex = r'%H0'	#час с нулем
		if regex in temp:
			temp = sub(regex, '{:0>2}'.format(self.hour), temp)

		regex = r'%H'	#час
		if regex in temp:
			temp = sub(regex, '{}'.format(self.hour), temp)

		regex = r'%M0'	#минуты с нулем
		if regex in temp:
			temp = sub(regex, '{:0>2}'.format(self.minute), temp)

		regex = r'%M'	#минуты
		if regex in temp:
			temp = sub(regex, '{}'.format(self.minute), temp)

		regex = r'%AMPM'	#время в 12 часовом вормате
		if regex in temp:
			str_time = '{}:{:0>2}PM'.format(self.hour-12, self.minute) if self.hour > 12 else '{}:{:0>2}AM'.format(self.hour,self.minute)
			temp = sub(regex, str_time, temp)

		regex = r'%S0'	#секунды с нулем
		if regex in temp:
			temp = sub(regex, '{:0>2}'.format(self.second), temp)

		regex = r'%S'	#секунды
		if regex in temp:
			temp = sub(regex, str(self.second), temp)

		regex = r'%Z'	#локальная зона
		if regex in temp:
			temp = sub(regex, '{}'.format(self.getActiveTimeZone()), temp)

		regex = r'%wAE3'	#сокращеная надпись дня недели до трех символов на английском языке
		if regex in temp:
			weekday = self.getWeekday()
			if weekday != 'error in hrono':
				temp = sub(regex, '{}'.format(format_weekdays[weekday][5]), temp)
			else: temp = sub(regex, '', temp)

		regex = r'%wAR3'	#сокращеная надпись дня недели до трех символов на русском языке
		if regex in temp:
			weekday = self.getWeekday()
			if weekday != 'error in hrono':
				temp = sub(regex, '{}'.format(format_weekdays[weekday][2]), temp)
			else: temp = sub(regex, '', temp)

		regex = r'%wAR'	#сокращеная надпись дня недели до 2 символов на русском языке
		if regex in temp:
			weekday = self.getWeekday()
			if weekday != 'error in hrono':
				temp = sub(regex, '{}'.format(format_weekdays[weekday][1]), temp)
			else: temp = sub(regex, '', temp)

		regex = r'%wAE'	#сокращеная надпись дня недели до 2 символов на русском языке
		if regex in temp:
			weekday = self.getWeekday()
			if weekday != 'error in hrono':
				temp = sub(regex, '{}'.format(format_weekdays[weekday][4]), temp)
			else: temp = sub(regex, '', temp)

		regex = r'%wR'	#сокращеная надпись дня недели на русском языке
		if regex in temp:
			weekday = self.getWeekday()
			if weekday != 'error in hrono':
				temp = sub(regex, '{}'.format(format_weekdays[weekday][0]), temp)
			else: temp = sub(regex, '', temp)

		regex = r'%wE'	#сокращеная надпись дня недели на английском языке
		if regex in temp:
			weekday = self.getWeekday()
			if weekday != 'error in hrono':
				temp = sub(regex, '{}'.format(format_weekdays[weekday][3]), temp)
			else: temp = sub(regex, '', temp)

		regex = r'%w'	#день недели
		if regex in temp:
			weekday = self.getWeekday()
			if weekday != 'error in hrono':
				temp = sub(regex, '{}'.format(weekday), temp)
			else: temp = sub(regex, '', temp)

		regex = r'%cRome'	#век римскими цифрами
		if regex in temp:
			weekday = self.getCenturyRome()
			if weekday != 'error in hrono':
				temp = sub(regex, '{}'.format(weekday), temp)
			else: temp = sub(regex, '', temp)

		regex = r'%c'	#век арабскими цифрами
		if regex in temp:
			weekday = self.getCentury()
			if weekday != 'error in hrono':
				temp = sub(regex, '{}'.format(weekday), temp)
			else: temp = sub(regex, '', temp)

		regex = r'%a'	#сокращеная надпись дня недели до трех символов на английском языке
		if regex in temp:
			weekday = self.getWeekday()
			if weekday != 'error in hrono':
				temp = sub(regex, '{}'.format(format_weekdays[weekday][5]), temp)
			else: temp = sub(regex, '', temp)

		regex = r'%A'	#надпись дня недели на английском языке
		if regex in temp:
			weekday = self.getWeekday()
			if weekday != 'error in hrono':
				temp = sub(regex, '{}'.format(format_weekdays[weekday][3]), temp)
			else: temp = sub(regex, '', temp)

		regex = r'%W'	#кол-во недель с начала года (считается с первого понедельника)
		if regex in temp:
			temp = sub(regex, str(self.getWeekYear()), temp)

		regex = r'%j'	#кол-во дней с начала года
		if regex in temp:
			temp = sub(regex, str(self.getDayYear()), temp)

		regex = r'%I'	#часы в 12часовом формате
		if regex in temp:
			str_time = hour-12 if hour > 12 else hour
			temp = sub(regex, str(str_time), temp)

		return temp

	def datetime_from_string(self, findings):
		#могут прийти следующие строки в формате
		#2019 11 11 20 00 00
		#или
		#20191111200000
		#могут отстутствовать сек > минуты > часы > день > месяц
		d = findall(r'\d+', findings)
		ymdhms = False
		ymdhms_True = list()

		CE = 1
		try:
			if findings[0] == '-':
				findings = findings.replace('-', ' ').strip()
				CE = -1
		except IndexError: pass
		
		if type(d) == list and len(d) != 0:
			d = [int(x) for x in d]
			ld, ld0 = len(d), len(str(d[0]))
			if ld == 1 and ld0 <= 4: #скорее всего год
				ymdhms = {'y':int(d[0]),'mo':1,'d':1,'h':0,'m':0,'s':0}
				ymdhms_True = ['y']
			elif ld == 1 and (ld0 == 5 or ld0 == 6):
				#скорее всего год с месяцем, либо год, месяц, дата
				month, year = int(str(d[0])[4:]), int(str(d[0])[:4])
				if month <= 12 and month > 0: 
					ymdhms = {'y':year,'mo':month,'d':1,'h':0,'m':0,'s':0}
					ymdhms_True = ['y', 'mo']
				elif month == 0 and ld0 == 5:
					#видимо хотел ввести месяц в виде 01 (типа 202001), но успел ввести только 0
					ymdhms = {'y':year,'mo':1,'d':1,'h':0,'m':0,'s':0}
					ymdhms_True = ['y', 'mo']
				else:
					month, day = int(str(month)[:1]), int(str(month)[1:])
					if month != 0 and day != 0:
						ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
						ymdhms_True = ['y', 'mo', 'd']
			elif ld == 1 and ld0 == 7:
				year, md = int(str(d[0])[:4]), int(str(d[0])[4:])
				if int(str(md)[:-1]) <= 12:
					month, day = int(str(md)[:-1]), int(str(md)[-1:])
					if day > 0: 
						ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
						ymdhms_True = ['y', 'mo', 'd']
					else: 
						ymdhms = {'y':year,'mo':month,'d':1,'h':0,'m':0,'s':0}
						ymdhms_True = ['y', 'mo']
				elif self.check_date(year, int(str(md)[:1]), int(str(md)[-2:])) is True:
					month, day = int(str(md)[:1]), int(str(md)[-2:])
					ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
					ymdhms_True = ['y', 'mo', 'd']
				elif self.check_count_days_in_month(year,int(str(md)[:1]),int(str(md)[-2:])) is True:
					month, day, hour = int(str(md)[0]), int(str(md)[1]), int(str(md)[2])
					ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':0,'s':0}
					ymdhms_True = ['y', 'mo', 'd', 'h']
			elif ld == 1 and ld0 == 8:
				year, md = int(str(d[0])[:4]), str(d[0])[4:]
				month, day = int(md[:2]), int(md[2:])
				if self.check_date(year, month, day) is True:
					#1992 12 31
					ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
					ymdhms_True = ['y', 'mo', 'd']
				elif month > 12:
					#1992 9 31 9 
					#1992 9 9 23
					#1992 9 9 9 9
					month = int(md[:1])
					day = int(md[1]+md[2])
					if self.check_count_days_in_month(year, month, day) is True:
						ymdhms = {'y':year,'mo':month,'d':day,'h':int(md[3]),'m':0,'s':0}
						ymdhms_True = ['y', 'mo', 'd', 'h']
					else:
						day = int(md[1])
						hour = int(md[2]+md[3])
						if hour <= 23:
							ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':0,'s':0}
							ymdhms_True = ['y', 'mo', 'd', 'h']
						else:
							hour, minute = int(md[2]), int(md[3])
							ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':minute,'s':0}
							ymdhms_True = ['y', 'mo', 'd', 'h', 'm']
				elif month <= 12:
					#1992 12 9 9
					day, hour = int(md[-2]), int(md[-1])
					ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':0,'s':0}
					ymdhms_True = ['y', 'mo', 'd', 'h']
			elif ld == 1 and ld0 >= 9:
				'''
				Если месяц двойной с двойной датой
				1999 12 31 9
				Если месяц двойной с одинарной датой 
				1999 12 9 отправить в _time_from_string

				Если месяц одинарный и двойная дата
				1999 9 31 отправить в _time_from_string
				'''
				year, md = int(str(d[0])[:4]), str(d[0])[4:]
				month, day = int(md[:2]), int(md[2]+md[3])

				def function(year, month, day, balance):
					r = self.time_from_string(balance)
					if r is not False:
						return {'y':year,'mo':month,'d':day,
							'h':r['hour'],'m':r['min'],'s':r['second']}
					else: return False

				if month <= 12:
					if self.check_count_days_in_month(year, month, day) is True:
						ymdhms = function(year, month, day, md[4:])
					else:
						day = int(md[2])
						ymdhms = function(year, month, day, md[3:])
				elif month > 12:
					month = int(md[0])
					day = int(md[1]+md[2])
					if self.check_count_days_in_month(year, month, day) is True:
						ymdhms = function(year, month, day, md[3:])
					else:
						day = int(md[1])
						ymdhms = function(year, month, day, md[2:])
			elif ld >= 2 and ld <= 6 and d[1] > 0 and d[1] <= 12:
				ymdhms = {'y':int(d[0]),'mo':int(d[1]),'d':1,'h':0,'m':0,'s':0}
				if ld >= 3:
					if self.check_count_days_in_month(int(d[0]),int(d[1]),int(d[2])) is True:
						ymdhms['d'] = int(d[2])
				if ld >= 4:
					if d[3] <= 23 and d[3] >= 0: 
						ymdhms['h'] = int(d[3])
				if ld >= 5:
					if d[4] <= 59 and d[4] >= 0:
						ymdhms['m'] = int(d[4])
				if ld == 6:
					if d[5] <= 59 and d[5] >= 0:
						ymdhms['s'] = int(d[5])
		
		if ymdhms is not False: 
			ymdhms['y'] = ymdhms['y'] * CE
			if ymdhms['d'] == 0: ymdhms['d'] = 1

		self.year = ymdhms['y']
		self.month = ymdhms['mo']
		self.day = ymdhms['d']
		self.hour = ymdhms['h']
		self.minute = ymdhms['m']
		self.second = ymdhms['s']
	
	def time_from_string(self, findings):
		#ПЫТАЕТСЯ НАЙТИ В СТРОКЕ ЗНАЧЕНИЯ ВРЕМЕНИ
		t = findall(r'(\d+)', findings)
		hms = {'hour':None,'min':None,'second':0}
		if len(t) == 1:
			if int(t[0]) <= 23 and (len(t[0]) == 1 or len(t[0]) == 2):
				hms['hour'], hms['min'] = int(t[0]), 0
			elif len(t[0]) == 2:
				hms['hour'], hms['min'] = int(t[0][0]), int(t[0][1])*10
			elif len(t[0]) == 3:
				tz = [t[0][0], t[0][1], t[0][2]]
				if int(tz[0]) <= 9 and int(tz[1] + tz[2]) < 60:
					hms['hour'], hms['min'] = int(tz[0]), int(tz[1] + tz[2])
				elif (int(tz[0] + tz[1]) > 9) and (int(tz[0] + tz[1]) < 24) and (int(tz[2]) <= 5):
					hms['hour'], hms['min'] = int(tz[0] + tz[1]), int(tz[2])*10
				else:
					hms['hour'], hms['min'] = int(t[0][0]), int(t[0][1])*10
					hms['second'] = int(t[0][2])*10
			elif len(t[0]) == 4:
				tz = [int(t[0][:-2]), int(t[0][-2:])]
				if tz[0] <= 23 and tz[1] < 59:
					hms['hour'], hms['min'] = tz[0], tz[1]
			elif len(t[0]) == 5:
				#1 59 59 | 23 1 59 | 23 59 1
				hour, minute = int(t[0][:2]), int(t[0][2]+t[0][3])
				if hour < 24 and minute < 60:
					#значит одинарные секунды
					hms['hour'], hms['min'] = hour, minute
					hms['second'] = int(t[0][4])*10
				elif hour < 24:
					#значит одинарные минуты
					hms['hour'], second = hour, int(t[0][-2:])
					if second > 60: hms['second'] = 59
					else: hms['second'] = second
					minute = int(t[0][2])
					if minute*10 > 60: hms['min'] = minute
					else: hms['min'] = minute*10
				elif minute < 60:
					#значит одинарные часы
					hms['hour'] = int(t[0][0])
					minute = int(t[0][1]+t[0][2])
					if minute < 60: hms['min'] = minute
					second = int(t[0][-2:])
					if second > 60: hms['second'] = 59
					else: hms['second'] = second
			elif len(t[0]) == 6:
				hour, minute, second = int(t[0][:2]), int(t[0][2]+t[0][3]), int(t[0][-2:])
				if hour < 24 and minute < 60 and second < 60:
					hms['hour'], hms['min'], hms['second'] = hour, minute, second
		elif len(t) == 2:
			if int(t[0]) < 24 and int(t[1]) < 60:
				hms['hour'], hms['min'] = int(t[0]), int(t[1])
		elif len(t) == 3:
			if int(t[0]) < 24 and int(t[1]) < 60 and int(t[2]) < 60:
				hms['hour'], hms['min'], hms['second'] = int(t[0]), int(t[1]), int(t[2])
		if hms['hour'] is not None and hms['min'] is not None: return hms
		else: return False

	def converter_arabic_numerals_to_roman_numerals(self, arabic):
		roman = {
			0:['I','II','III','IV','V','VI','VII','VIII','IX'], #единицы
			1:['X','XX','XXX','XL','L','LX','LX','LXX','LXXX','XC'], #десятки
			2:['C','CC','CCC','CD','IƆ','IƆC','IƆCC','IƆCCC','CCIƆ'], #сотни
			3:['CIƆ','CIƆCIƆ','CIƆCIƆCIƆ','CIƆIƆƆ','IƆƆ','IƆƆCIƆ','IƆƆCIƆCIƆ',
			'IƆƆCIƆCIƆCIƆ','CIƆCCIƆƆ'],
			4:['CCIƆƆ','CCIƆƆCCIƆƆ','CCIƆƆCCIƆƆCCIƆƆ','CCIƆƆIƆƆƆ','IƆƆƆ','IƆƆƆCCIƆƆ',
			'IƆƆƆCCIƆƆCCIƆƆ','IƆƆƆCCIƆƆCCIƆƆCCIƆƆ','CCIƆƆCCCIƆƆƆ'],
			5:['CCCIƆƆƆ','CCCIƆƆƆCCCIƆƆƆ','CCCIƆƆƆCCCIƆƆƆCCCIƆƆƆ','CCCIƆƆƆIƆƆƆƆ','IƆƆƆƆ',
				'IƆƆƆƆCCCIƆƆƆ','IƆƆƆƆCCCIƆƆƆCCCIƆƆƆ']}
		if arabic > 0 and arabic < 800000:
			list_int_arabic = [int(x) for x in list(str(arabic))]
			list_int_arabic.reverse()
			list_int_roman = list()
			for x in zip(range(len(list_int_arabic)), list_int_arabic):
				list_int_roman.append(roman[x[0]][x[1]-1])
			list_int_roman.reverse()
			return ''.join(list_int_roman)

	def generatePeriod(self, obj_chrono = None, result = 'ymdHMS'):
		#находит большую дату между датой в текущем объекте chrono и переданным
		#переводит в секунды оба объекта
		#получившуюся разницу распределяет согласно шаблону. Если в шаблоне указано только S, то 
		#результат разницы будет передан только в секундах. Если в шаблоне присутствует yS, то
		#результат будет передан в кол-ве лет и остатка в виде секунд
		#результат будет возвращен в виде словаря
		return pchrono(obj_chrono, self, False)

	def __lt__(self, other):
		#x < y
		if self.getUnixEpoch() < other.getUnixEpoch():
			return True
		else: return False 

	def __le__(self, other):
		#x <= y
		if self.getUnixEpoch() <= other.getUnixEpoch():
			return True
		else: return False

	def __eq__(self, other):
		#x == y
		if self.getUnixEpoch() == other.getUnixEpoch():
			return True
		else: return False

	def __ne__(self, other):
		#x != y
		if self.getUnixEpoch() != other.getUnixEpoch():
			return True
		else: return False

	def __gt__(self, other):
		#x > y
		if self.getUnixEpoch() > other.getUnixEpoch():
			return True
		else: return False

	def __ge__(self, other):
		#x >= y
		if self.getUnixEpoch() >= other.getUnixEpoch():
			return True
		else: return False

	def __str__(self):
		return self.format('Object.Chrono(DATE %Y-%m0-%d0; TIME %H0:%M0:%S0; TZ %Z;)')

	def __sub__(self, other):
		#chrono_1 - chrono_2 вернет период двух объектов хроно через self.getDifferent(other)
		#print(other.format())
		return self.generatePeriod(other)


class pchrono(object):
	def __init__(self, start = None, finish = None, priority_day = True):
		#priority_day = True - ориентироваться на период длиной в днях
		#priority_day = False - ориентируется на данные о неполной дате и времени
		
		#если start == вчера, то start это сегодня вычесть сутки

		super(pchrono, self).__init__()
		if start is None and finish is None:
			self.start = chrono().setTime(0, 0, 0)
			self.finish = chrono(self.start).shift(day = 1)

		elif start is not None and finish is None and priority_day is True:
			#указанную дату принимает как период равный суткам
			self.start = chrono(start).setTime(0, 0, 0)
			self.finish = chrono(self.start).shift(day = 1)

		elif start is not None and finish is None and priority_day is False:
			#ищет период на основании введенных в chrono данных. 
			#Если в chrono был введен только год, то период будет равен start: 2020-01-01 00:00:00; finish: 2021-01-01 00:00:00; TZ:
			self.start = chrono(start)
			if self.start.unspecified_values['year']:
				if self.start.unspecified_values['month']:
					if self.start.unspecified_values['day']:
						if self.start.unspecified_values['hour']:
							if self.start.unspecified_values['minute']:
								if self.start.unspecified_values['second']:
									#выбирает priority_day == True
									self.start = chrono(start).setTime(0, 0, 0)
									self.finish = chrono(self.start).shift(day = 1)
								else:
									self.start = chrono(start)
									self.finish = chrono(start).shift(minute = 1)
							else:
								self.start = chrono(start)
								self.finish = chrono(start).shift(hour = 1)
						else:
							self.start = chrono(start)
							self.finish = chrono(start).shift(day = 1)
					else:
						self.start = chrono(start)
						self.finish = chrono(start).shift(month = 1)
				else:
					self.start = chrono(start)
					self.finish = chrono(start).shift(year = 1)
			
		elif start is not None and finish is not None and priority_day is True:
			self.start = chrono(start).setTime(0, 0, 0)
			self.finish = chrono(finish).setTime(0, 0, 0).shift(day = 1)

		elif start is not None and finish is not None and priority_day is False:
			self.start = chrono(start)
			self.finish = chrono(finish)

	def __str__(self):
		temp = '%Y-%m0-%d0 %H0:%M0:%S0;'
		return 'Object.PChrono(START {} FINISH {})'.format(self.start.format(temp), self.finish.format(temp))

	def formatDiff(self, temp = ''):
		pass

	def getSecondsDiff(self):
		return self.finish.getUnixEpoch() - self.start.getUnixEpoch()

	def check_dates(self, date):
		if date.isdatetime():
			start = date
			finish = date
		if date.isdate(): 
			#нужно найти период конкретного дня
			start = hrono(date.year, date.month, date.day, 0, 0, 0)
			finish = hrono(date.year, date.month, date.day, 23, 59, 59)
		elif date.year is not None and date.month is not None:
			#нужно найти период конкретного месяца
			ly0 = 1 if date.check_leap_year(date.year) is True else 0
			cd = {1:31,2:28+ly0,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
			start = hrono(date.year, date.month, 1, 0, 0, 0)
			finish = hrono(date.year, date.month, cd[date.month], 23, 59, 59)
		elif date.year is not None:
			start = hrono(date.year, 1, 1, 0, 0, 0)
			finish = hrono(date.year, 12, 31, 23, 59, 59)
		return start, finish

	def getScale(self):
		balance = {'y':0,'d':0,'h':0,'m':0,'s':0}
		seconds = self.getSecondsDiff()
		by = seconds // (86400 * 365)
		bd = (seconds - (by * 86400 * 365)) // 86400
		bh = (seconds - (bd * 86400)) // 3600
		bm = (seconds - (bd * 86400 + bh * 3600)) // 60
		bs = (seconds - (bd * 86400 + bh * 3600)) % 60
		balance['y'] = by
		balance['d'] = bd
		balance['h'] = bh
		balance['m'] = bm
		balance['s'] = bs
		return balance

	def getPercentDay(self):
		return round(self.getSecondsDiff() * 100 / 86400, 1)

	def getPercentWeek(self):
		return round(self.getSecondsDiff() * 100 / (86400 * 7), 1)

	def getPercentYear(self):
		return round(self.getSecondsDiff() * 100 / (86400 * 365), 1)

	def getPercentDecade(self):
		return round(self.getSecondsDiff() * 100 / (86400 * 365 * 10 + 2), 1)

	def getPercentCentury(self):
		return round(self.getSecondsDiff() * 100 / (86400 * 365 * 100 + 25), 1)

	def getHM(self):
		second = self.getSecondsDiff()
		h = second // 3600
		m = (second - (h*3600)) // 60
		return h, m



if __name__ == '__main__':
	import time

	c = chrono(1955, 8, 14)
	c.setTime("05:0")
	print(c.format())

