from re import findall, match

from ch_validators import isDate, isTime, isCountDaysInMonth

monthNames = {
    'jan': 1, 'january':  1, 'янв': 1, 'январь': 1, 'января': 1,
    'feb': 2, 'february': 2, 'фев': 2, 'февраль': 2, 'февраля': 2,
    'mar': 3, 'march': 3, 'мар': 3, 'март': 3, 'марта': 3, 
    'apr': 4, 'april': 4, 'апр': 3, 'апрель': 4, 'апреля': 4,
    'may': 5, 'may': 5, 'май': 5, 'мая': 5,
    'jun': 6, 'june': 6, 'июн': 6, 'июнь': 6, 'июня': 6,
    'jul': 7, 'july': 7, 'июл': 7, 'июль': 7, 'июля': 7,
    'aug': 8, 'august': 8, 'авг': 8, 'август': 8, 'августа': 8,
    'sep': 9, 'september': 9, 'сен': 9, 'сентябрь': 9, 'сентября': 9,
    'oct': 10, 'october': 10, 'окт': 10, 'октябрь': 10, 'октября': 10,
    'nov': 11, 'november': 11, 'нов': 11, 'ноябрь': 11, 'ноября': 11,
    'dec': 12, 'december': 12, 'дек': 12, 'декабрь': 12, 'декабря': 12,
}



def dtExtractByRegex(regex, string):
    # в шаблоне должны быть именованные группы
    # примеры смотреть в dtExtractByTemplate
    # year
    # month
    # day
    # hour
    # minute
    # second
    # month_text - любое текстовое обозначение месяца предусмотренное в monthNames

    year = None
    month = None
    day = None
    hour = 0
    minute = 0
    second = 0

    r = match(regex, string)
    if r is not None:
        recd = r.groupdict()
        received_keys = recd.keys()

        if "year" in received_keys:
            year = int(recd['year'])
        
        if "month" in received_keys:
            month = int(recd['month'])
        elif "month_text" in received_keys:
            month = monthNames.get(recd['month_text'].lower())

        if "day" in received_keys:
            day = int(recd['day'])

        if isDate(year, month, day) is False:
            return None

        hour = int(recd.get('hour', 0))
        minute = int(recd.get('minute', 0))
        second = int(recd.get('second', 0))

        if isTime(hour, minute, second) is False:
            return None

        return [year, month, day, hour, minute, second]
    
    return None



def dtExtractByTemplate(template, string):
    # пределывает переданный шаблон в regex-выражение шаблоны типа "yyyy, dd MMM hh:mm"
    # передает дальнейшее выполнение в dtExtractByRegex
    templates = [
        ["yyyy", r"(?P<year>-\d{1,4}|\d{1,4})"],
        ["dd", r"(?P<day>\d{1,2})"],
        ["hh", r"(?P<hour>\d{1,2})"],
        ["mm", r"(?P<minute>\d{1,2})"],
        ["ss", r"(?P<second>\d{1,2})"],
        ["MMMM", r"(?P<month_text>[a-zA-Z]{3,9})"],
        ["MMM", r"(?P<month_text>[a-zA-Z]{3})"],
        ["MM", r"(?P<month>\d{1,2})"],
    ]

    for x in templates:
        if x[0] in template:
            template = template.replace(x[0], x[1])

    return dtExtractByRegex(template, string)



