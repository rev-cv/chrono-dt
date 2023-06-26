import datetime
from ch_validators import isDayBegun, isLeapYear
from ch_in_validators import isTupleInterval

def sumIntervals(interval_list, measure='second'):
    # общая сумма всех интервалов содержащихся в self

    def getDuration(i1, i2, measure='second'):
        diff = (datetime.datetime(*i2) - datetime.datetime(*i1)).total_seconds()

        if 'second' == measure:
            return diff
        elif 'minute' == measure:
            return diff // 60
        elif 'hour' == measure:
            return round(diff / 3600, 1)
        elif 'day' == measure:
            return round(diff / 86400, 1)
    
    sumfrags = 0.0
    for x in interval_list:
        sumfrags += getDuration(x[0], x[1], measure)
    return sumfrags


def occIntervals(interval_list, measure='second'):  # occupancy / заполненность
    # sumIntervals → сумма всех интервалов
    # occIntervals → сумма интервалов без учета наслаивания ↲
    # т.е. сколько времени занимают все интервалы

    diff = 0

    for x in mergeIntervals(interval_list, False):
        diff += x[1] - x[0]
    
    if 'second' == measure:
        return diff
    elif 'minute' == measure:
        return diff // 60
    elif 'hour' == measure:
        return round(diff / 3600, 1)
    elif 'day' == measure:
        return round(diff / 86400, 1)


def getOccupancyPercent(s, f, intervals) -> float:
    # выдает процент заполненности интервала s—f интервалами из intervals
    intervals = fragmentByIntervals(s, f, intervals)
    # ↑ убирает и обрезает интервалы выходящие за пределы s—f
    # ↓ длительность периода s—f
    diff = (datetime.datetime(*f) - datetime.datetime(*s)).total_seconds()
    # ↓ временная заполненность времени интервалами
    frag = occIntervals(intervals)
    return round(frag * 100 / diff, 1)


def findSkipIntervals(interval_list) -> list:
    # находит между интервалами пропуски
    # возвращает найденные пропуски в виде интервалов
    result = list()
    union_intervals = mergeIntervals(interval_list)
    lastfinish = None

    for x in union_intervals:
        if lastfinish is None:
            lastfinish = x[1]
        else:
            if lastfinish < x[0]:
                result.append( (lastfinish, x[0]) )
                lastfinish = x[1]
    
    return result


def defineBoundary(i1s, i1f, i2s, i2f):
    # определяет включенность одного интервала в другой
    # если возможно объединение объединяет эти два интервала в один

    u1 = datetime.datetime(*i1s)
    u2 = datetime.datetime(*i1f)
    u3 = datetime.datetime(*i2s)
    u4 = datetime.datetime(*i2f)

    if u3 <= u1 and u2 <= u4:
        # 1 into 2
        return (i2s, i2f)
    elif u1 <= u3 and u4 <= u2:
        # 2 into 1
        return (i1s, i1f)
    elif u2 == u3 or (u3 < u2 and u1 <= u3):
        # i1 и i2 следуют друг за другом стык-в-стык
        # или начало i2 лежит в периоде i1
        return (i1s, i2f)
    elif u4 == u1 or (u1 < u4 and u3 <= u1):
        # i2 и i1 следуют друг за другом стык-в-стык
        # или начала i1 лежит в периоде i2
        return (i2s, i1f)
    
    return False


def merge2Intervals(i1s, i1f, i2s, i2f, greedy = False):
    # greedy=True — объединить два интервала (i1s—i1f & i2s—i2f) игнорируя пропуск между ними
    # greedy=False — объединить два интервала, если ↲
    # они входят друг-в-дружку или безразрывно следуют друг-за-другом

    if greedy:
        chs = sorted([
            datetime.datetime(*i1s),
            datetime.datetime(*i1f),
            datetime.datetime(*i2s),
            datetime.datetime(*i2f)
        ])
        s, f = chs[0], chs[-1]
        return (
            (s.year, s.month, s.day, s.hour, s.minute, s.second),
            (f.year, f.month, f.day, f.hour, f.minute, f.second)
        )
    else:
        result = defineBoundary(i1s, i1f, i2s, i2f)
        if result is not False:
            return result
    raise Exception(f'{__name__}.{merge2Intervals.__name__}(): Error when merging intervals. Merge options are probably set incorrectly.')


