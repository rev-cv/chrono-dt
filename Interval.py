
import datetime
from ch_in_catchers import setRoundOff, setInterval
from ch_in_validators import (
    isReal,
    isDateWithinInterval,
    isIntervalWithinInterval,
    isTupleInterval
)
from Chrono import Chrono
from ch_in_mutators import chgToStepInterval
from IntervalsGenerate import (
    merge2Intervals,
    fragmentByDay,
    fragmentByDecade,
    fragmentByMonth,
    fragmentByWeek,
    fragmentByQuarter,
    fragmentByYear,
    fragmentByDecennary,
    fragmentByHour,
    fragmentByMinute,
    fragmentByIntervals,
    subtractByIntervals,
    convertIntervals,
)
from ch_in_pitchers import getСompleted

class Interval(object):
    def __init__(self, dates = None, roundoff = None, expansion=True):
        super(Interval, self).__init__()

        self.s = None  # start начало временного интервала
        self.f = None  # finish конец временного интервала
        self.tz = None # временная зона периода

        self.roundoff = setRoundOff(roundoff)
        self.expansion = expansion

        self.set(dates)
    

    # SETTERS ↲

    def set(self, dates):
        if type(dates) is tuple or type(dates) is list:
            if isTupleInterval(dates):
                # интервал получен как ((1970, 1, 1, 0, 0, 0), (1970, 1, 25, 0, 0, 0))
                self.s, self.f = setInterval(dates[0], dates[1], self.roundoff, self.expansion)
            elif isinstance(dates[0], Chrono) and isinstance(dates[1], Chrono):
                # интервал получен как (Chrono, Chronon)
                if dates[0].tz != dates[1].tz:
                    dates[1].toTimeZone(dates[0].tz)
                self.s, self.f = setInterval(
                    (dates[0].y, dates[0].m, dates[0].d, dates[0].H, dates[0].M, dates[0].S),
                    (dates[1].y, dates[1].m, dates[1].d, dates[1].H, dates[1].M, dates[1].S),
                    self.roundoff, self.expansion
                )
            elif type(dates[0]) is str and type(dates[1]) is str:
                cs = Chrono(dates[0])
                cf = Chrono(dates[1])
                self.s, self.f = setInterval(
                    (cs.y, cs.m, cs.d, cs.H, cs.M, cs.S),
                    (cf.y, cf.m, cf.d, cf.H, cf.M, cf.S),
                    self.roundoff, self.expansion
                )
            else:
                raise Exception(f"{__name__}.{self.set.__name__}(): It is not clear what was received.")
            
        elif isinstance(dates, Interval):
            # интервал получен как Interval
            self.s, self.f = list(*dates.s), list(*dates.f)
            self.tz = dates.tz
            self.roundoff = dates.roundoff
            self.expansion = dates.expansion

        elif isinstance(dates, Chrono):
            self.s, self.f = setInterval(
                dates.getTupleDateTime()[:-1], None, self.roundoff, self.expansion
            )
            self.tz = dates.tz

        else:
            self.s, self.f = setInterval(dates, None, self.roundoff, self.expansion)

        return self
    

    # QUASTIONS ↲

    # ↓ является ли полученный интервал реальным?
    def isReal(self):
        return isReal(self.s, self.f, self.expansion, isGenerateError=False)
    
    # ↓ входит ли дата или аргумент в данный интервал?
    def isIncluded(self, arg = None, isFullEntry=False):

        # ↓ если передан период
        if (type(arg) is tuple or type(arg) is list) and len(arg) == 2:
            return isIntervalWithinInterval(self.s, self.f, arg[0], arg[1], isFullEntry)
        elif isinstance(arg, Interval):
            return isIntervalWithinInterval(self.s, self.f, arg.s, arg.f, isFullEntry)
        
        # ↓ если передана дата
        else:
            d = Chrono(arg)
            return isDateWithinInterval(self.s, self.f, d.getDateTime())
    

    # MUTATTORS ↲

    # ↓ next / prev интервал в зависимости от заданного roundoff и шагов
    def step(self, st=0):
        self.s, self.f = chgToStepInterval(self.s, st, self.roundoff)
        return self

    # ↓ объединяет два интервала
    def join(self, i2, greedy = False):
        if (type(i2) is tuple or type(i2) is list) and len(i2) == 2:
            self.s, self.f = merge2Intervals(self.s, self.f, i2[0], i2[1], greedy)
        elif isinstance(i2, Interval):
            self.s, self.f = merge2Intervals(self.s, self.f, i2.s, i2.f, greedy)
        else:
            i2 = Interval(i2)
            self.s, self.f = merge2Intervals(self.s, self.f, i2.s, i2.f, greedy)
        return self
    
    # ↓ объединяет два интервала, если между ними нет пропуска
    def __truediv__(self, other): # ( / )
        return self.join(i2 = other, greedy = False)

    # ↓ объединяет два интервала даже если между ними есть пропуск
    # пропуск становится частью нового интервала
    def __floordiv__(self, other): # ( // )
        return self.join(i2 = other, greedy = True)
    
    
    # GENERATOR NEW INTERVALS ↲

    # ↓ фрагментирует данный интервал на более мелкие интервалы 
    def fragment(self, intervals="day") -> list:
        if type(intervals) is str:
            # передано указание, на какие интервалы дробить данный интервал
            if "day" == intervals:
                return fragmentByDay(self.s, self.f)
            elif "month" == intervals:
                return fragmentByMonth(self.s, self.f)
            elif "week" == intervals:
                return fragmentByWeek(self.s, self.f)
            elif "qua" == intervals[:3]: # quarter
                return fragmentByQuarter(self.s, self.f)
            elif "year" == intervals:
                return fragmentByYear(self.s, self.f)
            elif "dece" == intervals[:4]: # decennary
                return fragmentByDecennary(self.s, self.f)
            elif "dec" == intervals[:3]: # decade
                return fragmentByDecade(self.s, self.f)
            elif "hour" == intervals:
                return fragmentByHour(self.s, self.f)
            elif "min" == intervals[:3]: # minute
                return fragmentByMinute(self.s, self.f)
        elif type(intervals) is tuple or type(intervals) is list and len(intervals) > 0:
            # переданные интервалы будут вписаны в self-интервал (обрезаны и удалены)
            intervals = convertIntervals(intervals)
            return fragmentByIntervals(self.s, self.f, intervals)
        return list()

    # ↓ «вычитает» из self-интервала переданные интервалы
    # возвращает интервалы оставшиеся после «вычитания» 
    def subtract(self, intervals) -> list:
        intervals = convertIntervals(intervals)
        return subtractByIntervals(self.s, self.f, intervals)



    def start(self):
        return Chrono(*self.s)

    def finish(self):
        return Chrono(*self.f)
    
    def dts(self):
        return datetime.datetime(*self.s)

    def dtf(self):
        return datetime.datetime(*self.f)
    
    def qdts(self):
        pass

    def qdtf(self):
        pass

    def getСompleted(self, d):
        if isinstance(d, Chrono):
            return getСompleted(self.s, self.f, (d.y, d.m, d.d, d.H, d.M, d.S))
        elif isinstance(d, datetime.datetime):
            return getСompleted(self.s, self.f, (d.year, d.month, d.day, d.hour, d.minute, d.second))


    def __str__(self) -> str:
        print(self.s, self.f)
        return f'{self.s[0]}-{self.s[1]}-{self.s[2]} — {self.f[0]}-{self.f[1]}-{self.f[2]}'
    
    

if __name__ == '__main__':
    # a = Interval("2023-05-12", 'dece')
    # aa = a.fragment("dec")

    # for x in aa:
    #     print(x)

    # print(len(aa))

    bb = subtractByIntervals(
        [2023, 5, 14, 0, 0, 0],
        [2023, 5, 15, 0, 0, 0],
        [ 
            [ [2023, 5, 14, 15, 0, 0], [2023, 5, 14, 18, 0, 0]],
            [ [2023, 5, 14, 9, 0, 0], [2023, 5, 14, 10, 0, 0]]
        ]
    )
    
    for x in bb:
        print(x)