def dtExtractByLogic(string):
    # Модуль производит разбор строки в которую предположительно записана дата
    # в последовательности <год месяц день часы минуты секунды>
    # Подобный алгоритм хорош тем, что он не зависит от разделителей
    # и может разбирать такие даты
    # 2019 11 11 20 00 00
    # 20191111200000

    d = findall(r'\d+', string)
    ymdhms = False

    CE = 1
    try:
        if string[0] == '-':
            string = string.replace('-', ' ').strip()
            CE = -1
    except IndexError: pass
    # ↑ определяет BC и AD
    # если в начале строки стоит знак минус
    # до значит дата "до нашей эры"

    
    if type(d) == list and len(d) != 0:
        d = [int(x) for x in d]
        ld, ld0 = len(d), len(str(d[0]))
        if ld == 1 and ld0 <= 4: #скорее всего год
            ymdhms = {'y':int(d[0]),'mo':1,'d':1,'h':0,'m':0,'s':0}
        elif ld == 1 and (ld0 == 5 or ld0 == 6):
            #скорее всего год с месяцем, либо год, месяц, дата
            month, year = int(str(d[0])[4:]), int(str(d[0])[:4])
            if month <= 12 and month > 0: 
                ymdhms = {'y':year,'mo':month,'d':1,'h':0,'m':0,'s':0}
            elif month == 0 and ld0 == 5:
                #видимо хотел ввести месяц в виде 01 (типа 202001), но успел ввести только 0
                ymdhms = {'y':year,'mo':1,'d':1,'h':0,'m':0,'s':0}
            else:
                month, day = int(str(month)[:1]), int(str(month)[1:])
                if month != 0 and day != 0:
                    ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
        elif ld == 1 and ld0 == 7:
            year, md = int(str(d[0])[:4]), int(str(d[0])[4:])
            if int(str(md)[:-1]) <= 12:
                month, day = int(str(md)[:-1]), int(str(md)[-1:])
                if day > 0: 
                    ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
                else: 
                    ymdhms = {'y':year,'mo':month,'d':1,'h':0,'m':0,'s':0}
            elif isDate(year, int(str(md)[:1]), int(str(md)[-2:])) is True:
                month, day = int(str(md)[:1]), int(str(md)[-2:])
                ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
            elif isCountDaysInMonth(year,int(str(md)[:1]),int(str(md)[-2:])) is True:
                month, day, hour = int(str(md)[0]), int(str(md)[1]), int(str(md)[2])
                ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':0,'s':0}
        elif ld == 1 and ld0 == 8:
            year, md = int(str(d[0])[:4]), str(d[0])[4:]
            month, day = int(md[:2]), int(md[2:])
            if isDate(year, month, day) is True:
                #1992 12 31
                ymdhms = {'y':year,'mo':month,'d':day,'h':0,'m':0,'s':0}
            elif month > 12:
                #1992 9 31 9 
                #1992 9 9 23
                #1992 9 9 9 9
                month = int(md[:1])
                day = int(md[1]+md[2])
                if isCountDaysInMonth(year, month, day) is True:
                    ymdhms = {'y':year,'mo':month,'d':day,'h':int(md[3]),'m':0,'s':0}
                else:
                    day = int(md[1])
                    hour = int(md[2]+md[3])
                    if hour <= 23:
                        ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':0,'s':0}
                    else:
                        hour, minute = int(md[2]), int(md[3])
                        ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':minute,'s':0}
            elif month <= 12:
                #1992 12 9 9
                day, hour = int(md[-2]), int(md[-1])
                ymdhms = {'y':year,'mo':month,'d':day,'h':hour,'m':0,'s':0}
        elif ld == 1 and ld0 >= 9:
            year, md = int(str(d[0])[:4]), str(d[0])[4:]
            month, day = int(md[:2]), int(md[2]+md[3])

            def function(year, month, day, balance):
                r = timeExtractByLogic(balance)
                if r is not False:
                    return {'y':year,'mo':month,'d':day,
                        'h':r['hour'],'m':r['min'],'s':r['second']}
                else: return False

            if month <= 12:
                if isCountDaysInMonth(year, month, day) is True:
                    ymdhms = function(year, month, day, md[4:])
                else:
                    day = int(md[2])
                    ymdhms = function(year, month, day, md[3:])
            elif month > 12:
                month = int(md[0])
                day = int(md[1]+md[2])
                if isCountDaysInMonth(year, month, day) is True:
                    ymdhms = function(year, month, day, md[3:])
                else:
                    day = int(md[1])
                    ymdhms = function(year, month, day, md[2:])
        elif ld >= 2 and ld <= 6 and d[1] > 0 and d[1] <= 12:
            ymdhms = {'y':int(d[0]),'mo':int(d[1]),'d':1,'h':0,'m':0,'s':0}
            if ld >= 3:
                if isCountDaysInMonth(int(d[0]),int(d[1]),int(d[2])) is True:
                    ymdhms['d'] = int(d[2])
            if ld >= 4:
                if d[3] <= 23 and d[3] >= 0: 
                    ymdhms['h'] = int(d[3])
            if ld >= 5:
                if d[4] <= 59 and d[4] >= 0:
                    ymdhms['m'] = int(d[4])
            if ld == 6:
                if d[5] <= 59 and d[5] >= 0:
                    ymdhms['s'] = int(d[5])
    
    if ymdhms is not False: 
        ymdhms['y'] = ymdhms['y'] * CE
        if ymdhms['d'] == 0: ymdhms['d'] = 1

    return [
        ymdhms['y'],
        ymdhms['mo'],
        ymdhms['d'],
        ymdhms['h'],
        ymdhms['m'],
        ymdhms['s']
    ]