def mergeIntervals(interval_list, isTuple=True) -> list:
    # интервалы между которыми не существует пропусков объединяются в один интервал
    # выдается список объедененныъх интервалов
    result = list()

    def joiner(new_interval):
        nonlocal result

        if len(result) == 0:
            result.append(new_interval)
        else:
            # проверяется, вродит new_interval в один из добавленных интервалов
            isAdd = False
            
            for i in range(0, len(result)):
                u1, u2 = new_interval
                u3, u4 = result[i]

                if u3 <= u1 and u2 <= u4:
                    # 1 into 2
                    # result[i] = result[i]
                    isAdd = False
                    break
                elif u1 <= u3 and u4 <= u2:
                    # 2 into 1
                    result[i] = (u1, u2)
                    isAdd = False
                    break
                elif u2 == u3 or (u3 < u2 and u1 <= u3):
                    # i1 и i2 следуют друг за другом стык-в-стык
                    # или начало i2 лежит в периоде i1
                    result[i] = (u1, u4)
                    isAdd = False
                    break
                elif u4 == u1 or (u1 < u4 and u3 <= u1):
                    # i2 и i1 следуют друг за другом стык-в-стык
                    # или начало i1 лежит в периоде i2
                    result[i] =  (u3, u2)
                    isAdd = False
                    break
                else:
                    isAdd = True
            
            if isAdd:
                # период никак не пересекается с уже добавленными периодами
                result.append(new_interval)

    toUnite = [ 
        ( 
            datetime.datetime(*x[0]).timestamp(), 
            datetime.datetime(*x[1]).timestamp() 
        ) 
        for x in interval_list 
    ]
    toUnite.sort(key=lambda c: c[0])


    for interval in toUnite:
        joiner(interval)

    
    if isTuple:

        joinedintervalstuples = list()
        for x in result:
            s = datetime.datetime.fromtimestamp(x[0])
            f = datetime.datetime.fromtimestamp(x[1])
            joinedintervalstuples.append((
                (s.year, s.month, s.day, s.hour, s.minute, s.second),
                (f.year, f.month, f.day, f.hour, f.minute, f.second),
            ))

        return joinedintervalstuples
    else:
        return result

def subtractByIntervals(s, f, intervals) -> list:
    # задать фрагментацию для интервала s—f ↲
    # посредством вычитания интервалов из s—f
    cutoff = fragmentByIntervals(s, f, intervals)
    skips = findSkipIntervals(cutoff)

    if len(cutoff) > 0:
        ds = sorted(cutoff, key=lambda x: datetime.datetime(*x[0]))
        if datetime.datetime(*s) != datetime.datetime(*ds[0][0]):
            skips.insert(0, (s, ds[0][0]))

        df = sorted(cutoff, key=lambda x: datetime.datetime(*x[1]))
        if datetime.datetime(*f) != datetime.datetime(*df[-1][1]):
            skips.append((df[-1][1], f))
    
    return skips

def fragmentByIntervals(s, f, intervals) -> list:
    # задать фрагментацию для интервала s—f
    # Из переданного исписка исключаются интервалы не входящие в self
    # интервалы входящие частично в self обрезаются 
    s1 = datetime.datetime(*s).timestamp()
    f1 = datetime.datetime(*f).timestamp()

    fragments = list()

    for x in intervals:
        s2 = datetime.datetime(*x[0]).timestamp()
        f2 = datetime.datetime(*x[1]).timestamp()

        if s1 <= s2 and f2 <= f1:
            # интервал входит в self
            fragments.append( (x[0], x[1]) )
        elif s2 < s1 and s1 < f2 <= f1:
            # старт интервала начинается раньше self. Обрезать!
            fragments.append( [s, x[1]] )
        elif s1 <= s2 < f1 and f2 > f1:
            # старт интервала начался в self, но завершился после окончания self. Образать!
            fragments.append( [x[0], f] )
        elif s2 <= s1 and f1 <= f2:
            # интервал поглощается self, обрезать с двух сторон
            fragments.append( [s, f] )
    
    return fragments


def fragmentByDay(s, f) -> list:
    # фрагментировать период s—f по дням
    # начало дня → 2023-05-11 00:00:00
    # окончание дня → 2023-05-12 00:00:00

    fragments = list()
    proceed = True

    current = datetime.datetime(s[0], s[1], s[2], 0, 0, 0).timestamp()
    ending = datetime.datetime(f[0], f[1], f[2], 0, 0, 0).timestamp()

    if isDayBegun(s[3], s[4], s[5]):
        current = current + 86400
    
    while proceed:
        if current < ending:
            sdt = datetime.datetime.fromtimestamp(current)
            fdt = sdt + datetime.timedelta(days=1)
            fragments.append([
                [sdt.year, sdt.month, sdt.day, 0, 0, 0],
                [fdt.year, fdt.month, fdt.day, 0, 0, 0],
            ])
        else:
            proceed = False
        current += 86400

    return fragments

