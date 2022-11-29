import datetime
import sys
import time
from re import compile, findall, match, sub

import pytz
from tzlocal import get_localzone


class Chrono(object):

    def __init__(self, 
            y = None, m = None, d = None, 
            H = None, M = None, S = None, 
            shift = None, tz = "local"):

        super(Chrono, self).__init__()
        self.attach_data()

        self.y = None
        self.m = None
        self.d = None
        self.H = None
        self.M = None
        self.S = None
        self.tz = None

        self.setTimeZone(tz)

        if y is not False:
            self.set(y, m, d, H, M, S)  # type: ignore

        if shift is not None:
            if type(shift) is str:
                # принимает строку с текстовыми командами для смещения
                self.shiftTextCommand(shift)
            elif type(shift) is dict:
                # принимает словарь с текстовыми командами для смещения
                self.shift(**shift)

    def __str__(self):
        s = 'CHRONO('
        s += 'DATE yyyy-MM-dd ' if self.isDate() else 'DATE None '
        s += 'TIME hh:mm:ss ' if self.isTime() else 'TIME None '
        s += 'TZ tz)'
        return self.template(s)

    def attach_data(self):
        self._countDays = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
        # ↑ зафиксированое количество дней в месяцах

        self.t_weekdays = {
            1: ['Понедельник', 'Пн', 'Пнд', 'Monday', 'Mo', 'Mon'],
            2: ['Вторник', 'Вт', 'Втр', 'Tuesday', 'Tu', 'Tue'],
            3: ['Среда', 'Ср', 'Сре', 'Wednesday', 'We', 'Wed'],
            4: ['Четверг', 'Чт', 'Чтв', 'Thursday', 'Th', 'Thu'],
            5: ['Пятница', 'Пт', 'Птн', 'Friday', 'Fr', 'Fri'],
            6: ['Суббота', 'Сб', 'Суб', 'Saturday', 'Sa', 'Sat'],
            7: ['Воскресенье', 'Вс', 'Вск', 'Sunday', 'Su', 'Sun'],
        }

        self.t_month_rus = ['', 
            'Январь', 'Февраль', 'Март', 
            'Апрель', 'Май', 'Июнь', 
            'Июль', 'Август', 'Сентябрь', 
            'Октябрь', 'Ноябрь', 'Декабрь'
        ]

        self.t_month_rus_abb = ['', 
            'Янв', 'Фев', 'Мар', 
            'Апр', 'Май', 'Июн', 
            'Июл', 'Авг', 'Сен', 
            'Окт', 'Ноя', 'Дек'
        ]

        self.t_month_eng = ['', 
            'January', 'February', 'March', 
            'April', 'May', 'June', 
            'July', 'August', 'September', 
            'October', 'November', 'December'
        ]

        self.t_month_eng_abb = ['', 
            'Jan', 'Feb', 'Mar', 
            'Apr', 'May', 'Jun', 
            'Jul', 'Aug', 'Sep', 
            'Oct', 'Nov', 'Dec'
        ]

        self.monthNames = {
            'jan': 1, 'january':  1, 'янв': 1, 'январь': 1, 'января': 1,
            'feb': 2, 'february': 2, 'фев': 2, 'февраль': 2, 'февраля': 2,
            'mar': 3, 'march': 3, 'мар': 3, 'март': 3, 'марта': 3,
            'apr': 4, 'april': 4, 'апр': 3, 'апрель': 4, 'апреля': 4,
            'may': 5, 'may': 5, 'май': 5, 'мая': 5,
            'jun': 6, 'june': 6, 'июн': 6, 'июнь': 6, 'июня': 6,
            'jul': 7, 'july': 7, 'июл': 7, 'июль': 7, 'июля': 7,
            'aug': 8, 'august': 8, 'авг': 8, 'август': 8, 'августа': 8,
            'sep': 9, 'september': 9, 'сен': 9, 'сентябрь': 9, 'сентября': 9,
            'oct': 10, 'october': 10, 'окт': 10, 'октябрь': 10, 'октября': 10,
            'nov': 11, 'november': 11, 'нов': 11, 'ноябрь': 11, 'ноября': 11,
            'dec': 12, 'december': 12, 'дек': 12, 'декабрь': 12, 'декабря': 12,
        }


    # ·······················································
    # CHRONO ANALYZER
    # → Анализирует поступающие и хранящиеся данные
    # ·······················································


    def _isDate(self, y, m, d, isGenerateError=False):
        # является ли переданные значения датой?
        # проверка кол-ва месяцев и кол-ва дней в месяце
        if 12 < m < 1:
            if isGenerateError is False: 
                return False
            else:
                raise Exception("<chrono._isDate()>: the month is indicated by numbers from 1 to 12")

        return self._isCountDaysInMonth(y, m, d, isGenerateError)

    def _isTime(self, H, M, S, isGenerateError=False):
        # является переданные значения временем?
        if 0 <= H < 24:
            if 0 <= M < 60:
                if 0 <= S < 60:
                    return True
                elif isGenerateError is True:
                    raise Exception("<chrono._isTime()>: the seconds are incorrect.")
            elif isGenerateError is True:
                raise Exception("<chrono._isTime()>: the minutes are incorrect.")
        elif isGenerateError is True:
            raise Exception("<chrono._isTime()>: the hours are incorrect.")

        return False

    def _isDateTime(self, y, m, d, H, M, S, isGenerateError=False):
        isdate = self._isDate(y, m, d, isGenerateError)
        istime = self._isTime(H, M, S, isGenerateError)
        if isdate and istime:
            return True
        return False

    def isDate(self):
        # содержит ли объект Chrono дату?
        if self.y is None or self.m is None or self.d is None:
            return False
        return True

    def isTime(self):
        # содержит ли объект Chrono время?
        if self.H is None or self.M is None or self.S is None:
            return False
        return True

    def isDateTime(self):
        # содержит ли объект Chrono дату и время?
        if self.isDate() is True and self.isTime() is True:
            return True
        return False 

    def _isCountDaysInMonth(self, y, m, d, isGenerateError=False):
        # верно ли количество дней (d) для указанного месяца (m)
        # с учетом високосного и не високосного года

        if d <= 0:
            if isGenerateError is False: 
                return False
            else:
                raise Exception("<chrono._isCountDaysInMonth()>: day cannot be number 0")

        if m in [1, 3, 5, 7, 8, 10, 12] and d <=31: 
            return True
        elif m in [4, 6, 9, 11] and d < 31: 
            return True
        elif m == 2 and d < 29: 
            return True
        elif m == 2 and self.isLeapYear(y) is True and d <= 29: 
            return True
        else:
            if isGenerateError is False: 
                return False
            else:
                raise Exception("<chrono._isCountDaysInMonth()>: the specified day does not exist in the specified month.")

    def isLeapYear(self, year = None):
        # является ли год високосным?
        year = self.y if year is None and self.y is not None else year
        if year is not None:
            if year % 4 == 0:
                if year % 100 != 0: 
                    return True
                else:
                    if year % 400 == 0: 
                        return True
                    else: 
                        return False
        return False

    def isPart(self, pchrono):
        # является частью периода?
        pass

    def isDayBegun(self):
        # начался ли день?
        # пока время равно 00:00:00 день считается не начавшимся
        # эта проверка необходима для периодов чтобы период типа
        # 2022-03-12 00:00:00 — 2022-03-13 00:00:00 принедлежал только для дня 
        # 2022-03-12, но не для дня 2022-03-13
        if self.H == 0 and self.M == 0 and self.S == 0:
            return False
        return True

    def isUTC(self):
        return True if self.tz == "UTC" else False

    def isLocal(self):
        return True if self.tz != "UTC" and self.tz is not None else False

    def isTimeZone(self, TimeZone):
        # проверка временной зоны на возможность использования
        return True if TimeZone in self.getAllTimeZone() else False

    
    # ·······················································
    # CHRONO CATCHER
    # → Задает данные в chrono
    # ·······················································


    def set(self, 
            y = 2000, 
            m = 1, 
            d = 1, 
            H = 0, 
            M = 0, 
            S = 0, 
        ):
        type_y = type(y)

        if y is None:
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
                self.setUnixEpoch(y)

        elif type_y is str:
            command = y.lower()   # type: ignore

            if command == "now":
                self.setNow()
            elif command == "utc":
                return round(time.time())
            elif command == "s":
                return time.time()
            elif command == "ns":
                return time.time_ns()
            else:
                # разбирает строку в которой предположительно имеется
                # последовательность y, m, d, H, M, S
                # при этом эта последовательность может быть разделена
                # любыми символами в любом количестве
                # или разделение может не быть вовсе
                # Например, обработаются обе строки
                # 2022-12-12 04:12:55
                # 20221212041255
                self.setDateTimeFromString(y)

        elif isinstance(y, datetime.datetime):
            self.setDT(y)

        elif isinstance(y, Chrono):
            # является ли объект chrono
            self.setChrono(y)

        elif type_y is tuple or type_y is list:
            #Предположительно содержит (year, month, day, hour, minute, second)
            self.setDateTime(*y)  # type: ignore

        elif 'PyQt5.QtCore.QDateTime' in str(type_y):
            # так сделано, чтобы не импортировать PyQt до того пока действительно не будет нужен
            self.setQDateTime(y)

        elif 'PyQt5.QtCore.QDate' in str(type_y):
            # так сделано, чтобы не импортировать PyQt до того пока действительно не будет нужен
            self.setQDate(y)
            if 'PyQt5.QtCore.QTime' in str(type(m)):
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

    def setDate(self, y = 1992, m = 1, d = 1):
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

    def setDateFromString(self, string, *args):
        d, t = self.deconstruction_date(string)
        self.setTupleDate(*d)
        return self

    def setTimeFromString(self, string, *args):
        t = self.deconstruction_time(string)
        if t is not False:
            self.setTupleTime(t['hour'], t['min'], t['second'])
        return self

    def setDateTimeFromString(self, string, *args):
        # Принимает строку и аргументы с помощью которых из строки будет извлечена дата/время
        # setString(string, "year", "month", "day", "hour", "minute", "second")
        # setString(string, "ymdHMS") #устанавливает относительную позицию
        d, t = self.deconstruction_date(string)
        self.setTupleDate(*d)
        self.setTupleTime(*t)
        return self

    def setNow(self):
        dt = datetime.datetime.now()
        self.y = dt.year
        self.m = dt.month
        self.d = dt.day
        self.H = dt.hour
        self.M = dt.minute
        self.S = dt.second
        self.tz = self.getLocalTimeZone()
        return self

    def setUnixEpoch(self, unixepoch):
        self.y = 1970
        self.m = 1
        self.d = 1
        self.H = 0
        self.M = 0
        self.S = 0
        self.tz = 'UTC'
        self.shift(second = unixepoch)
        return self

    def setISO(self, iso):
        d, t = self.deconstruction_date(iso)
        self.setTupleDate(*d)
        self.setTupleTime(*t)
        self.tz = 'UTC'
        return self

    def setByReGex(self, regex, string):
        # вставка по regex выражению
        result = self.deconstruction_datetime_by_regex(regex, string)
        if type(result) is list:
            self.setTupleDate(*result[0])
            self.setTupleTime(*result[1])
        return self

    def setByTemplate(self, template, string):
        # вставка по шаблону типа yyyy-MM-dd hh:mm:ss
        result = self.deconstruction_datetime_by_template(template, string)
        if type(result) is list:
            self.setTupleDate(*result[0])
            self.setTupleTime(*result[1])
        return self

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
            raise Exception("<chrono.setTimeZone()>:  time zone unknown!")
        return self


    # ·······················································
    # CHRONO PITCHER
    # → Выводит информацию из chrono
    # ·······················································


    def getAllTimeZone(self):
        return list(pytz.all_timezones)

    def getLocalTimeZone(self):
        return str(get_localzone())

    def getOffsetByUTC(self):
        # смещение относительно UTC в часах
        if self.tz != "UTC":
            local = Chrono(False).setDT(datetime.datetime.now())
            utc = Chrono(False).setChrono(local).toUTC()
            delta = (local.getDateTime() - utc.getDateTime()).seconds / (60 * 60)
        return 0.0
    
    def getDateTime(self):
        return datetime.datetime(self.y, self.m, self.d, self.H, self.M, self.S)  # type: ignore

    def getDate(self):
        return datetime.date(self.y, self.m, self.d)  # type: ignore

    def getTupleDateTime(self):
        return (self.y, self.m, self.d, self.H, self.M, self.S, self.tz)

    def getTupleDate(self):
        return (self.y, self.m, self.d)

    def getTupleTime(self):
        return (self.H, self.M, self.S)

    def getDayYear(self):
        # получение количество деней с начала года текущей даты
        days = 1 if self.isLeapYear() and self.m > 2 else 0  # type: ignore
        days += self.d # type: ignore
        for i in range(1, self.m):  # type: ignore
            days += self._countDays[i]
        return days

    def getISO(self): 
        #всегда возвращает время в UTC
        if self.isUTC():
            return self.template(r"yyyy-MM-ddThh:mm:ss")
        else:
            return Chrono(False).setChrono(self).toUTC().template(r"yyyy-MM-ddThh:mm:ss")

    def getUnixEpoch(self):
        # получение даты преобразованной в секунды прошедших с 1970
        # написана кастомная функция, чтобы UnixEpoch могла быть отрицательной
        # т.е. чтобы могла отображать время в секундах до 1970
        ch = self if self.tz == "UTC" else Chrono(False).setChrono(self).toUTC()

        count_days = 0

        if ch.y >= 1970:  # type: ignore
            count_days += ch.getDayYear() - 1
            # прибавляется часть прошедшего года
            for year in range(1970, ch.y):  # type: ignore
                count_days += 366 if ch.isLeapYear(year) else 365

        elif ch.y < 1970:  # type: ignore
            for year in range(1970, ch.y, -1): # type: ignore
                count_days -= 366 if ch.isLeapYear(year) else 365

        return (count_days * 86400) + (ch.H * 3600) + (ch.M * 60) + ch.S # type: ignore

    def getDecade(self):
        # получение декады месяца в которую входит текущая дата
        if self.d < 11: # type: ignore 
            return 1
        elif self.d < 21:  # type: ignore
            return 2
        else: return 3

    def getDecadeByYear(self):
        # получение декады с начала года для текущей даты
        d = {3:0,2:1,1:2}
        return self.m * 3 - d[self.getDecade()]  # type: ignore

    def getWeekday(self):
        # получить день недели для текущей даты
        if self.isDate() is True:
            month = self.m + 10 if self.m < 3 else self.m - 2  # type: ignore
            year = self.y - 1 if self.m < 3 else self.y # type: ignore
            result = (self.d + 31 * month // 12 + year + year // 4 - year // 100 + year // 400) % 7  # type: ignore
            return 7 if result == 0 else result
        raise Exception("<chrono.getWeekday()>:  date not created!")

    def getWeekYear(self): 
        # получение недели с начала года, начиная с первого понедельника
        days_number = self.getDayYear()
        days_number -= self.getWeekday()
        week_number = 0 if Chrono(self.y, 1, 1, 0, 0, 0).getWeekday() != 1 else 1
        while days_number > 0:
            days_number -= 7
            week_number += 1
        return week_number
    
    def getLastDayMonth(self):
        if self.m in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif self.m in [4, 6, 9, 11]:
            return 30
        elif self.m == 2:
            return 29 if self.isLeapYear() else 28

    def getCentury(self):
        # возвращает век арабскими цифрами
        return ( self.y // 100 ) + 1 if self.y > 0 else self.y // 100 * (-1) # type: ignore
    
    def getCenturyRome(self):
        # возвращает век записанный римскими цифрами
        century = self.getCentury()
        if century < 0:
            rc = self.convertToRomanNumerals(century * (-1))
            return f'{rc}.BC'
        else:
            return f'{self.convertToRomanNumerals(century)}.AD'


    # ·······················································
    # CHRONO TRANSFORMATOR
    # → Изменяет внутреннее состояние chrono
    # ·······················································


    def setTS(self, string):
        return self.setTimeShift(string)

    def setTimeShift(self, string):
        # Time + Shift
        # получает строку в которой может быть передано одновременно и время и смещение 
        # пример: 
        # "00:25 +45" → 01:10
        # "025 + 45"  → 01:10
        # a.setTS("2 +3d -25") → задает 02:00 прибавляет 3 дня и вычетает 25 минут

        string = string.strip()
        # ↑ строка должна начинать с чисел времени

        time = findall(r"^\d{1,2}:\d{1,2}|^\d{1,4}", string)
        if len(time) > 0:
            self.setTimeFromString(time[0])
            string = sub(r"(^\d{1,2}:\d{1,2}|^\d{1,4})", r"", string)
        self.shiftTextCommand(string)
        return self

    def shiftTC(self, string):
        return self.shiftTextCommand(string)

    def shiftTextCommand(self, string):
        # Text Command
        # задание смещения текстовыми командами
        # пример:
        # +1y -1y 23mo -23mo 3d -3d +1h 25m 1w
        # +2*2w = +4w, +55*5m = +275m
        shift_args = {'year':0, 'month':0, 'day':0, 'hour':0, 'minute':0, 'second':0, 'week':0}
        
        def multiplication(string):
            multipliers = string[0].split("*")
            return str( int(multipliers[0]) * int(multipliers[1]) )
        string = sub(r'[0-9]+\*[0-9]+', multiplication, string)
        # ↑ выполняет переумножение чисел разделенных `*` в текстовой команде 
        shift = f' {string.lower()} '

        y  = findall(r'([- +]\d+)y', shift)
        mo = findall(r'([- +]\d+)mo', shift)
        d  = findall(r'([- +]\d+)d', shift)
        h  = findall(r'([- +]\d+)h', shift)
        m  = findall(r'([- +]\d+)m ', shift)
        s  = findall(r'([- +]\d+)s', shift)
        w  = findall(r'([- +]\d+)w', shift)
        # ↓ если передано число безх текстового индикатора, то оно считается как минуты
        m.extend(findall(r'([- +]\d+)[ ]', shift))

        if len(y) != 0: shift_args['year'] = sum([int(x) for x in y])
        if len(mo)!= 0: shift_args['month'] = sum([int(x) for x in mo])
        if len(d) != 0: shift_args['day'] = sum([int(x) for x in d])
        if len(h) != 0: shift_args['hour'] = sum([int(x) for x in h])
        if len(m) != 0: shift_args['minute'] = sum([int(x) for x in m])
        if len(s) != 0: shift_args['second'] = sum([int(x) for x in s])
        if len(w) != 0: shift_args['week'] = sum([int(x) for x in w])

        return self.shift(**shift_args)

    def shift(self, year = 0, month = 0, day = 0, hour = 0, minute = 0, second = 0, week = 0):
        
        delta_seconds = second + (minute * 60) + (hour * 3600) +  (day * 86400) + (week * 86400 * 7)
        self.setDT(
            self.getDateTime() + datetime.timedelta(seconds = delta_seconds) 
        )

        # Если указан год или месяц, то 
        # находится следующая дата + следующего года или месяца

        if month != 0:
            self.m += month  # type: ignore
            if self.m < 1:
                while self.m < 1:
                    self.m += 12
                    self.y -= 1 # type: ignore
            elif self.m > 12:
                while self.m > 12:
                    self.m -= 12
                    self.y += 1  # type: ignore

        self.y += year # type: ignore

        count_days = {
            1:31,
            2:29 if self.isLeapYear(self.y) else 28,
            3:31,
            4:30,
            5:31,
            6:30,
            7:31,
            8:31,
            9:30,
            10:31,
            11:30,
            12:31
        }

        if self.d > count_days[self.m]:  # type: ignore
            self.d = count_days[self.m]  # type: ignore

        return self

    def toTimeZone(self, TimeZone = 'UTC'):
        # переводит время из текущей временной зоны в переданную
        if TimeZone != self.tz:
            preset_tz = pytz.timezone( str(self.tz) )
            preset_dt = preset_tz.localize(
                self.getDateTime()
            )

            new_tz = pytz.timezone(str(TimeZone))
            new_datetime = preset_dt.astimezone(new_tz)

            self.y = new_datetime.year
            self.m = new_datetime.month
            self.d = new_datetime.day
            self.H = new_datetime.hour
            self.M = new_datetime.minute
            self.S = new_datetime.second
            self.tz = str(TimeZone)

        return self

    def toUTC(self):
        return self.toTimeZone('UTC')

    def toLocal(self):
        return self.toTimeZone(
            self.getLocalTimeZone()
        )


    # ·······················································
    # STRING CONSTRUCTION
    # → Изменяет внутреннее состояние chrono
    # ·······················································


    def F(self, temp = r"%a %b %d %H0:%M0:%S0 %Y %Z"):
        return self.format(temp)

    def T(self, temp = r"yyyy-MM-dd hh:mm:ss"):
        return self.template(temp)

    def template(self, temp = r"yyyy-MM-dd hh:mm:ss"):
        '''
        Метод предназначен только для шаблонов!

        yyyy - полный год
        yy   - год без века
        
        MM   - месяц с нулем
        MMMM - месяц текстом на английском (полный)
        MMM  - месяц текстом на английском (сокращенно)

        dd   - день с нулем
        ddd  - день недели текстом (сокращенно)
        dddd - день недели текстом (полный)

        hh - часы с нулем

        mm - минуты с нулем

        ss - секунды с нулем

        tz - временная зона
        ap - AM/PM
        '''

        regex = r'yyyy' # полный год
        if regex in temp:
            temp = sub(regex, f'{self.y}', temp)

        regex = r'yy'#год без века
        if regex in temp:
            temp = sub(regex, str(self.y)[-2:], temp)

        regex = r'MMMM'	#полное название месяца на английском языке
        if regex in temp:
            temp = sub(regex, self.t_month_eng[self.m], temp) # type: ignore

        regex = r'MMM'	#сокращенное название месяца на английском языке
        if regex in temp:
            temp = sub(regex, self.t_month_eng_abb[self.m], temp) # type: ignore

        regex = r'MM' # месяц с нулем
        if regex in temp:
            temp = sub(regex, f'{self.m:0>2}', temp)


        regex = r'dddd' # надпись дня недели на английском языке
        if regex in temp:
            temp = sub(regex, f'{self.t_weekdays[self.getWeekday()][3]}', temp)

        regex = r'ddd' # сокращеная надпись дня недели до трех символов на английском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][5], temp)

        regex = r'dd' # день с нулем
        if regex in temp:
            temp = sub(regex, f'{self.d:0>2}', temp)


        regex = r'hh'	#час с нулем
        if regex in temp:
            temp = sub(regex, f'{self.H:0>2}', temp)

        regex = r'mm'	#минуты с нулем
        if regex in temp:
            temp = sub(regex, f'{self.M:0>2}', temp)

        regex = r'ap'	#время в 12 часовом вормате
        if regex in temp:
            ap = "PM" if self.H > 12 else "AM"  # type: ignore
            temp = sub( regex, ap, temp)

        regex = r'ss'	#секунды с нулем
        if regex in temp:
            temp = sub(regex, f'{self.S:0>2}', temp)
        
        regex = r'tz'	#временная зона
        if regex in temp:
            temp = sub(regex, f'{self.tz}', temp)

        return temp

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
            dec = self.getDecade()
            temp = sub(regex, f'{dec}th', temp)

        regex = r'%DY'	#декада месяца, но отчет с начала года
        if regex in temp:
            dec = self.getDecadeByYear()
            temp = sub(regex, f'{dec}th', temp)

        regex = r'%QUA'	#квартал года
        if regex in temp:
            qua = 'Ⅳ'
            if self.m < 4: qua = 'Ⅰ'      # type: ignore
            elif self.m < 7: qua = "Ⅱ"   # type: ignore
            elif self.m < 10: qua = "Ⅲ" # type: ignore
            temp = sub(regex, qua, temp)

        regex = r'%Y'	#полный год
        if regex in temp:
            temp = sub(regex, f'{self.y}', temp)

        regex = r'%y'#год без века
        if regex in temp:
            temp = sub(regex, str(self.y)[-2:], temp)

        regex = r'%m0'	#номер месяца с нулем, если месяц январь-сентябрь
        if regex in temp:
            temp = sub(regex, f'{self.m:0>2}', temp)

        regex = r'%mE'	#полное название месяца на английском языке
        if regex in temp:
            temp = sub(regex, self.t_month_eng[self.m], temp) # type: ignore

        regex = r'%mR'	#полное название месяца на русском языке языке
        if regex in temp:
            temp = sub(regex, self.t_month_rus[self.m], temp) # type: ignore

        regex = r'%mAE'	#сокращенное название месяца на английском языке
        if regex in temp:
            temp = sub(regex, self.t_month_eng_abb[self.m], temp) # type: ignore

        regex = r'%mAR'	#сокращенное название месяца на русском языке
        if regex in temp:
            temp = sub(regex, self.t_month_rus_abb[self.m], temp) # type: ignore

        regex = r'%m'	#номер месяца без нуля, если месяц январь-сентябрь
        if regex in temp:
            temp = sub(regex, str(self.m), temp)

        regex = r'%B'	#полное название месяца на английском языке
        if regex in temp:
            temp = sub(regex, self.t_month_eng[self.m], temp)  # type: ignore

        regex = r'%b'	#сокращенное название месяца на английском языке
        if regex in temp:
            # type: ignore
            temp = sub(regex, self.t_month_eng_abb[self.m], temp) # type: ignore

        regex = r'%d0'	#день месяца с нулем (05) в датах между 01-09
        if regex in temp:
            temp = sub(regex, f'{self.d:0>2}', temp)

        regex = r'%d'	#день месяца без нуля (5) в датах между 1-9
        if regex in temp:
            temp = sub(regex, str(self.d), temp)

        regex = r'%H0'	#час с нулем
        if regex in temp:
            temp = sub(regex, f'{self.H:0>2}', temp)

        regex = r'%H'	#час
        if regex in temp:
            temp = sub(regex, str(self.H), temp)

        regex = r'%M0'	#минуты с нулем
        if regex in temp:
            temp = sub(regex, f'{self.M:0>2}', temp)

        regex = r'%M'	#минуты
        if regex in temp:
            temp = sub(regex, str(self.M), temp)

        regex = r'%AMPM'	#время в 12 часовом вормате
        if regex in temp:
            temp = sub(
                regex, 
                f'{self.H-12}:{self.M}PM' if self.H > 12 else f'{self.H}:{self.M}AM', # type: ignore
                temp
            )

        regex = r'%S0'	#секунды с нулем
        if regex in temp:
            temp = sub(regex, f'{self.S:0>2}', temp)

        regex = r'%S'	#секунды
        if regex in temp:
            temp = sub(regex, str(self.S), temp)

        regex = r'%Z'	#временная зона
        if regex in temp:
            temp = sub(regex, f'{self.tz}', temp)

        regex = r'%wAE3'	#сокращеная надпись дня недели до трех символов на английском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][5], temp)

        regex = r'%wAR3'	#сокращеная надпись дня недели до трех символов на русском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][2], temp)

        regex = r'%wAR'	#сокращеная надпись дня недели до 2 символов на русском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][1], temp)

        regex = r'%wAE'	#сокращеная надпись дня недели до 2 символов на русском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][4], temp)

        regex = r'%wR'	#сокращеная надпись дня недели на русском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][0], temp)

        regex = r'%wE'	#сокращеная надпись дня недели на английском языке
        if regex in temp:
            temp = sub(regex, self.t_weekdays[self.getWeekday()][3], temp)

        regex = r'%w'	#день недели
        if regex in temp:
            temp = sub(regex, f'{self.getWeekday()}', temp)

        regex = r'%cRome'	#век римскими цифрами
        if regex in temp:
            temp = sub(regex, f'{self.getCenturyRome()}', temp)

        regex = r'%c'	#век арабскими цифрами
        if regex in temp:
            temp = sub(regex, f'{self.getCentury()}', temp)

        regex = r'%a'	#сокращеная надпись дня недели до трех символов на английском языке
        if regex in temp:
            temp = sub(regex, f'{self.t_weekdays[self.getWeekday()][5]}', temp)

        regex = r'%A'	#надпись дня недели на английском языке
        if regex in temp:
            temp = sub(regex, f'{self.t_weekdays[self.getWeekday()][3]}', temp)

        regex = r'%W'	#кол-во недель с начала года (считается с первого понедельника)
        if regex in temp:
            temp = sub(regex, str(self.getWeekYear()), temp)

        regex = r'%j'	#кол-во дней с начала года
        if regex in temp:
            temp = sub(regex, str(self.getDayYear()), temp)

        regex = r'%I'	#часы в 12часовом формате
        if regex in temp:
            temp = sub(
                regex, 
                f'{self.H-12}:{self.M}' if self.H > 12 else f'{self.H}:{self.M}', # type: ignore
                temp
            )

        return temp


    def convertToRomanNumerals(self, arabic):
        # https://unicode-table.com/ru/sets/roman-numerals/
        result = ""

        def reduction (symbol_roman, arg):
            nonlocal arabic
            nonlocal result
            if arabic >= arg:
                while arabic >= arg:
                   result += symbol_roman 
                   arabic -= arg
        
        reduction('ↈ', 100000)
        reduction('ↇ', 50000)
        reduction('ↂ', 10000)
        reduction('ↁ', 5000)
        reduction('Ⅿ', 1000)
        reduction('Ⅾ', 500)
        reduction('Ⅽ', 100)
        reduction('Ⅼ', 50)
        reduction('Ⅹ', 10)

        if 0 < arabic < 10:
            r = {1:'Ⅰ',2:'Ⅱ',3:'Ⅲ',4:'Ⅳ',5:'Ⅴ',6:'Ⅵ',7:'Ⅶ',8:'Ⅷ',9:'Ⅸ',10:'Ⅹ'}
            result += r[arabic]

        return result 


    # ·······················································
    # CHRONO DECONSTRUCTION
    # → Преобразовывает строки в данные для chrono
    # ·······················································


    def deconstruction_datetime_by_regex(self, regex, string):
        # в шаблоне должны быть именованные группы
        # примеры смотреть в deconstruction_datetime_by_template
        # year
        # month
        # day
        # hour
        # minute
        # second
        # month_text - любое текстовое обозначение месяца предусмотренное в self.monthNames

        year = None
        month = None
        day = None
        hour = 0
        minute = 0
        second = 0

        r = match(regex, string)
        if r is not None:
            recd = r.groupdict()
            received_keys = recd.keys()

            if "year" in received_keys:
                year = int(recd['year'])
            
            if "month" in received_keys:
                month = int(recd['month'])
            elif "month_text" in received_keys:
                month = self.monthNames.get(recd['month_text'].lower())

            if "day" in received_keys:
                day = int(recd['day'])

            if self._isDate(year, month, day) is False:
                return None

            hour = int(recd.get('hour', 0))
            minute = int(recd.get('minute', 0))
            second = int(recd.get('second', 0))

            if self._isTime(hour, minute, second) is False:
                return None

            return [
                [year, month, day],
                [hour, minute, second]
            ]

        return None

    def deconstruction_datetime_by_template(self, template, string):
        # пределывает переданный шаблон в regex-выражение шаблоны типа "yyyy, dd MMM hh:mm"
        # передает дальнейшее выполнение в deconstruction_datetime_by_regex
        templates = [
            ["yyyy", r"(?P<year>-\d{1,4}|\d{1,4})"],
            ["dd", r"(?P<day>\d{1,2})"],
            ["hh", r"(?P<hour>\d{1,2})"],
            ["mm", r"(?P<minute>\d{1,2})"],
            ["ss", r"(?P<second>\d{1,2})"],
            ["MMMM", r"(?P<month_text>[a-zA-Z]{3,9})"],
            ["MMM", r"(?P<month_text>[a-zA-Z]{3})"],
            ["MM", r"(?P<month>\d{1,2})"],
        ]

        for x in templates:
            if x[0] in template:
                template = template.replace(x[0], x[1])

        return self.deconstruction_datetime_by_regex(template, string)


    def deconstruction_date(self, string):
        # Модуль производит разбор строки в которую предположительно записана дата
        # в последовательности <год месяц день часы минуты секунды>
        # Подобный алгоритм хорош тем, что он не зависит от разделителей
        # и может разбирать такие даты
        # 2019 11 11 20 00 00
        # 20191111200000

        d = findall(r'\d+', string)
        ymdhms = False

        CE = 1
        try:
            if string[0] == '-':
                string = string.replace('-', ' ').strip()
                CE = -1
        except IndexError: pass
        # ↑ определяет BC и AD
        # если в начале строки стоит знак минус
        # до значит дата "до нашей эры"

        
        if type(d) == list and len(d) != 0:
            d = [int(x) for x in d]
            ld, ld0 = len(d), len(str(d[0]))
            if ld == 1 and ld0 <= 4: #скорее всего год
                ymdhms = {'y':int(d[0]),'mo':1,'d':1,'h':0,'m':0,'s':0}
            elif ld == 1 and (ld0 == 5 or ld0 == 6):
                #скорее всего год с месяцем, либо год, месяц, дата
                month, year = int(str(d[0])[4:]), int(str(d[0])[:4])
                if month <= 12 and month > 0: 
                    ymdhms = {'y':year,'mo':month,'d':1,'h':0,'m':0,'s':0}
                elif month == 0 and ld0 == 5:
                    #видимо хотел ввести месяц в виде 01 (типа 202001), но успел ввести только 0
                    ymdhms = {'y':year,'mo':1,'d':1,'h':0,'m':0,'s':0}
                else:
                    month, day = int(str(month)[:1]), int(str(month)[1:])
                    if month != 0 and day != 0:
                        ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
            elif ld == 1 and ld0 == 7:
                year, md = int(str(d[0])[:4]), int(str(d[0])[4:])
                if int(str(md)[:-1]) <= 12:
                    month, day = int(str(md)[:-1]), int(str(md)[-1:])
                    if day > 0: 
                        ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
                    else: 
                        ymdhms = {'y':year,'mo':month,'d':1,'h':0,'m':0,'s':0}
                elif self._isDate(year, int(str(md)[:1]), int(str(md)[-2:])) is True:
                    month, day = int(str(md)[:1]), int(str(md)[-2:])
                    ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
                elif self._isCountDaysInMonth(year,int(str(md)[:1]),int(str(md)[-2:])) is True:
                    month, day, hour = int(str(md)[0]), int(str(md)[1]), int(str(md)[2])
                    ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':0,'s':0}
            elif ld == 1 and ld0 == 8:
                year, md = int(str(d[0])[:4]), str(d[0])[4:]
                month, day = int(md[:2]), int(md[2:])
                if self._isDate(year, month, day) is True:
                    #1992 12 31
                    ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
                elif month > 12:
                    #1992 9 31 9 
                    #1992 9 9 23
                    #1992 9 9 9 9
                    month = int(md[:1])
                    day = int(md[1]+md[2])
                    if self._isCountDaysInMonth(year, month, day) is True:
                        ymdhms = {'y':year,'mo':month,'d':day,'h':int(md[3]),'m':0,'s':0}
                    else:
                        day = int(md[1])
                        hour = int(md[2]+md[3])
                        if hour <= 23:
                            ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':0,'s':0}
                        else:
                            hour, minute = int(md[2]), int(md[3])
                            ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':minute,'s':0}
                elif month <= 12:
                    #1992 12 9 9
                    day, hour = int(md[-2]), int(md[-1])
                    ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':0,'s':0}
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
                    r = self.deconstruction_time(balance)
                    if r is not False:
                        return {'y':year,'mo':month,'d':day,
                            'h':r['hour'],'m':r['min'],'s':r['second']}
                    else: return False

                if month <= 12:
                    if self._isCountDaysInMonth(year, month, day) is True:
                        ymdhms = function(year, month, day, md[4:])
                    else:
                        day = int(md[2])
                        ymdhms = function(year, month, day, md[3:])
                elif month > 12:
                    month = int(md[0])
                    day = int(md[1]+md[2])
                    if self._isCountDaysInMonth(year, month, day) is True:
                        ymdhms = function(year, month, day, md[3:])
                    else:
                        day = int(md[1])
                        ymdhms = function(year, month, day, md[2:])
            elif ld >= 2 and ld <= 6 and d[1] > 0 and d[1] <= 12:
                ymdhms = {'y':int(d[0]),'mo':int(d[1]),'d':1,'h':0,'m':0,'s':0}
                if ld >= 3:
                    if self._isCountDaysInMonth(int(d[0]),int(d[1]),int(d[2])) is True:
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
            if ymdhms['d'] == 0: 
                ymdhms['d'] = 1

            return [
                [
                    ymdhms['y'],
                    ymdhms['mo'],
                    ymdhms['d'],
                ],
                [
                    ymdhms['h'],
                    ymdhms['m'],
                    ymdhms['s']
                ]				
            ]

    def deconstruction_time(self, findings):
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
        if hms['hour'] is not None and hms['min'] is not None: 
            return hms
        else: return False


    # ·······················································
    # CHRONO OPERATORS
    # → Изменяет внутреннее состояние chrono
    # ·······················································


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

if __name__ == '__main__':
    a = Chrono("2018-01-01")

    print(a.getWeekYear())
