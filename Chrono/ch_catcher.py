import sys
from datetime import datetime
import time

class chrono_catcher(object):
    """задает дату в chrono"""
    def __init__(self):
        super(chrono_catcher, self).__init__()

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
            # чтобы миновать тяжеловесный метод .set()
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
                self.setUnixEpoch(y)

        elif type_y is str:
            command = y.lower() 

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
        dt = datetime.now()
        self.y = dt.year
        self.m = dt.month
        self.d = dt.day
        self.H = dt.hour
        self.M = dt.minute
        self.S = dt.second
        self.tz = self.getLocalTimeZone()
        # self.MS = dt.microsecond
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
        return self

    def setByReGex(self, string, regex):
        # вставка по regex выражению
        pass

    def setByTemplate(self, string, template):
        # вставка по шаблону типа yyyy-MM-dd hh:mm:ss tz
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
            raise Exception("<chrono.setTimeZone()>:  time zone unknown!")
        return self

    def setDateTimeISO(self, iso_str): 
        #2020-05-14T08:20:30 — всегда UTC
        self.deconstruction_date(iso_str)
        self.tz = 'UTC'
        return self