def fragmentByDecade(s, f) -> list:
    # фрагментировать период s—f по декадам
    ys, ms, ds, Hs, Ms, Ss = s
    yf, mf, df, Hf, Mf, Sf = f

    fragments = list()
    current_dec = 0
    proceed = True

    sdb = isDayBegun(Hs, Ms, Ss)

    if ds == 1 and sdb is False:
        # день не началася и является первым числом месяца
        # это единственое условие при котором начало может оказаться первой декадой
        ds, current_dec = 1, 0
    elif ds < 11 or (ds == 11 and sdb is False):
        ds, current_dec = 11, 1
    elif ds < 21 or (ds == 21 and sdb is False):
        ds, current_dec = 21, 2
    else:
        ms, ds = ms + 1, 1
        if ms > 12:
            ys, ms = ys + 1, 1
    
    current = datetime.datetime(ys, ms, ds, 0, 0, 0).timestamp()
        
    if df <= 10:
        df = 1
    elif df <= 20:
        df = 11
    else:
        df = 21

    ending = datetime.datetime(yf, mf, df, 0, 0, 0).timestamp()

    i10 = 864000 # 10 дней
    i31 = 950400 # 11 дней в некоторых 3х декадах месяца
    i29 = 777600 # 9 дней в феврале високосного года
    i28 = 691200 # 8 дней в феврале обычного года

    increments = {
        1:  [i10, i10, i31],
        2:  [i10, i10, i29 if isLeapYear(ys) else i28],
        3:  [i10, i10, i31],
        4:  [i10, i10, i10],
        5:  [i10, i10, i31],
        6:  [i10, i10, i10],
        7:  [i10, i10, i31],
        8:  [i10, i10, i31],
        9:  [i10, i10, i10],
        10: [i10, i10, i31],
        11: [i10, i10, i10],
        12: [i10, i10, i31],
    }

    while proceed:
        while proceed and current_dec < 3:
            if current < ending:
                dt = datetime.datetime.fromtimestamp(current)
                y1, m1, d1 = dt.year, dt.month, dt.day
                y2, m2, d2 = dt.year, dt.month, dt.day

                if current_dec == 0:
                    m2, d2 = dt.month, 11
                elif current_dec == 1:
                    m2, d2 = dt.month, 21
                else:
                    m2, d2 = dt.month + 1, 1
                    if m2 > 12:
                        y2, m2 = dt.year + 1, 1

                fragments.append([
                    [y1, m1, d1, 0, 0, 0],
                    [y2, m2, d2, 0, 0, 0],
                ])
                
            else:
                proceed = False

            current += increments[ms][current_dec]
            current_dec += 1

        current_dec = 0

        if ms + 1 > 12:
            ms = 1
            ys += 1
            increments[2][2] = i29 if isLeapYear(ys) else i28
        else:
            ms += 1

    return fragments

def fragmentByMonth(s, f) -> list:
    # фрагментировать период s—f по месяцам
    ys, ms, ds, Hs, Ms, Ss = s
    yf, mf, df, Hf, Mf, Sf = f

    fragments = list()
    proceed = True

    if isDayBegun(Hs, Ms, Ss) or ds > 1:
        ys, ms = (ys, ms + 1) if ms + 1 <= 12 else (ys + 1, 1)

    current = datetime.datetime(ys, ms, 1, 0, 0, 0).timestamp()
    ending = datetime.datetime(yf, mf, 1, 0, 0, 0).timestamp()

    i30 = 2592000 # 30 дней
    i31 = 2678400 # 31 дней в некоторых 3х декадах месяца
    i29 = 2505600 # 29 дней в феврале високосного года
    i28 = 2419200 # 28 дней в феврале обычного года

    increments = {
        1:  i31,
        2:  i29 if isLeapYear(ys) else i28,
        3:  i31,
        4:  i30,
        5:  i31,
        6:  i30,
        7:  i31,
        8:  i31,
        9:  i30,
        10: i31,
        11: i30,
        12: i31,
    }
    
    while proceed:
        if current < ending:
            dt = datetime.datetime.fromtimestamp(current)
            y1, m1, d1 = dt.year, dt.month, dt.day
            y2, m2, d2 = dt.year, dt.month + 1, 1

            if m2 > 12:
                y2, m2 = y2 + 1, 1

            fragments.append([
                [y1, m1, d1, 0, 0, 0],
                [y2, m2, d2, 0, 0, 0],
            ])
        else:
            proceed = False

        current += increments[ms]

        if ms + 1 > 12:
            ys, ms = ys + 1, 1
            increments[2] = i29 if isLeapYear(ys) else i28
        else:
            ms = ms + 1

    return fragments

