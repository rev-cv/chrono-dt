import datetime
from tzlocal import get_localzone

from ch_validators import *
from ch_mutators import toTimeZone
from ch_formators import template



def getAllTimeZone():
    return all_timezones



def getLocalTimeZone():
    return get_localzone()



def getDiffBetweenTZ(tz1, tz2):
    # разница между часовыми зонами
    d = datetime.datetime.now()
    dd = [d.year, d.month, d.day, d.hour, d.minute, d.second]
    dt1 = datetime.datetime(*dd, tzinfo=pytz.timezone(tz1))
    dt2 = datetime.datetime(*dd, tzinfo=pytz.timezone(tz2))
    diff = round((dt1 - dt2).total_seconds() / 3600, 1)
    # return diff if diff >= 0 else diff * (-1)
    return diff



def getOffsetByUTC(tz):
    # смещение относительно UTC в часах
    return getDiffBetweenTZ("UTC", tz)



days_in_months = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}



def getDayYear(y, m, d):
    # получение количество деней с начала года текущей даты
    days = 1 if isLeapYear(y) and m > 2 else 0
    days += d
    for i in range(1, m):
        days += days_in_months[i]
    return days



def getISO(y, m, d, H, M, S, tz): 
    #всегда возвращает время в UTC
    if tz != 'UTC':
        y, m, d, H, M, S = toTimeZone(ftz = tz, tz='UTC', tdt = (y, m, d, H, M, S))
    return template(r"yyyy-MM-ddThh:mm:ss")



def getUnixEpoch(y, m, d, H, M, S, tz):
    # получение даты преобразованной в секунды прошедших с 1970
    # написана кастомная функция, чтобы UnixEpoch могла быть отрицательной
    # т.е. чтобы могла отображать время в секундах до 1970
    if tz != 'UTC':
        y, m, d, H, M, S = toTimeZone(ftz = tz, tz='UTC', tdt = (y, m, d, H, M, S))

    count_days = d + 0

    if y >= 1970:
        count_days += getDayYear(y, m, d) - 1
        # прибавляется часть прошедшего года
        for year in range(1970, y):
            count_days += 366 if isLeapYear(year) else 365

    elif y < 1970:
        for year in range(1970, y, -1):
            count_days -= 366 if isLeapYear(year) else 365

    return (count_days * 86400) + (H * 3600) + (M * 60) + S



def getDecade(d):
    # получение декаду месяца в которую входит текущая дата
    if d < 11: 
        return 1
    elif d < 21:
        return 2
    else: 
        return 3



def getDecadeByYear(m, d):
    # получение декады с начала года для текущей даты
    decs = {3:0,2:1,1:2}
    return m * 3 - decs[getDecade(d)]



def getWeekday(y, m, d):
    # получить день недели для текущей даты
    month = m + 10 if m < 3 else m - 2
    year = y - 1 if m < 3 else y
    result = (d + 31 * month // 12 + year + year // 4 - year // 100 + year // 400) % 7
    return 7 if result == 0 else result



def getWeekYear(y, m, d): 
    # получить неделю с начала года, начиная с первого понедельника
    days_number = getDayYear(y, m, d) - getWeekday(y, m, d)
    week_number = 0
    while days_number > 0:
        days_number -= 7
        week_number += 1
    return week_number



def getLastDayMonth(y, m):
    if m in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif m in [4, 6, 9, 11]:
        return 30
    elif m == 2:
        return 29 if isLeapYear(y) else 28



def getCentury(y):
    # возвращает век арабскими цифрами
    return ( y // 100 ) + 1 if y > 0 else y // 100 * (-1)
