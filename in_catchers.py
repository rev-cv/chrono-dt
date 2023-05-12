from ch_mutators import shift
from ch_pitchers import getWeekday, getUnixEpoch

def setStart(start, isExpansion, roundOff):
    # start = [1970, 1, 1, 0, 0, 0]
    if roundOff is not None:
        if isExpansion is True:
            return decrease(start, roundOff)
        elif isExpansion is False:
            return increase(start, roundOff)
    return start

def setFinish(finish, isExpansion, roundOff):
    # finish = [1970, 1, 1, 0, 0, 0]
    if roundOff is not None:
        if isExpansion is True:
            return increase(finish, roundOff)
        elif isExpansion is False:
            return decrease(finish, roundOff)
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
    elif 'decade' == ro:
        H, M, S = 0, 0, 0
        if d <= 10:
            d = 11
        elif d <= 20:
            d = 21
        else:
            y, m, d, H, M, S = shift(month=1, tdt=(y, m, 1, H, M, S))
    elif 'quarter' == ro:
        H, M, S, d = 0, 0, 0, 1
        if m <= 3:
            m = 4
        elif m <= 6:
            m = 7
        elif m <= 9:
            m = 10
        else:
            y, m = y + 1, 1
    elif 'decennary' == ro:
        H, M, S = 0, 0, 0,
        d, m = 1, 1
        y = int(str(y)[:-1] + "0") + 10
    elif "minute" == ro:
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
    elif 'decade' == ro:
        H, M, S = 0, 0, 0
        if d <= 10:
            d = 1
        elif d <= 20:
            d = 11
        else:
            d = 21
    elif 'quarter' == ro:
        H, M, S, d = 0, 0, 0, 1
        if m < 4:
            m = 1
        elif m < 7:
            m = 4
        elif m < 10:
            m = 7
        else:
            m = 10
    elif 'decennary' == ro:
        H, M, S = 0, 0, 0,
        d, m = 1, 1
        y = int(str(y)[:-1] + "0")
    elif "minute" == ro:
        S = 0
    elif 'week' == ro:
        # смещение до прошлого понедельника
        y, m, d, H, M, S = shift(
            day = getWeekday(y, m, d) * (-1) + 1, 
            tdt=(y, m, d, 0, 0, 0)
        )
        
    return (y, m, d, H, M, S)

fos = (None, 'decennary', 'year', 'quarter', 'month', 'decade', 'week', 'day', 'hour', 'minute')

def setRoundOff(roundOff):
    if roundOff in fos:
        return roundOff
    raise Exception("Invalid argument passed for 'roundOff'")

def setFramentation(start, finish, intervals):
    # задает список интервалов для self.fragments
    # Из переданного исписка исключаются интервалы не входящие в self
    # интервалы входящие частично в self обрезаются 
    s1 = getUnixEpoch(*start)
    f1 = getUnixEpoch(*finish)

    fragments = list()

    for x in intervals:
        s2 = getUnixEpoch(*x.s)
        f2 = getUnixEpoch(*x.f)

        if s1 <= s2 and f2 <= f1:
            # интервал входит в self
            fragments.append( [x.s, x.f] )
        elif s2 < s1 and s1 < f2 <= f1:
            # старт интервала начинается раньше self. Обрезать!
            fragments.append( [start, x.f])
        elif s1 <= s2 < f1 and f2 > f1:
            # старт интервала начался в self, но завершился после окончания self. Образать!
            fragments.append( [x.s, finish] )
        elif s2 <= s1 and f1 <= f2:
            # интервал поглощается self, обрезать с двух сторон
            fragments.append( [start, finish] )
    
    return fragments

