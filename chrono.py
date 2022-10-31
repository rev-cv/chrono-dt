from Chrono.ch_transformator import ChronoTransformator
from Chrono.ch_catcher import ChronoCatcher
from Chrono.ch_pitcher import ChronoPitcher
from Chrono.ch_analyzer import ChronoAnalyzer
from Chrono.ch_operators import ChronoOperators
from String.string_deconstruction import Deconstruction
from String.string_construction import FormatterCrono, FormatterInterval

from Interval.in_catcher import IntervalCatcher
from Interval.in_analyzer import IntervalAnalyzer

class Chrono( ChronoCatcher, ChronoAnalyzer, ChronoPitcher, ChronoOperators,
        ChronoTransformator, Deconstruction, FormatterCrono ):

    def __init__(self, 
            y = None, m = None, d = None, 
            H = None, M = None, S = None, 
            shift = None, tz = "local"):


        super(Chrono, self).__init__()

        self.chrono = Chrono
        self.y = None
        self.m = None
        self.d = None
        self.H = None
        self.M = None
        self.S = None
        self.tz = None

        self.setTimeZone(tz)

        if y is not False:
            self.set(y, m, d, H, M, S)

        if shift is not None:
            if type(shift) is str:
                # принимает строку с текстовыми командами для смещения
                self.shiftTextCommand(shift)
            elif type(shift) is dict:
                # принимает словарь с текстовыми командами для смещения
                self.shift(**shift)

    def __str__(self):
        s = 'Object.Chrono('
        s += 'DATE yyyy-MM-dd ' if self.isDate() else 'DATE None '
        s += 'TIME hh:mm:ss ' if self.isTime() else 'TIME None '
        s += 'TZ tz)'
        return self.template(s)



class Interval(IntervalCatcher, FormatterInterval, IntervalAnalyzer):
    def __init__(self, s = None, f = None, roundOff = None, expand=True, tz=None, about=None):
        super(Interval, self).__init__()

        # roundOff — округляет интервал путем расширения, если expand=True
        # roundOff — округляет интервал путем уменьшения, если expand=False

        # ПРИМЕР start = <2022-10-25 12:45>, finish = <2022-11-26 4:35>

        # "hour" — округляет период до часа
                # expand=True  → <2022-10-25 12:00:00 — 2022-11-26 05:00:00>
                # expand=False → <2022-10-25 13:00:00 — 2022-11-26 04:00:00>
        # 'day' — округляет период до дня
                # expand=True  → <2022-10-25 00:00:00 — 2022-11-27 00:00:00>
                # expand=False → <2022-10-26 00:00:00 — 2022-11-26 00:00:00>
                # ↑ В данном случае должна быть ошибка "Использование `expand=False` 
                # привело к схлопыванию интервала"
                
                # Если в interval() передано только start или только finish, а roundOff == None
                # то применяются roundOff="day"

        # 'month' — округляет период до месяца
                # expand=True  → <2022-10-01 00:00:00 — 2022-11-30 00:00:00>
                # expand=False → <2022-11-01 00:00:00 — 2022-11-01 00:00:00>
                # ↑ В данном случае должна быть ошибка "Использование `expand=False` 
                # привело к схлопыванию интервала"

        # "year" — округляет интервал до года
                # expand=True  → <2022-01-01 00:00:00 — 2023-01-01 00:00:00>
                # expand=False → <2023-11-01 00:00:00 — 2022-11-01 00:00:00>
                # ↑ В данном случае должна быть ошибка "Интервал слишком короткий 
                # чтобы можно было использовать `expand=False` и 'roundOff='year'"
        # "decade" - декада месяца
        # `quarter` - квартал года
        # "decennary" - десятелетие

        self.chrono = Chrono
        self.s = None # start начало временного интервала
        self.f = None # finish конец временного интервала
        self.tz = tz
        self.about = about
        # ↑ Любая информация, которую можно присвоить интервалу
        # эта информация будет просто таскаться за интервалом
        # полезно, когда речь идет не о гипотетических интервалах

        self.fragments = []
        # ↑ список возможных дочерних интервалов

        self.roundOff = self.setRoundOff(roundOff)
        self.expand = expand

        self.set(s, f)

        self.isReal(True)
        

    def __str__(self):
        s = 'Object.Interval(\n'
        s += '    START START{{yyyy-MM-dd hh:mm:ss}}\n'
        s += '    FINISH FINISH{{yyyy-MM-dd hh:mm:ss}}\n'
        s += '    TZ tz\n'
        s += ')'
        return self.template(s)

    
class Intervals(object):
    """Обрабатывает список интервалов"""
    def __init__(self, intervals_list = None):
        super(Intervals, self).__init__()

    def getMissedIntervals(self):
        # создает список с интервалами, которые могут уместиться между текущими интевалами
        return []
    
    def getStackedIntervals(self):
        # выбрать наслаивающиеся друг на дружку интервалы
        pass
    
    def getCalendar(self, year):
        # получить матрицу интервалов содержащих указанный год
        # year.fragments(
        #   months.fragments(
        #       weeks.fragments(
        #           days
        #       )
        #   )
        # )
        pass
    
    def getFragmentation(self, interval, frag = "days"):
        # раздробить данный интервал на дни / часы / прочее
        pass
        

if __name__ == '__main__':
    # a = Chrono()
    # print(a)
    # b = chrono(a)
    # print(b)
    
    # from PyQt5.QtCore import QDateTime

    # time = QDateTime(2022, 11, 20, 11, 34, 34)
    # tz = time.timeZone()

    # for x in QTimeZone().availableTimeZoneIds():
    # 	x = x.__str__()
    # 	print(type(x), x[2:-1], len(x))

    # a = chrono("20221215", shift="-2y")
    # print(a)
    
    i = Interval(
        Chrono(2022, 5, 12),
        Chrono(2022, 12, 12)
    )
    print(i)
