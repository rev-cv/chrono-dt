from re import sub

t_weekdays = {
    1: ['Понедельник', 'Пн', 'Пнд', 'Monday', 'Mo', 'Mon'],
    2: ['Вторник', 'Вт', 'Втр', 'Tuesday', 'Tu', 'Tue'],
    3: ['Среда', 'Ср', 'Сре', 'Wednesday', 'We', 'Wed'],
    4: ['Четверг', 'Чт', 'Чтв', 'Thursday', 'Th', 'Thu'],
    5: ['Пятница', 'Пт', 'Птн', 'Friday', 'Fr', 'Fri'],
    6: ['Суббота', 'Сб', 'Суб', 'Saturday', 'Sa', 'Sat'],
    7: ['Воскресенье', 'Вс', 'Вск', 'Sunday', 'Su', 'Sun'],
}

t_month_rus = ['', 
    'Январь', 'Февраль', 'Март', 
    'Апрель', 'Май', 'Июнь', 
    'Июль', 'Август', 'Сентябрь', 
    'Октябрь', 'Ноябрь', 'Декабрь'
]

t_month_rus_abb = ['', 
    'Янв', 'Фев', 'Мар', 
    'Апр', 'Май', 'Июн', 
    'Июл', 'Авг', 'Сен', 
    'Окт', 'Ноя', 'Дек'
]

t_month_eng = ['', 
    'January', 'February', 'March', 
    'April', 'May', 'June', 
    'July', 'August', 'September', 
    'October', 'November', 'December'
]

t_month_eng_abb = ['', 
    'Jan', 'Feb', 'Mar', 
    'Apr', 'May', 'Jun', 
    'Jul', 'Aug', 'Sep', 
    'Oct', 'Nov', 'Dec'
]

def getDecade(d):
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

days_in_months = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

def getDayYear(y, m, d):
    # получение количество деней с начала года текущей даты
    days = 1 if isLeapYear(y) and m > 2 else 0
    days += d
    for i in range(1, m):
        days += days_in_months[i]
    return days

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
    

