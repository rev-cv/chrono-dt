import datetime
from ch_validators import isDayBegun, isLeapYear

def fragmentByDay(s, f):
    # разбивает период s—f по дням
    # начало дня → 2023-05-10 00:00:00
    # окончание дня → 2023-05-11 00:00:00

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

def fragmentByDecade(s, f):
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

    if current >= ending:
        raise Exception("The period cannot be fragmented into intervals of a long decade.")

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

def fragmentByMonth(s, f):
    ys, ms, ds, Hs, Ms, Ss = s
    yf, mf, df, Hf, Mf, Sf = f

    fragments = list()
    proceed = True

    if isDayBegun(Hs, Ms, Ss) or ds > 1:
        ys, ms = (ys, ms + 1) if ms + 1 <= 12 else (ys + 1, 1)

    current = datetime.datetime(ys, ms, ds, 0, 0, 0).timestamp()
    ending = datetime.datetime(yf, mf, 1, 0, 0, 0).timestamp()

    i30 = 2592000 # 30 дней
    i31 = 2678400 # 31 дней в некоторых 3х декадах месяца
    i29 = 2505600 # 29 дней в феврале високосного года
    i28 = 2419200 # 28 дней в феврале обычного года

    increments = {
        1:  i30,
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

def fragmentByWeek(s, f):
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

def fragmentByQuarter(s, f):
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

def fragmentByYear(s, f):
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

def fragmentByDecennary(s, f):
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

def fragmentByHour(s, f):
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

def fragmentByMinute(s, f):
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

def joinIntervals(i1s, i1f, i2s, i2f, greedy = False):
    if greedy:
        chs = sorted([
            datetime.datetime(*i1s),
            datetime.datetime(*i1f),
            datetime.datetime(*i2s),
            datetime.datetime(*i2f)
        ])
        return (chs[0], chs[-1])
    else:
        result = defineBoundary(i1s, i1f, i2s, i2f)
        if result is not False:
            return result
    raise Exception("Combining these two intervals according to the given parameters is not possible!")

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