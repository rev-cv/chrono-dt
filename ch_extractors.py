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



def validatorForDateExtractByLogic(func):
    def wrapper(arg):
        result = func(arg)
        if type(result) is list:
            if isDate(*result):
                return result
        return None
    return wrapper



@validatorForDateExtractByLogic
def dateExtractByLogic(string):
    # попытка угодать дату

    datetime = [0, 1, 1]

    str_digits = findall(r'\d+', string)
    count_digits = len(str_digits)



    def oneLineExtract(digit, string):
        len_0 = len(string)

            
        if len_0 == 1:
            # 7 → 2007-01-01

            datetime[0] = digit + 2000
            return datetime


        elif len_0 == 2:
            # 22 → 2022-01-01
            # 92 → 1992-01-01

            if 00 <= digit < 50:
                datetime[0] = digit + 2000
            elif 50 <= digit < 100:
                datetime[0] = digit + 1900
            return datetime
        

        elif len_0 == 3:
            # 5 1 2 → 2005-12-01
            # 5 3 5 → 2005-03-05
            # 2 2 5 → 2022-05-01

            t1 = int(string[0])
            t1_2 = int(string[:2])
            t2_3 = int(string[1:])

            if 2 < t1:
                datetime[0] = t1 + 2000
                if 1 <= t2_3 <= 12:
                    datetime[1] = t2_3
                else:
                    datetime[1] = int(string[1])
                    datetime[2] = int(string[2])
                return datetime
            elif 0 <= t1_2 < 50:
                # вероятно это сокращенный год 21 века + месяц до октября
                datetime[0] = t1_2 + 2000
                datetime[1] = int(string[2])
                return datetime
            return None


        elif len_0 == 4:
            # 19 52 → 1952-01-01
            # 20 45 → 2045-01-01
            # 23 10 → 2023-10-01
            # 23 15 → 2023-01-05

            t1_2 = int(string[:2])
            t3_4 = int(string[2:])

            if t1_2 == 19 or t1_2 == 20:
                datetime[0] = digit
            elif 0 <= t1_2 < 50 and 1 <= t3_4 <= 12:
                datetime[0] = t1_2 + 2000
                datetime[1] = t3_4
            elif 0 <= t1_2 < 50 and 12 < t3_4:
                datetime[0] = t1_2 + 2000
                datetime[1] = int(string[2])
                datetime[2] = int(string[3])
            return datetime


        elif len_0 == 5:
            # 9 10 25 → 2009-10-25
            # 91 5 12 → 1991-05-12
            # 05 12 6 → 2005-12-06
            # 2022 5  → 2022-05-01

            t1 = int(string[0])
            t1_4 = int(string[:4])


            if 2 < t1:
                datetime[0] = t1 + 2000
                t2_3 = int(string[1:3])
                t4_5 = int(string[3:])

                if 1 <= t2_3 <= 12 and 1 <= t4_5 <= 31:
                    datetime[1] = t2_3
                    datetime[2] = t4_5
                    return datetime
                else:
                    t1_2 = int(string[:2])
                    t3_4 = int(string[2:4])
                    t4_5 = int(string[4:])

                    if t1_2 < 50:
                        datetime[0] = t1_2 + 2000
                    else:
                        datetime[0] = t1_2 + 1900

                    if 1 <= t3_4 <= 12:
                        datetime[1] = t3_4
                        datetime[2] = int(string[4])
                    elif 1 <= t4_5 <= 31:
                        datetime[1] = int(string[2])
                        datetime[2] = t4_5
                    else:
                        return None
                    
                    return datetime
            

            elif t1 <= 2:
                datetime[0] = int(string[:2]) + 2000
                t3_4 = int(string[2:4])
                t4_5 = int(string[3:])

                if 1 <= t3_4 <= 12:
                    datetime[1] = t3_4
                    datetime[2] = int(string[4])
                    return datetime
                elif 1 <= t4_5 <= 31:
                    datetime[1] = int(string[2])
                    datetime[2] = int(string[3:])
                    return datetime


            if 1950 < t1_4 < 2100:
                datetime[0] = t1_4
                datetime[1] = int(string[4])
                return datetime
            else:
                return None


        elif len_0 == 6:
            # 2022 12
            # 2022 3 2
            # 20 12 15

            t1_4 = int(string[:4])
            t3_4 = int(string[2:4])
            t5_6 = int(string[4:])

            if 1980 <= t1_4 <= 2050:
                datetime[0] = t1_4

                if 1 <= t5_6 <= 12:
                    datetime[1] = t5_6
                else:
                    datetime[1] = int(string[4])
                    datetime[2] = int(string[5])
            
            elif 1 <= t3_4 <= 12 and 1 <= t5_6 <= 31:
                datetime[1] = t3_4
                datetime[2] = t5_6

                t1_2 = int(string[:2])

                datetime[0] = t1_2 + 2000 if t1_2 < 50 else t1_2 + 1900
            else:
                datetime[0] = t1_4

                if 1 <= t5_6 <= 12:
                    datetime[1] = t5_6
                else:
                    datetime[1] = int(string[4])
                    datetime[2] = int(string[5])

            return datetime


        elif len_0 == 7:
            # 2022 05 4
            # 2022 5 04

            t5_6 = int(string[4:6])
            t6_7 = int(string[5:])

            print(t5_6, t6_7)

            if 1 <= t5_6 <= 12:
                return [int(string[:4]), t5_6, int(string[6])]
            elif 1 <= t6_7 <= 31:
                return [int(string[:4]), int(string[5]), t6_7]
            return None


        elif len_0 == 8:
            year = int(string[:4])
            month = int(string[4:6])
            day = int(string[6:])

            if 1 <= month <= 12 and 1 <= day <= 31:
                return [year, month, day]
            return None



    if count_digits != 0:
        digits = [int(x) for x in str_digits]

        # чем является первое число из 3 возможных?
        

        if count_digits == 1:
            return oneLineExtract(digits[0], str_digits[0])
        else:
            # если несколько строк с цифрами, значит первое число указывает на год
            if 890 < digits[0] < 2300:
                # вероятно это года
                datetime[0] = digits[0]
            elif 00 <= digits[0] < 50:
                # вероятно это сокращенный год 21 века
                datetime[0] = digits[0] + 2000
            elif 50 <= digits[0] < 100:
                # вероятно это сокращенный год 20 века
                datetime[0] = digits[0] + 1900
            else:
                return None
            
        if count_digits == 2 or count_digits == 3:
            len_1 = len(str_digits[1])

            if len_1 == 1:
                datetime[1] = digits[1]
            elif len_1 == 2:
                if 1 <= digits[1] <= 12:
                    datetime[1] = digits[1]
                else:
                    datetime[1] = int(str_digits[1][0])
                    datetime[2] = int(str_digits[1][1])
                    return datetime
            elif len_1 == 3:
                t1_2 = int(str_digits[1][:2])
                t2_3 = int(str_digits[1][1:])

                if 1 <= t1_2 <= 12:
                    datetime[1] = t1_2
                    datetime[2] = int(str_digits[1][2])
                    return datetime
                elif 1 <= t2_3 <= 31:
                    datetime[1] = int(str_digits[1][0])
                    datetime[2] = t2_3
                    return datetime
                return None
            elif len_1 == 4:
                t1_2 = int(str_digits[1][:2])
                t3_4 = int(str_digits[1][2:])

                if 1 <= t1_2 <= 12 and 1 <= t3_4 <= 31:
                    datetime[1] = t1_2
                    datetime[2] = t3_4
                    return datetime
                return None


        if count_digits == 3:
            if 1 <= digits[2] <= 31:
                datetime[2] = digits[2]
                return datetime
            return None
        
        return datetime





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



if __name__ == "__main__":
    a = dateExtractByLogic("23716")
    print(a)