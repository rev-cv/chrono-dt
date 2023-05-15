import datetime
import time


from ch_catchers import *
from ch_pitchers import *
from ch_mutators import toTimeZone, shift, shiftTextCommand
from ch_formators import format, template


class Chrono(object):

    def __init__(self, 
            y = None, 
            m = None, 
            d = None, 
            H = None, 
            M = None, 
            S = None, 
            tz = "local",
            shift = None
        ):

        super(Chrono, self).__init__()

        self.y = None
        self.m = None
        self.d = None
        self.H = None
        self.M = None
        self.S = None
        self.tz = None

        if y is not False:

            self.setTimeZone(tz)

            self.set(y, m, d, H, M, S)  # type: ignore

            if shift is not None:
                if type(shift) is str:
                    # принимает строку с текстовыми командами для смещения
                    self.shiftTextCommand(shift)
                elif type(shift) is dict:
                    # принимает словарь с текстовыми командами для смещения
                    self.shift(**shift)
    
    def set(self, y = None, m = None, d = None, H = None, M = None, S = None):
        type_y = type(y)

        if y is None:
            # datetime now
            self.setNow()

        elif type_y is int:
            if type(m) is int and type(d) is int:
                # сигнатура аргументов указывает на то, что дата передана цифрами 2021, 11, 5
                # дата может так же быть передана со временем
                H = H if type(H) is int else 0
                M = M if type(M) is int else 0
                S = S if type(S) is int else 0
                
                self.y, self.m, self.d = setDate(y, m, d)
                self.H, self.M, self.S = setTime(H, M, S)

            else:
                # скорее всего передана дата в UnixEpoch
                self.y, self.m, self.d, self.H, self.M, self.S = setUnixEpoch(y)

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
                self.y, self.m, self.d, self.H, self.M, self.S = setDateTimeFromStr(y)

        elif isinstance(y, datetime.datetime):
            self.setDT(y)

        elif isinstance(y, Chrono):
            # является ли объект chrono
            self.setChrono(y)

        elif type_y is tuple or type_y is list:
            #Предположительно содержит (year, month, day, hour, minute, second)
            setDateTime(*y)

        elif 'PyQt5.QtCore.QDateTime' in str(type_y):
            # так сделано, чтобы не импортировать PyQt до того пока действительно не будет нужен
            setQDateTime(y)

        elif 'PyQt5.QtCore.QDate' in str(type_y):
            # так сделано, чтобы не импортировать PyQt до того пока действительно не будет нужен
            setQDate(y)
            if 'PyQt5.QtCore.QTime' in str(type(m)):
                setQTime(m)

        return self
    


    # SETTERS ↲
    
    # ↓ задает текущее время
    def setNow(self):
        dt = datetime.datetime.now()
        self.y, self.m, self.d = dt.year, dt.month, dt.day
        self.H, self.M, self.S = dt.hour, dt.minute, dt.second
        self.tz = getLocalTimeZone()
        return self
    
    # ↓ создает копию chrono
    def setChrono(self, ch):
        self.y, self.m, self.d = ch.y, ch.m, ch.d
        self.H, self.M, self.S = ch.H, ch.M, ch.S
        self.tz = ch.tz
        return self
    
    # ↓ задает дату без проверки на валидацию
    def setTupleDate(self, y, m, d):
        # задается без проверки
        self.y, self.m, self.d = y, m, d
        return self

    # ↓ задает время без проверки на валидацию
    def setTupleTime(self, H, M, S):
        # задается без проверки
        self.H, self.M, self.S = H, M, S
        return self
    
    # ↓ задает дату из полученных аргументов
    def setDate(self, y = 1999, m = 1, d = 1):
        self.y, self.m, self.d = setDate(y, m, d)
        return self

    # ↓ задает время из полученных аргументов
    def setTime(self, H = 0, M = 0, S = 0):
        self.H, self.M, self.S = setTime(H, M, S)
        return self

    # ↓ задает дату из полученных аргументов
    def setDateTime(self, y = 1999, m = 1, d = 1, H = 0, M = 0, S = 0):
        self.y, self.m, self.d, self.H, self.M, self.S = setDateTime(y, m, d, H, M, S)
        return self
    
    # ↓ задает дату из datime.datime
    def setDT(self, dt):
        self.y, self.m, self.d = dt.year, dt.month, dt.day
        self.H, self.M, self.S = dt.hour, dt.minute, dt.second
        return self
    
    # ↓ задает дату из datime.date
    def setD(self, d):
        self.y, self.m, self.d = d.year, d.month, d.day
        self.H, self.M, self.S = 0, 0, 0
        return self
    
    # ↓ задает TimeZone без изменения состояния времения (СОКР.)
    def setTZ(self, tz):
        self.tz = setTimeZone(tz)

    # задает дату/время из UnixEpoch
    def setUnixEpoch(self, unixepoch):
        self.y, self.m, self.d, self.H, self.M, self.S = setUnixEpoch(unixepoch)

    # задает время обрабатывая строку
    def setTimeFromStr(self, string):
        self.H, self.M, self.S = setTimeFromStr(string)

    # задает дату/время обрабатывая строку
    def setISO(self, iso):
        self.y, self.m, self.d, self.H, self.M, self.S = setISO(iso)
        
    # задает дату/время обрабатывая строку
    def setDateTimeFromStr(self, string):
        self.y, self.m, self.d, self.H, self.M, self.S = setDateTimeFromStr(string)

    # задает дату/время обрабатывая строку согласно regex-шаблону
    def setByReGex(self, regex, string):
        self.y, self.m, self.d, self.H, self.M, self.S = setByReGex(regex, string)

    # задает дату/время обрабатывая строку согласно текстовому шаблону
    def setByTemplate(self, template, string):
        self.y, self.m, self.d, self.H, self.M, self.S = setByTemplate(template, string)

    # задает дату из PyQt5.QtCore.QDate
    def setQDate(self, qd):
        self.y, self.m, self.d = setQDate(qd)
        return self

    # задает время из PyQt5.QtCore.QTime
    def setQTime(self, qt):
        self.H, self.M, self.S = setQTime(qt)
        return self

    # задает дату/время из PyQt5.QtCore.QDateTime
    def setQDateTime(self, qdt):
        self.y, self.m, self.d, self.H, self.M, self.S = setQDateTime(qdt)
        return self

    # задает время из строки. Так же в строке после времени указывается смещение
    def setTimeShift(self, string):
        self.y, self.m, self.d, self.H, self.M, self.S = setTimeShift(
            string, self.y, self.m, self.d, self.H, self.M, self.S
        )
        return self
        
    # ↓ задает TimeZone без изменения состояния времения
    def setTimeZone(self, tz):
        self.tz = setTimeZone(tz)
        return self
    


    # QUASTIONS ↲


    # ↓ является текущая дата UTC?
    def isUTC(self):
        return True if self.tz == "UTC" else False

    # ↓ является текущая дата НЕ UTC? False - если локализация вообще не задана
    def isLocal(self):
        return True if self.tz != "UTC" and self.tz is not None else False

    # ↓ является ли год текущей даты високосным?
    def isLeapYear(self):
        return isLeapYear(self.y)

    # ↓ время больше 00:00:00?
    def isDayBegun(self):
        return isDayBegun(self.H, self.M, self.S)



    # MUTATTORS ↲
    
    # задает смещение даты текстовыми командами
    def shiftTC(self, string):
        self.y, self.m, self.d, self.H, self.M, self.S = shiftTextCommand(
            string, [self.y, self.m, self.d, self.H, self.M, self.S]
        )
        return self
    
    # задает смещение даты текстовыми командами
    def __call__(self, string):
        return self.shiftTC(string)

    # задает смещение даты посредством передачи именованных аргументов
    def shift(self, second = 0, year = 0, month = 0, day = 0, hour = 0, minute = 0, week = 0):
        self.y, self.m, self.d, self.H, self.M, self.S = shift(
            second, year, month, day, hour, minute, week,
            [self.y, self.m, self.d, self.H, self.M, self.S]
        )
        return self
    
    # конвертирует время для заданного часового пояса
    def toTimeZone(self, tz='UTC'):
        self.y, self.m, self.d, self.H, self.M, self.S = toTimeZone(
            self.tz, tz, (self.y, self.m, self.d, self.H, self.M, self.S)
        )
        return self
    
    # конвертирует время в UTC
    def toUTC(self):
        self.y, self.m, self.d, self.H, self.M, self.S = toTimeZone(
            self.tz, 'UTC', (self.y, self.m, self.d, self.H, self.M, self.S)
        )
        return self
    
    # конвертирует время в локальное для компьютера
    def toLocal(self):
        self.y, self.m, self.d, self.H, self.M, self.S = toTimeZone(
            ftz = self.tz, tdt=(self.y, self.m, self.d, self.H, self.M, self.S)
        )
        return self



    # GETTERS ↓

    # ↓ получить python-объект datetime.datetime
    def getDateTime(self):
        return datetime.datetime(self.y, self.m, self.d, self.H, self.M, self.S)

    # ↓ получить python-объект datetime.date
    def getDate(self):
        return datetime.date(self.y, self.m, self.d)

    # ↓ получить tuple-даты/времени
    def getTupleDateTime(self):
        return (self.y, self.m, self.d, self.H, self.M, self.S, self.tz)
    
    # ↓ получить tuple-даты/времени. Аналог getTupleDateTime result = *chrono_object
    def __iter__(self):
        return iter((self.y, self.m, self.d, self.H, self.M, self.S, self.tz))

    # ↓ получить tuple-даты
    def getTupleDate(self):
        return (self.y, self.m, self.d)

    # ↓ получить tuple-времени
    def getTupleTime(self):
        return (self.H, self.M, self.S)
    
    # ↓ получить смещение времени относительно UTC
    def getOffsetByUTC(self):
        return getOffsetByUTC(self.tz)
    
    # ↓ получить количество дней с начала года
    def getDayYear(self):
        return getDayYear(self.y, self.m, self.d)

    # ↓ получить время в строке формата ISO
    def getISO(self):
        return getISO(self.y, self.m, self.d, self.H, self.M, self.S, self.tz)
    
    # ↓ получить время в формате UnixEpoch
    def getUnixEpoch(self):
        return getUnixEpoch(self.y, self.m, self.d, self.H, self.M, self.S, self.tz)
    
    # ↓ получить номер декады месяца в которую входит текущая дата
    def getDecade(self):
        return getDecade(self.d)
    
    # ↓ получить номер декады с начала года в которую входит текущая дата
    def getDecadeByYear(self):
        return getDecadeByYear(self.m, self.d)

    # ↓ получить день недели для текущей даты
    def getWeekday(self): # 0 - ПНД
        return getWeekday(self.y, self.m, self.d)
    
    # ↓ получить неделю с начала года, начиная с первого понедельника
    def getWeekYear(self):
        return getWeekYear(self.y, self.m, self.d)

    # ↓ получить последний день месяца
    def getLastDayMonth(self):
        return getLastDayMonth(self.y, self.m)
    
    # ↓ # получить век
    def getCentury(self):
        return getCentury(self.y)
    


    # FOMATTER ↲

    # ↓ форматирование по шаблону типа %Y-%m-%d %H:%M:%S
    def F(self, temp):
        return format(temp, self.y, self.m, self.d, self.H, self.M, self.S, self.tz)

    # ↓ форматирование по шаблону типа yyyy-MM-dd hh:mm:ss
    def T(self, temp):
        return template(temp, self.y, self.m, self.d, self.H, self.M, self.S, self.tz)
    
    def __str__(self):
        temp = 'yyyy-MM-dd hh:mm:ss (tz)'
        return template(temp, self.y, self.m, self.d, self.H, self.M, self.S, self.tz)
    
    def __repr__(self):
        temp = 'Chrono(%Y, %m, %d, %H, %M, %S, "%Z")'
        return format(temp, self.y, self.m, self.d, self.H, self.M, self.S, self.tz)



    # OPERATORS ↲

    #self < other
    def __lt__(self, other):
        return True if self.getUnixEpoch() < other.getUnixEpoch() else False

    #self <= other
    def __le__(self, other):
        return True if self.getUnixEpoch() <= other.getUnixEpoch() else False

    #self == other
    def __eq__(self, other):
        return True if self.getUnixEpoch() == other.getUnixEpoch() else False

    #self != other
    def __ne__(self, other):
        return True if self.getUnixEpoch() != other.getUnixEpoch() else False

    #self > other
    def __gt__(self, other):
        return True if self.getUnixEpoch() > other.getUnixEpoch() else False

    #self >= other
    def __ge__(self, other):
        return True if self.getUnixEpoch() >= other.getUnixEpoch() else False
    
    # вычислить разницу между двумя датами
    def __sub__(self, other):
        if isinstance(other, datetime):
            pass
        elif isinstance(other, self.chrono):
            d1 = datetime.datetime(self.y, self.m, self.d, self.H, self.M, self.S)
            td = (other.y, other.m, other.d, other.H, other.M, other.S)
            d2 = datetime.datetime(*td) if self.tz == other.tz else datetime.datetime(
                *toTimeZone( other.tz, self.tz, td )
            )
            return (d1 - d2).total_seconds()

        return None


if __name__ == '__main__':
    a = Chrono("2018-01-01")

    print(a.__repr__())
    print(a)

    b = eval(a.__repr__())
    print(*b)