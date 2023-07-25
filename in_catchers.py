import datetime
from math import ceil
from ch_mutators import shift
from ch_pitchers import getWeekday
from Chrono import Chrono
from re import match, findall, MULTILINE


def setInterval(start = None, finish = None, roundoff = None, expansion=True):
    # start → [1970, 1, 1, 0, 0, 0]

    result = [[1970, 1, 1, 0, 0, 0], [1970, 1, 1, 0, 0, 0]]

    if start is False:
        # предполгается, что интервал будет задан вручную
        return result

    if start is not None and finish is not None:
        # → передано начало и окончание интервала
        # → динамическое «округление» не задано (roundoff is None)

        if type(start) is not list and type(start) is not tuple:
            s = Chrono(start)
            start = [s.y, s.m, s.d, s.H, s.M, s.S]
        if type(finish) is not list and type(start) is not tuple:
            f = Chrono(finish)
            finish = [f.y, f.m, f.d, f.H, f.M, f.S]

        result[0] = setStart(start, expansion, roundoff)
        result[1] = setFinish(finish, expansion, roundoff)
    else:
        roundoff = "day" if roundoff is None else roundoff
        # ↑ если для интервала не передано start и finish, то ↲
        # дальнейшее создание интервала не имеет смысла ↲
        # без заданных roundoff и expansion
            
        if start is not None and finish is None:
            result[0] = setStart(start, expansion, roundoff)
            result[1] = setFinish(start, expansion, roundoff)

        elif start is None and finish is not None:
            result[0] = setStart(finish, expansion, roundoff)
            result[1] = setFinish(finish, expansion, roundoff)
            
        else:
            now = datetime.datetime.now()
            tuplenow = [now.year, now.month, now.day, now.hour, now.minute, now.second]
            result[0] = setStart(tuplenow, expansion, roundoff)
            result[1] = setFinish(tuplenow, expansion, roundoff)
    
    if None in result[0] or None in result[1]:
        raise Exception(f"{__name__}.{setInterval.__name__}(): The interval has not been defined.")
    
    if datetime.datetime(*result[0]) < datetime.datetime(*result[1]):
        return result
    
    raise Exception(f"{__name__}.{setInterval.__name__}(): The resulting interval is subject to collapse.")



def setStart(start, expansion, roundoff):
    # start = [1970, 1, 1, 0, 0, 0]
    if roundoff is not None:
        if expansion is True:
            return decrease(start, roundoff)
        elif expansion is False:
            return increase(start, roundoff)
    return start



def setFinish(finish, expansion, roundoff):
    # finish = [1970, 1, 1, 0, 0, 0]
    if roundoff is not None:
        if expansion is True:
            return increase(finish, roundoff)
        elif expansion is False:
            return decrease(finish, roundoff)
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
    elif 'dece' == ro[:4]: # decennary
        H, M, S = 0, 0, 0,
        d, m = 1, 1
        y = int(str(y)[:-1] + "0") + 10
    elif 'dec' == ro[:3]: # decade
        H, M, S = 0, 0, 0
        if d <= 10:
            d = 11
        elif d <= 20:
            d = 21
        else:
            y, m, d, H, M, S = shift(month=1, tdt=(y, m, 1, H, M, S))
    elif 'qua' == ro[:3]: # quarter
        H, M, S, d = 0, 0, 0, 1
        if m <= 3:
            m = 4
        elif m <= 6:
            m = 7
        elif m <= 9:
            m = 10
        else:
            y, m = y + 1, 1
    elif "min" == ro[:3]: # minute
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
    elif 'dece' == ro[:4]: # decennary
        H, M, S = 0, 0, 0,
        d, m = 1, 1
        y = int(str(y)[:-1] + "0")
    elif 'dec' == ro[:3]: # decade
        H, M, S = 0, 0, 0
        if d <= 10:
            d = 1
        elif d <= 20:
            d = 11
        else:
            d = 21
    elif 'qua' == ro[:3]: # quarter
        H, M, S, d = 0, 0, 0, 1
        if m < 4:
            m = 1
        elif m < 7:
            m = 4
        elif m < 10:
            m = 7
        else:
            m = 10
    elif "min" == ro[:3]: # minute
        S = 0
    elif 'week' == ro:
        # смещение до прошлого понедельника
        y, m, d, H, M, S = shift(
            day = getWeekday(y, m, d) * (-1) + 1, 
            tdt=(y, m, d, 0, 0, 0)
        )
        
    return (y, m, d, H, M, S)



