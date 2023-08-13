import datetime, pytz
from re import findall, sub
from ch_validators import isLeapYear
from tzlocal import get_localzone



def shiftTextCommand(string, tdt = [1970, 1, 1, 0, 0, 0]):
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

    sh= f' {string.lower()} '

    yy = findall(r'([- +]\d+)y', sh)
    mo = findall(r'([- +]\d+)mo', sh)
    mo += findall(r'([- +]\d+)M', sh)
    dd = findall(r'([- +]\d+)d', sh)
    HH = findall(r'([- +]\d+)h', sh)
    MM = findall(r'([- +]\d+)m ', sh)
    SS = findall(r'([- +]\d+)s', sh)
    WW = findall(r'([- +]\d+)w', sh)
    # ↓ если передано число безх текстового индикатора, то оно считается как минуты
    MM.extend(findall(r'([- +]\d+)[ ]', sh))

    if len(yy) != 0: shift_args['year']   = sum([int(x) for x in yy])
    if len(mo) != 0: shift_args['month']  = sum([int(x) for x in mo])
    if len(dd) != 0: shift_args['day']    = sum([int(x) for x in dd])
    if len(HH) != 0: shift_args['hour']   = sum([int(x) for x in HH])
    if len(MM) != 0: shift_args['minute'] = sum([int(x) for x in MM])
    if len(SS) != 0: shift_args['second'] = sum([int(x) for x in SS])
    if len(WW) != 0: shift_args['week']   = sum([int(x) for x in WW])

    return shift(tdt = tdt, **shift_args)



def shift( 
        second = 0, year = 0, month = 0, day = 0, hour = 0, minute = 0, week = 0,
        tdt = (1970, 1, 1, 0, 0, 0)
    ):
    
    y, m, d, H, M, S = tdt
    delta_seconds = second + (minute * 60) + (hour * 3600) +  (day * 86400) + (week * 86400 * 7)

    dt = datetime.datetime(y, m, d, H, M, S) + datetime.timedelta(seconds = delta_seconds)
    y, m, d = dt.year, dt.month, dt.day
    H, M, S = dt.hour, dt.minute, dt.second

    # Если указан год или месяц, то 
    # находится следующая дата + следующего года или месяца

    if month != 0:
        m += month
        if m < 1:
            while m < 1:
                m += 12
                y -= 1
        elif m > 12:
            while m > 12:
                m -= 12
                y += 1

    y += year

    count_days = {
        1:31,
        2:29 if isLeapYear(y) else 28,
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

    if d > count_days[m]: 
        d = count_days[m]

    return (y, m, d, H, M, S)



def toTimeZone(ftz = None, tz = None, tdt = [1970, 1, 1, 0, 0, 0]):
    # переводит время из временной зоны fromTZ в tz
    y, m, d, H, M, S = tdt

    if tz is None:
        tz = get_localzone()
    
    if ftz is None:
        ftz = get_localzone()

    current_time = datetime.datetime(y, m, d, H, M, S)

    current_tz = pytz.timezone(str(ftz))
    new_tz = pytz.timezone(str(tz))

    current_time = current_tz.localize(current_time)

    nt = current_time.astimezone(new_tz)

    return (nt.year, nt.month, nt.day, nt.hour, nt.minute, nt.second)
