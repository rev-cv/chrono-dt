import pytz



countDays = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
all_timezones = list(pytz.all_timezones)



def isDate(y, m, d, isGenerateError=False):
    # является ли переданные значения датой?
    # проверка кол-ва месяцев и кол-ва дней в месяце
    if 12 < m < 1:
        if isGenerateError is False: 
            return False
        else:
            raise Exception("<chrono._isDate()>: the month is indicated by numbers from 1 to 12")

    return isCountDaysInMonth(y, m, d, isGenerateError)



def isTime(H, M, S, isGenerateError=False):
    # является переданные значения временем?
    if 0 <= H < 24:
        if 0 <= M < 60:
            if 0 <= S < 60:
                return True
            elif isGenerateError is True:
                raise Exception("ch_analyzer.isTime(): the seconds are incorrect.")
        elif isGenerateError is True:
            raise Exception("ch_analyzer.isTime(): the minutes are incorrect.")
    elif isGenerateError is True:
        raise Exception("ch_analyzer.isTime(): the hours are incorrect.")

    return False



def isCountDaysInMonth(y, m, d, isGenerateError=False):
    # верно ли количество дней (d) для указанного месяца (m) ↲
    # с учетом високосного и не високосного года

    if d <= 0:
        if isGenerateError is False: 
            return False
        else:
            raise Exception("ch_analyzer.isCountDaysInMonth(): day cannot be number <= 0")

    if m in [1, 3, 5, 7, 8, 10, 12] and d <=31: 
        return True
    elif m in [4, 6, 9, 11] and d < 31: 
        return True
    elif m == 2 and d < 29: 
        return True
    elif m == 2 and isLeapYear(y) is True and d <= 29: 
        return True
    else:
        if isGenerateError is False: 
            return False
        else:
            raise Exception("ch_analyzer.isCountDaysInMonth(): the specified day does not exist in the specified month.")



def isLeapYear(year):
    # является ли год високосным?
    if year % 4 == 0:
        if year % 100 != 0: 
            return True
        else:
            if year % 400 == 0: 
                return True
            else: 
                return False
    else: return False



def isDayBegun(H, M, S):
    # начался ли день? пока время равно 00:00:00 день считается не начавшимся
    
    # Эта проверка необходима для периодов чтобы период типа ↲
    # 2022-03-12 00:00:00 — 2022-03-13 00:00:00 принедлежал только для дня 
    # 2022-03-12, но не для дня 2022-03-13
    if H == 0 and M == 0 and S == 0:
        return False
    return True



def isTimeZone(TimeZone):
    # проверка временной зоны на возможность использования
    return True if TimeZone in all_timezones else False



def validatorLastDayInMonth(y, m, d):
    # в отличии от isCountDaysInMonth, если проверка не пройдена возвращает последний день месяца
    if isCountDaysInMonth(y, m, d):
        return d
    else:
        if m in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif m in [4, 6, 9, 11]:
            return 30
        elif m == 2:
            return 29 if isLeapYear(y) else 28