fos = (
    None, 
    'decennary', 'year', 'quarter', 'month', 'decade', 'week', 'day', 'hour', 'minute',
    'dece', 'qua', 'dec', 'min'
)



def setRoundOff(roundoff):
    if roundoff in fos:
        return roundoff
    raise Exception("Invalid argument passed for 'roundoff'")



def setIntervalByWeek(year, week_number, roundoff, expansion):

    if type(year) is str:
        # вместо года и номера недели пришел шаблон типа '%Y, WEEK %W'
        year, week_number = [int(x) for x in year.split(', WEEK ')]

    sd = datetime.datetime(year, 1, 1)

    # ↓ первый понедельник года
    while sd.weekday() != 0:  # 0 - понедельник
        sd += datetime.timedelta(days=1)

    # ↓ понедельник выбранной недели
    td = sd + datetime.timedelta(weeks=week_number - 1)

    return setInterval( (td.year, td.month, td.day, 0, 0, 0), None, roundoff, expansion )



def setIntervalByDecade(year, decade_number, roundoff, expansion):

    if type(year) is str:
        # вместо года и номера недели пришел шаблон типа '%Y, DEC %DY'
        year, decade_number = [int(x) for x in year.split(', DEC ')]

    if not 1 <= decade_number <= 36:
        raise ValueError("Недопустимый номер декады. Декада должна быть в диапазоне от 1 до 36.")

    month = (decade_number - 1) // 3 + 1
    day = (decade_number - 1) % 3 * 10 + 1

    return setInterval( (year, month, day, 0, 0, 0), None, roundoff, expansion )


def setIntervalByName(name:str):
    # на основании анализа имени генерит интервал

    # 2023, 12 Jun          12 июня 2023 года
    # 2023, DEC 15          15 декада 2023 года
    # 2023, WEEK 12         12 неделя 2023 года 
    # 2023, Jun             июнь 2023 года
    # 2023, QUA Ⅱ           2 квартал 2023 года (апрель—июнь)
    # 2023                  2023 год
    # 2020's                20е годы (20—30)


    day = match(r'\d{4}, \d{2} [A-Z][a-z]{2}', name)
    if day is not None:
        date = Chrono(False).setByTemplate('yyyy, dd MMM', name)
        return setInterval(
            (date.y, date.m, date.d, date.H, date.M, date.S),
            roundoff="day"
        )
    

    week = findall(r'(\d{4}), WEEK (\d{1,2})', name)
    if 0 < len(week):
        return setIntervalByWeek(int(week[0][0]), int(week[0][1]), 'week', True)
    

    dec = findall(r'(\d{4}), DEC (\d{1,2})', name)
    if 0 < len(week):
        return setIntervalByDecade(int(dec[0][0]), int(dec[0][1]), 'decade', True)
    

    month = match(r'\d{4}, [A-Z][a-z]{2}', name)
    if month is not None:
        date = Chrono(False).setByTemplate('yyyy, MMM', name)
        return setInterval(
            (date.y, date.m, date.d, date.H, date.M, date.S),
            roundoff="month"
        )
    

    dece = findall(r"(\d{4})'s", name)
    if dece is not None and name[-2:] == "'s":
        return setInterval( (int(dece[0]), 1, 1, 0, 0, 0), roundoff="dece" )
    

    qua = findall(r'(\d{4}), QUA ([ⅠⅡⅢⅣ])', name)
    if qua is not None and "QUA" in name:
        y, q = qua[0]
        if q == "Ⅰ":
            return setInterval( (int(y), 1, 1, 0, 0, 0), roundoff="quarter" )
        elif q == "Ⅱ":
            return setInterval( (int(y), 4, 1, 0, 0, 0), roundoff="quarter" )
        elif q == "Ⅲ":
            return setInterval( (int(y), 7, 1, 0, 0, 0), roundoff="quarter" )
        else:
            return setInterval( (int(y), 10, 1, 0, 0, 0), roundoff="quarter" )


    year = dece = findall(r"(\d{4})", name)
    if year is not None:
        return setInterval( (int(year[0]), 1, 1, 0, 0, 0), roundoff="year" )


if __name__ == "__main__":
    # print(
    #     setIntervalByName("2023, DEC 21")
    # )

    print(
        increase((2023, 7, 20, 45, 35, 0), "decade")
    )
    