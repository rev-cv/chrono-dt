import datetime
from ch_mutators import shift
from ch_pitchers import getWeekday
from Chrono import Chrono

def setInterval(start = None, finish = None, roundoff = None, expansion=True):
    # start → [1970, 1, 1, 0, 0, 0]

    result = [[1970, 1, 1, 0, 0, 0], [1970, 1, 1, 0, 0, 0]]

    

    if start is False:
        # предполгается, что интервал будет задан вручную
        return result

    if start is not None and finish is not None:
        # → передано начало и окончание интервала
        # → динамическое «округление» не задано (roundoff is None) 

        if type(start) is not list or type(start) is not tuple:
            s = Chrono(start)
            start = [s.y, s.m, s.d, s.H, s.M, s.S]
        if type(finish) is not list or type(start) is not tuple:
            f = Chrono(finish)
            finish = [f.y, f.m, f.d, f.H, f.M, f.S]

        result[0] = setStart(start, expansion, roundoff)
        result[1] = setFinish(finish, expansion, roundoff)
    else:
        roundoff = "day" if roundoff is None else roundoff
        # ↑ если для интервала не передано start и finish, то ↲
        # дальнейшее создание интервала не имеет смысла ↲
        # без заданных roundoff и expansion
            
        if start is not None and finish is None:
            result[0] = setStart(start, expansion, roundoff)
            result[1] = setFinish(start, expansion, roundoff)

        elif start is None and finish is not None:
            result[0] = setStart(finish, expansion, roundoff)
            result[1] = setFinish(finish, expansion, roundoff)
            
        else:
            now = datetime.datetime.now()
            tuplenow = [now.year, now.month, now.day, now.hour, now.minute, now.second]
            result[0] = setStart(tuplenow, expansion, roundoff)
            result[1] = setFinish(tuplenow, expansion, roundoff)
            
    if datetime.datetime(*result[0]) < datetime.datetime(*result[1]):
        return result    
    raise Exception("Error. The resulting interval is subject to collapse.")

def setStart(start, expansion, roundoff):
    # start = [1970, 1, 1, 0, 0, 0]
    if roundoff is not None:
        if expansion is True:
            return decrease(start, roundoff)
        elif expansion is False:
            return increase(start, roundoff)
    return start

def setFinish(finish, expansion, roundoff):
    # finish = [1970, 1, 1, 0, 0, 0]
    if roundoff is not None:
        if expansion is True:
            return increase(finish, roundoff)
        elif expansion is False:
            return decrease(finish, roundoff)
    return finish

def increase(td, ro):
    # смещение даты вправо по исторической шкале
    y, m, d, H, M, S = td
    if 'day' == ro:
        y, m, d, H, M, S = shift(day=1, tdt=(y, m, d, 0, 0, 0))
    elif 'month' == ro:
        y, m, d, H, M, S = shift(month=1, tdt=(y, m, 1, 0, 0, 0))
    elif 'hour' == ro:
        y, m, d, H, M, S = shift(hour=1, tdt=(y, m, d, H + 1, 0, 0))
    elif 'year' == ro:
        y, m, d, H, M, S = y + 1, 1, 1, 0, 0, 0
    elif 'dece' == ro[:4]: # decennary
        H, M, S = 0, 0, 0,
        d, m = 1, 1
        y = int(str(y)[:-1] + "0") + 10
    elif 'dec' == ro[:3]: # decade
        H, M, S = 0, 0, 0
        if d <= 10:
            d = 11
        elif d <= 20:
            d = 21
        else:
            y, m, d, H, M, S = shift(month=1, tdt=(y, m, 1, H, M, S))
    elif 'qua' == ro[:3]: # quarter
        H, M, S, d = 0, 0, 0, 1
        if m <= 3:
            m = 4
        elif m <= 6:
            m = 7
        elif m <= 9:
            m = 10
        else:
            y, m = y + 1, 1
    elif "min" == ro[:3]: # minute
        y, m, d, H, M, S = shift(minute=1, tdt=(y, m, d, H, M, 0))
    elif 'week' == ro:
        # смещение до следующего понедельника
        y, m, d, H, M, S = shift(
            day = 8 - getWeekday(y, m, d), 
            tdt=(y, m, d, 0, 0, 0)
        )

    return (y, m, d, H, M, S)

def decrease(td, ro):
    y, m, d, H, M, S = td
    # смещение даты влево по исторической шкале
    if 'day' == ro:
        H, M, S = 0, 0, 0
    elif 'month' == ro:
        H, M, S, d = 0, 0, 0, 1
    elif 'hour' == ro:
        M, S = 0, 0
    elif 'year' == ro:
        H, M, S = 0, 0, 0
        d, m = 1, 1
    elif 'dece' == ro[:4]: # decennary
        H, M, S = 0, 0, 0,
        d, m = 1, 1
        y = int(str(y)[:-1] + "0")
    elif 'dec' == ro[:3]: # decade
        H, M, S = 0, 0, 0
        if d <= 10:
            d = 1
        elif d <= 20:
            d = 11
        else:
            d = 21
    elif 'qua' == ro[:3]: # quarter
        H, M, S, d = 0, 0, 0, 1
        if m < 4:
            m = 1
        elif m < 7:
            m = 4
        elif m < 10:
            m = 7
        else:
            m = 10
    elif "min" == ro[:3]: # minute
        S = 0
    elif 'week' == ro:
        # смещение до прошлого понедельника
        y, m, d, H, M, S = shift(
            day = getWeekday(y, m, d) * (-1) + 1, 
            tdt=(y, m, d, 0, 0, 0)
        )
        
    return (y, m, d, H, M, S)

fos = (
    None, 
    'decennary', 'year', 'quarter', 'month', 'decade', 'week', 'day', 'hour', 'minute',
    'dece', 'qua', 'dec', 'min'
)

def setRoundOff(roundoff):
    if roundoff in fos:
        return roundoff
    raise Exception("Invalid argument passed for 'roundoff'")