def fragmentByWeek(s, f) -> list:
    # фрагментировать период s—f по неделям
    ys, ms, ds, Hs, Ms, Ss = s
    yf, mf, df, Hf, Mf, Sf = f

    fragments = list()
    proceed = True

    sdt = datetime.datetime(ys, ms, ds, 0, 0, 0)
    if isDayBegun(Hs, Ms, Ss):
        sdt = sdt + datetime.timedelta(days=1)
    wdc = sdt.isoweekday()
    if wdc != 1:
        sdt = sdt + datetime.timedelta(days=8 - wdc)
    current = sdt.timestamp()
    
    fdt = datetime.datetime(yf, mf, df, 0, 0, 0)
    wdf =  sdt.isoweekday()
    if wdf != 1:
        fdt = fdt + datetime.timedelta(days=wdf * (-1) + 1)
    ending = fdt.timestamp()

    while proceed:
        if current < ending:
            dts = datetime.datetime.fromtimestamp(current)
            dtf = dts + datetime.timedelta(days=7)
            fragments.append([
                [dts.year, dts.month, dts.day, 0, 0, 0],
                [dtf.year, dtf.month, dtf.day, 0, 0, 0],
            ])
        else:
            proceed = False

        current += 604800 # 86400 * 7

    return fragments

def fragmentByQuarter(s, f) -> list:
    # фрагментировать период s—f по квартлам
    ys, ms, ds, Hs, Ms, Ss = s
    yf, mf, df, Hf, Mf, Sf = f

    fragments = list()
    proceed = True
    current_quarter = 1

    if ms == 1 and ds == 1 and isDayBegun(Hs, Ms, Ss) is False:
        ms = 1 # если 1 января и еще не начался день, то первый квартал
    elif ms <= 3:
        ms, current_quarter = 4, 2
    elif ms <= 6:
        ms, current_quarter = 7, 3
    elif ms <= 9:
        ms, current_quarter = 10, 4
    else:
        ys, ms = ys+1, 1
    current = datetime.datetime(ys, ms, 1, 0, 0, 0).timestamp()

    if mf <= 3:
        mf = 1
    elif mf <= 6:
        mf = 3
    elif mf <= 9:
        mf = 6
    elif mf <= 12:
        mf = 9
    ending = datetime.datetime(yf, mf, 1, 0, 0, 0).timestamp()

    fe = 29 if isLeapYear(ys) else 28
    increments = {
        1: (31 + fe + 31) * 86400,
        2: 7862400, # (30 + 31 + 30) * 86400,
        3: 7948800, # (31 + 31 + 30) * 86400,
        4: 7948800,
    }

    while proceed:
        while proceed and current_quarter <= 4:
            if current < ending:
                dts = datetime.datetime.fromtimestamp(current)
                dtf = dts + datetime.timedelta(days=round(increments[current_quarter] / 86400 + 2))
                fragments.append([
                    [dts.year, dts.month, 1, 0, 0, 0],
                    [dtf.year, dtf.month, 1, 0, 0, 0],
                ])
            else:
                proceed = False
            
            current += increments[current_quarter]
            current_quarter += 1
        
        ys += 1
        current_quarter = 1
        fe = 29 if isLeapYear(ys) else 28
        increments[1] = (31 + fe + 31) * 86400

    return fragments

def fragmentByYear(s, f) -> list:
    # фрагментировать период s—f по годам
    ys, ms, ds, Hs, Ms, Ss = s

    fragments = list()
    proceed = True

    if not ms == 1 and not ds == 1 and isDayBegun(Hs, Ms, Ss):
        ys += 1
    ending = f[0]

    while proceed:
        if ys < ending:
            fragments.append([
                [ys, 1, 1, 0, 0, 0],
                [ys + 1, 1, 1, 0, 0, 0]
            ])
        else:
            proceed = False
            
        ys += 1

    return fragments