def template(temp = r"yyyy-MM-dd hh:mm:ss", y = 1970, m = 1, d = 1, H = 0, M = 0, S = 0, tz = None):
    '''
    Метод предназначен только для шаблонов!

    yyyy - полный год
    yy   - год без века
    
    MM   - месяц с нулем
    MMMM - месяц текстом на английском (полный)
    MMM  - месяц текстом на английском (сокращенно)

    dd   - день с нулем
    ddd  - день недели текстом (сокращенно)
    dddd - день недели текстом (полный)

    hh - часы с нулем

    mm - минуты с нулем

    ss - секунды с нулем

    tz - временная зона
    ap - AM/PM
    '''

    regex = r'yyyy' # полный год
    if regex in temp:
        temp = sub(regex, f'{y}', temp)

    regex = r'yy'#год без века
    if regex in temp:
        temp = sub(regex, ( y // 100 ) + 1 if y > 0 else y // 100 * (-1), temp)

    regex = r'MMMM'	#полное название месяца на английском языке
    if regex in temp:
        temp = sub(regex, t_month_eng[m], temp)

    regex = r'MMM'	#сокращенное название месяца на английском языке
    if regex in temp:
        temp = sub(regex, t_month_eng_abb[m], temp)

    regex = r'MM' # месяц с нулем
    if regex in temp:
        temp = sub(regex, f'{m:0>2}', temp)


    regex = r'dddd' # надпись дня недели на английском языке
    if regex in temp:
        temp = sub(regex, f'{t_weekdays[getWeekday(y, m, d)][3]}', temp)

    regex = r'ddd' # сокращеная надпись дня недели до трех символов на английском языке
    if regex in temp:
        temp = sub(regex, t_weekdays[getWeekday(y, m, d)][5], temp)

    regex = r'dd' # день с нулем
    if regex in temp:
        temp = sub(regex, f'{d:0>2}', temp)


    regex = r'hh'	#час с нулем
    if regex in temp:
        temp = sub(regex, f'{H:0>2}', temp)

    regex = r'mm'	#минуты с нулем
    if regex in temp:
        temp = sub(regex, f'{M:0>2}', temp)

    regex = r'ap'	#время в 12 часовом вормате
    if regex in temp:
        ap = "PM" if H > 12 else "AM"
        temp = sub( regex, ap, temp)

    regex = r'ss'	#секунды с нулем
    if regex in temp:
        temp = sub(regex, f'{S:0>2}', temp)
    
    regex = r'tz'	#временная зона
    if regex in temp:
        temp = sub(regex, f'{tz}', temp)

    return temp





def format(temp = r"%a %b %d %H0:%M0:%S0 %Y %Z", y = 1970, m = 1, d = 1, H = 0, M = 0, S = 0, tz = None):
    regex = r'%HMS0' 
    if regex in temp:
        text_str = format(r'%H0:%M0:%S0')
        temp = sub(regex, text_str, temp)

    regex = r'%HMS'
    if regex in temp:
        text_str = format(r'%H:%M:%S')
        temp = sub(regex, text_str, temp)

    regex = r'%YMD0'
    if regex in temp:
        text_str = format(r'%Y-%m0-%d0')
        temp = sub(regex, text_str, temp)

    regex = r'%YMD_'
    if regex in temp:
        text_str = format(r'%Y_%m0.%d0.')
        temp = sub(regex, text_str, temp)

    regex = r'%YMD'
    if regex in temp:
        text_str = format(r'%Y-%m-%d')
        temp = sub(regex, text_str, temp)

    regex = r'%x'
    if regex in temp:
        text_str = format(r'%Y-%m0-%d0')
        temp = sub(regex, text_str, temp)

    regex = r'%X'
    if regex in temp:
        text_str = format(r'%H0:%M0:%S0')
        temp = sub(regex, text_str, temp)

    regex = r'%DEC'	#декада месяца
    if regex in temp:
        dec = getDecade(d)
        temp = sub(regex, f'{dec}', temp)

    regex = r'%DY'	#декада месяца, но отчет с начала года
    if regex in temp:
        dec = getDecadeByYear(m, d)
        temp = sub(regex, f'{dec}', temp)

    regex = r'%QUA'	#квартал года
    if regex in temp:
        qua = 'Ⅳ'
        if m < 4: qua = 'Ⅰ'
        elif m < 7: qua = "Ⅱ"
        elif m < 10: qua = "Ⅲ"
        temp = sub(regex, qua, temp)

    regex = r'%Y'	#полный год
    if regex in temp:
        temp = sub(regex, f'{y}', temp)

    regex = r'%y'#год без века
    if regex in temp:
        temp = sub(regex, str(y)[-2:], temp)

    regex = r'%m0'	#номер месяца с нулем, если месяц январь-сентябрь
    if regex in temp:
        temp = sub(regex, f'{m:0>2}', temp)

    regex = r'%mE'	#полное название месяца на английском языке
    if regex in temp:
        temp = sub(regex, t_month_eng[m], temp)

    regex = r'%mR'	#полное название месяца на русском языке языке
    if regex in temp:
        temp = sub(regex, t_month_rus[m], temp)

    regex = r'%mAE'	#сокращенное название месяца на английском языке
    if regex in temp:
        temp = sub(regex, t_month_eng_abb[m], temp)

    regex = r'%mAR'	#сокращенное название месяца на русском языке
    if regex in temp:
        temp = sub(regex, t_month_rus_abb[m], temp)

    regex = r'%m'	#номер месяца без нуля, если месяц январь-сентябрь
    if regex in temp:
        temp = sub(regex, str(m), temp)

    regex = r'%B'	#полное название месяца на английском языке
    if regex in temp:
        temp = sub(regex, t_month_eng[m], temp)

    regex = r'%b'	#сокращенное название месяца на английском языке
    if regex in temp:
        temp = sub(regex, t_month_eng_abb[m], temp)

    regex = r'%d0'	#день месяца с нулем (05) в датах между 01-09
    if regex in temp:
        temp = sub(regex, f'{d:0>2}', temp)

    regex = r'%d'	#день месяца без нуля (5) в датах между 1-9
    if regex in temp:
        temp = sub(regex, str(d), temp)

    regex = r'%H0'	#час с нулем
    if regex in temp:
        temp = sub(regex, f'{H:0>2}', temp)

    regex = r'%H'	#час
    if regex in temp:
        temp = sub(regex, str(H), temp)

    regex = r'%M0'	#минуты с нулем
    if regex in temp:
        temp = sub(regex, f'{M:0>2}', temp)

    regex = r'%M'	#минуты
    if regex in temp:
        temp = sub(regex, str(M), temp)

    regex = r'%AMPM'	#время в 12 часовом вормате
    if regex in temp:
        temp = sub(
            regex, 
            f'{H-12}:{m}PM' if H > 12 else f'{H}:{m}AM', 
            temp
        )

    regex = r'%S0'	#секунды с нулем
    if regex in temp:
        temp = sub(regex, f'{S:0>2}', temp)

    regex = r'%S'	#секунды
    if regex in temp:
        temp = sub(regex, str(S), temp)

    regex = r'%Z'	#временная зона
    if regex in temp:
        temp = sub(regex, f'{tz}', temp)

    regex = r'%wAE3'	#сокращеная надпись дня недели до трех символов на английском языке
    if regex in temp:
        temp = sub(regex, t_weekdays[getWeekday(y, m, d)][5], temp)

    regex = r'%wAR3'	#сокращеная надпись дня недели до трех символов на русском языке
    if regex in temp:
        temp = sub(regex, t_weekdays[getWeekday(y, m, d)][2], temp)

    regex = r'%wAR'	#сокращеная надпись дня недели до 2 символов на русском языке
    if regex in temp:
        temp = sub(regex, t_weekdays[getWeekday(y, m, d)][1], temp)

    regex = r'%wAE'	#сокращеная надпись дня недели до 2 символов на русском языке
    if regex in temp:
        temp = sub(regex, t_weekdays[getWeekday(y, m, d)][4], temp)

    regex = r'%wR'	#сокращеная надпись дня недели на русском языке
    if regex in temp:
        temp = sub(regex, t_weekdays[getWeekday(y, m, d)][0], temp)

    regex = r'%wE'	#сокращеная надпись дня недели на английском языке
    if regex in temp:
        temp = sub(regex, t_weekdays[getWeekday(y, m, d)][3], temp)

    regex = r'%w'	#день недели
    if regex in temp:
        temp = sub(regex, f'{getWeekday(y, m, d)}', temp)

    regex = r'%c'	#век арабскими цифрами
    if regex in temp:
        temp = sub(regex, f'{( y // 100 ) + 1 if y > 0 else y // 100 * (-1)}', temp)

    regex = r'%a'	#сокращеная надпись дня недели до трех символов на английском языке
    if regex in temp:
        temp = sub(regex, f'{t_weekdays[getWeekday(y, m, d)][5]}', temp)

    regex = r'%A'	#надпись дня недели на английском языке
    if regex in temp:
        temp = sub(regex, f'{t_weekdays[getWeekday(y, m, d)][3]}', temp)

    regex = r'%W'	#кол-во недель с начала года (считается с первого понедельника)
    if regex in temp:
        days_number = getDayYear(y, m, d) - getWeekday(y, m, d)
        week_number = 0
        while days_number > 0:
            days_number -= 7
            week_number += 1
        temp = sub(regex, str(week_number), temp)

    regex = r'%j'	#кол-во дней с начала года
    if regex in temp:
        temp = sub(regex, str(getDayYear(y, m, d)), temp)

    regex = r'%I'	#часы в 12часовом формате
    if regex in temp:
        temp = sub(
            regex, 
            f'{H-12}:{m}' if H > 12 else f'{H}:{m}', 
            temp
        )

    return temp