def timeExtractByLogic(findings):
    t = findall(r'(\d+)', findings)
    hms = {'hour':None,'min':None,'second':0}
    if len(t) == 1:
        if int(t[0]) <= 23 and (len(t[0]) == 1 or len(t[0]) == 2):
            hms['hour'], hms['min'] = int(t[0]), 0
        elif len(t[0]) == 2:
            hms['hour'], hms['min'] = int(t[0][0]), int(t[0][1])*10
        elif len(t[0]) == 3:
            tz = [t[0][0], t[0][1], t[0][2]]
            if int(tz[0]) <= 9 and int(tz[1] + tz[2]) < 60:
                hms['hour'], hms['min'] = int(tz[0]), int(tz[1] + tz[2])
            elif (int(tz[0] + tz[1]) > 9) and (int(tz[0] + tz[1]) < 24) and (int(tz[2]) <= 5):
                hms['hour'], hms['min'] = int(tz[0] + tz[1]), int(tz[2])*10
            else:
                hms['hour'], hms['min'] = int(t[0][0]), int(t[0][1])*10
                hms['second'] = int(t[0][2])*10
        elif len(t[0]) == 4:
            tz = [int(t[0][:-2]), int(t[0][-2:])]
            if tz[0] <= 23 and tz[1] < 59:
                hms['hour'], hms['min'] = tz[0], tz[1]
        elif len(t[0]) == 5:
            #1 59 59 | 23 1 59 | 23 59 1
            hour, minute = int(t[0][:2]), int(t[0][2]+t[0][3])
            if hour < 24 and minute < 60:
                #значит одинарные секунды
                hms['hour'], hms['min'] = hour, minute
                hms['second'] = int(t[0][4])*10
            elif hour < 24:
                #значит одинарные минуты
                hms['hour'], second = hour, int(t[0][-2:])
                if second > 60: hms['second'] = 59
                else: hms['second'] = second
                minute = int(t[0][2])
                if minute*10 > 60: hms['min'] = minute
                else: hms['min'] = minute*10
            elif minute < 60:
                #значит одинарные часы
                hms['hour'] = int(t[0][0])
                minute = int(t[0][1]+t[0][2])
                if minute < 60: hms['min'] = minute
                second = int(t[0][-2:])
                if second > 60: hms['second'] = 59
                else: hms['second'] = second
        elif len(t[0]) == 6:
            hour, minute, second = int(t[0][:2]), int(t[0][2]+t[0][3]), int(t[0][-2:])
            if hour < 24 and minute < 60 and second < 60:
                hms['hour'], hms['min'], hms['second'] = hour, minute, second
    elif len(t) == 2:
        if int(t[0]) < 24 and int(t[1]) < 60:
            hms['hour'], hms['min'] = int(t[0]), int(t[1])
    elif len(t) == 3:
        if int(t[0]) < 24 and int(t[1]) < 60 and int(t[2]) < 60:
            hms['hour'], hms['min'], hms['second'] = int(t[0]), int(t[1]), int(t[2])
    if hms['hour'] is not None and hms['min'] is not None: 
        return hms
    else: return None