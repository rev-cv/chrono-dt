import sys
import datetime
import re
from ch_validators import *
from ch_extractors import *
from ch_pitchers import *
from ch_mutators import shift, shiftTextCommand


def setDate(y = 1970, m = 1, d = 1):
    isDate(y, m, d, isGenerateError=True)
    return y, m, d

def setTime(H = 0, M = 0, S = 0):
    isTime(H, M, S, isGenerateError=True)
    return H, M, S

def setDateTime(y = 1970, m = 1, d = 1, H = 0, M = 0, S = 0):
    isDate(y, m, d, isGenerateError=True)
    isTime(H, M, S, isGenerateError=True)
    return (y, m, d, H, M, S)

def setTimeFromStr(string):
    t = timeExtractByLogic(string)
    if t is not False:
        return (t['hour'], t['min'], t['second'])
    raise Exception("ch_catchers.setTimeFromStr(): failed to extract time from string")

def setDateTimeFromStr(string):
    # извлекает из строки дату и время из строки.
    # строка имеет структуру yyyyMMddhhmmss и количество пропусков не имеет значения
    result = dtExtractByLogic(string)
    if type(result) is list:
        return result
    raise Exception("ch_catchers.setDateTimeFromStr(): failed to extract date from string") 

def setUnixEpoch(unixepoch):
    dt = datetime.datetime.fromtimestamp(unixepoch)
    return (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

def setISO(iso):
    result = dtExtractByLogic(iso)
    if type(result) is list:
        return result
    raise Exception("ch_catchers.setISO(): failed to extract date from string") 

def setByReGex(regex, string):
    # вставка по regex выражению
    result = dtExtractByRegex(regex, string)
    if type(result) is list:
        return result
    raise Exception("ch_catchers.setByReGex(): failed to extract date from string")

def setByTemplate(template, string):
    # вставка по шаблону типа yyyy-MM-dd hh:mm:ss
    result = dtExtractByTemplate(template, string)
    if type(result) is list:
        return result
    raise Exception("ch_catchers.setByTemplate(): failed to extract date from string")

def setQDate(qd):
    if 'QDate' not in sys.modules:
        from PyQt5.QtCore import QDateTime
    return [qd.year(), qd.day(), qd.day()]

def setQTime(qt):
    if 'QTime' not in sys.modules:
        from PyQt5.QtCore import QTime
    return [qt.hour(), qt.minute(), qt.second()]

def setQDateTime(qdt):
    if 'QDateTime' not in sys.modules:
        from PyQt5.QtCore import QDateTime
    return [
        *setQDate(qdt.date()), 
        *setQTime(qdt.time())
    ]

def setTimeZone(tz):
    # задает TimeZone без изменения состояния времения
    # в отличии от .toTimeZone()
    if tz.lower() == "local":
        return getLocalTimeZone()
    elif tz.lower() == "utc":
        return "UTC"
    elif tz in all_timezones:
        return tz
    else:
        raise Exception("<chrono.setTimeZone()>:  time zone unknown!")
    
regex_time = re.compile(r"^\d{1,2}:\d{1,2}|^\d{1,4}")

def setTimeShift(string, y = 1970, m = 1, d = 1, H = 0, M = 0, S = 0):
    # Time + Shift
    # получает строку в которой может быть передано одновременно и время и смещение 
    # пример: 
    # "00:25 +45" → 01:10
    # "025 + 45"  → 01:10
    # a.setTS("2 +3d -25") → задает 02:00 прибавляет 3 дня и вычетает 25 минут

    string = string.strip()
    # ↑ строка должна начинаться с чисел времени, т.е. с указания на время

    # time = findall(r"^\d{1,2}:\d{1,2}|^\d{1,4}", string)
    # if len(time) > 0:
    #     t = timeExtractByLogic(time[0])
    #     if t is not False:
    #         H, M, S = t['hour'], t['min'], t['second']
    #         string = sub(r"(^\d{1,2}:\d{1,2}|^\d{1,4})", r"", string)
    #         return shiftTextCommand(string, (y, m, d, H, M, S))
    #     else:
    #         raise Exception("ch_catchers.setTimeFromStr(): failed to extract time from string")
    
    # return y, m, d, H, M, S

    if not string.startswith("+") or not string.startswith("-"):
        time = regex_time.findall(string)
        if 0 < len(time):
            t = timeExtractByLogic(time[0])

            if t is not False:
                H, M, S = t['hour'], t['min'], t['second']
                string = regex_time.sub("", string)
            else:
                raise Exception("ch_catchers.setTimeFromStr(): failed to extract time from string")
    
    return shiftTextCommand(string, (y, m, d, H, M, S))