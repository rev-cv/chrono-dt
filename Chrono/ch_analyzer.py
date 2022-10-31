

class ChronoAnalyzer(object):
    """Анализирует поступающие и хранящиеся данные."""
    def __init__(self):
        super(ChronoAnalyzer, self).__init__()

        self._countDays = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
        

    def _isDate(self, y, m, d, isGenerateError=False):
        # является ли переданные значения датой?
        # проверка кол-ва месяцев и кол-ва дней в месяце
        if 12 < m < 1:
            if isGenerateError is False: 
                return False
            else:
                raise Exception("<chrono._isDate()>: the month is indicated by numbers from 1 to 12")

        return self._isCountDaysInMonth(y, m, d, isGenerateError=True)

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
        if year % 4 == 0:
            if year % 100 != 0: 
                return True
            else:
                if year % 400 == 0: 
                    return True
                else: 
                    return False
        else: return False

    def isPart(self, pchrono):
        # является частью периода?
        pass

    def isDayBegun(self):
        # начался ли день? до тех пор пока время не больше 00:00:00 день не начался
        # эта проверка необходима для периодов чтобы период типа
        # 2022-03-12 00:00:00 — 2022-03-13 00:00:00 принедлежал только для дня 
        # 2022-03-12, но не для дня 2022-03-13
        pass

    def isUTC(self):
        return True if self.tz == "UTC" else False

    def isLocal(self):
        return True if self.tz != "UTC" and self.tz is not None else False

    def isTimeZone(self, TimeZone):
        # проверка временной зоны на возможность использования
        return True if TimeZone in self.getAllTimeZone() else False



# Возможные варианты
# chrono(2021, 1, 1, 2, 35, 45, 1425, tz = "UTC", isUTC=True, shift="", auto=True)

# chrono(False) - создает незаполненный объект chrono. Самый быстрый способ создать chrono
# chrono( chrono() )

# chrono(QDateTime)
# chrono(QDate, QTime)

# chrono(datetime.datetime)
# chrono(datetime.date, datetime.time)

# chrono("2021-02-15")
# chrono("2021-02-15", "15:45")
# chrono("2021-02-15", "3:45PM")
# chrono("2021, 15 November", r"%Y, %d %mE")


# chrono()
# ns = time.time_ns()
# ms = (ns * 1e-6) - round(ns * 1e-9) / 1000
# s = 0