def fragmentByDecennary(s, f) -> list:
    # фрагментировать период s—f по десятилетиям
    ys, ms, ds, Hs, Ms, Ss = s

    fragments = list()
    proceed = True

    if ms == 1 and ds == 1 or isDayBegun(Hs, Ms, Ss) is False:
        dy = ys // 10 * 10
        ys = dy if ys == dy else dy + 10
    else:
        ys = (ys // 10 + 1) * 10

    yf = f[0] // 10 * 10
    
    while proceed:
        if ys < yf:
            fragments.append([
                [ys, 1, 1, 0, 0, 0],
                [ys + 10, 1, 1, 0, 0, 0]
            ])
        else:
            proceed = False
        
        ys += 10

    return fragments

def fragmentByHour(s, f) -> list:
    # фрагментировать период s—f по часам
    ys, ms, ds, Hs, Ms, Ss = s
    yf, mf, df, Hf, Mf, Sf = f

    fragments = list()
    proceed = True

    current = datetime.datetime(ys, ms, ds, Hs, 0, 0)
    if Ms > 0 or Ss > 0:
        current = current + datetime.timedelta(hours=1)
    current = current.timestamp()
    ending = datetime.datetime(yf, mf, df, Hf, 0, 0).timestamp()

    while proceed:
        if current < ending:
            dts = datetime.datetime.fromtimestamp(current)
            dtf = datetime.datetime.fromtimestamp(current + 3600)
            fragments.append([
                [dts.year, dts.month, dts.day, dts.hour, 0, 0],
                [dtf.year, dtf.month, dtf.day, dtf.hour, 0, 0]
            ])
        else:
            proceed = False

        current += 3600

    return fragments

def fragmentByMinute(s, f) -> list:
    # фрагментировать период s—f по минутам
    ys, ms, ds, Hs, Ms, Ss = s
    yf, mf, df, Hf, Mf, Sf = f

    fragments = list()
    proceed = True

    current = datetime.datetime(ys, ms, ds, Hs, Ms, 0)
    if Ss > 0:
        current = current + datetime.timedelta(minute=1)
    current = current.timestamp()
    ending = datetime.datetime(yf, mf, df, Hf, Mf, 0).timestamp()

    while proceed:
        if current < ending:
            dts = datetime.datetime.fromtimestamp(current)
            dtf = datetime.datetime.fromtimestamp(current + 60)
            fragments.append([
                [dts.year, dts.month, dts.day, dts.hour, dts.minute, 0],
                [dtf.year, dtf.month, dtf.day, dtf.hour, dtf.minute, 0]
            ])
        else:
            proceed = False

        current += 60

    return fragments


def convertIntervals(intervals, to="tuple") -> list:
    # Принимает список предположительно интервалов
    # интервал может иметь вид
    # либо ((1970, 1, 1, 0, 0, 0), (1970, 1, 25, 0, 0, 0))
    # либо Interval()
    from Interval import Interval

    result = list()

    for x in intervals:

        isInterval = isinstance(x, Interval)
        
        if isInterval and to == "tuple":
            result.append(( x.s, x.f ))

        elif isInterval and to == "interval":
            result.append(x)

        else:
            isTuple = isTupleInterval(x)

            if isTuple  and to == "interval":
                result.append( Interval(x) )

            elif isTuple  and to == "tuple":
                result.append(x)
    
    return result



if __name__ == '__main__':
    a = [
        [[2023, 5, 13, 15, 5, 0], [2023, 5, 13, 18, 25, 0]],
        [[2023, 5, 13, 10, 25, 0], [2023, 5, 13, 11, 0, 0]],
        [[2023, 5, 13, 2, 5, 0], [2023, 5, 13, 9, 30, 0]],
        [[2023, 5, 13, 9, 30, 0], [2023, 5, 13, 10, 25, 0]],
        [[2023, 5, 13, 21, 0, 0], [2023, 5, 13, 22, 0, 0]],
        [[2023, 5, 13, 23, 0, 0], [2023, 5, 14, 1, 0, 0]],
    ]

    # for x in mergeIntervals(a):
    #     print(f'{x[0][3]:0>2}:{x[0][4]:0>2} - {x[1][3]:0>2}:{x[1][4]:0>2}')

    print(
        getOccupancyPercent(
            (2023, 5, 13, 0, 0, 0),
            (2023, 5, 14, 0, 0, 0),
            a
        )
    )

    for x in findSkipIntervals(a):
        print(f'{x[0][3]:0>2}:{x[0][4]:0>2} - {x[1][3]:0>2}:{x[1][4]:0>2}')


