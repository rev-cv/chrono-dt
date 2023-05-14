import datetime

def isReal(start, finish, isExpansion = True, isGenerateError=False):
    # является ли полученный интервал start—finish реальным?
    # Например если start == finish или start > finish ↲
    # то такого периода не может существовать в реальности.

    # Функция isReal принимает объекты Chrono и datetime.datetime

    if type(start) is list or type(start) is tuple:
        start = datetime.datetime(*start)
    
    if type(finish) is list or type(finish) is tuple:
        finish = datetime.datetime(*finish)
    
    if start >= finish:
        if isGenerateError:
            error = "\nThe created interval cannot exist in reality!\n"
            # Созданный интервал не может существовать в реальности!
            error += "The start of the interval cannot:\n"
            error += "    - occur later than the finish of the interval\n"
            error += "    - coincide with the finish of the interval\n"
            # Старт интервала не может произойти позже финиша интервала.
            # Старт интервала не может совпадать с финишем интервала!
            
            if isExpansion is False:
                error += "Probably using `isExpansion=False` caused the interval to collapse.\n"
                # Вероятно использование `isExpansion=False` привело к схлопыванию интервала
            
            error += "There may be an error in the received `class Interval` data."
            # Возможна ошибка в полученных данных `class Interval`.
            raise Exception(error)
        return False
    return True

def isDateWithinInterval(date, start, finish):
    # входит ли переданная дата в данный период?

    if type(start) is list or type(start) is tuple:
        start = datetime.datetime(*start)
    
    if type(finish) is list or type(finish) is tuple:
        finish = datetime.datetime(*finish)
    
    if type(date) is list or type(date) is tuple:
        date = datetime.datetime(*date)
    
    if start <= date <= finish:
        return True
    return False

def isIntervalWithinInterval(ds, df, in_ds, in_df, isFullEntry=False):
    # входит ли переданный интервал в текущий интервал?

    # принимаемые даты могут быть Chrono или datetime.datetime

    # isFullEntry — 
    # должно ли быть полное вхождение (True) 
    # или интервал может выходить за границы (False)?

    if type(ds) is list or type(ds) is tuple:
        ds = datetime.datetime(*ds)
    
    if type(df) is list or type(df) is tuple:
        df = datetime.datetime(*df)
    
    if type(in_ds) is list or type(in_ds) is tuple:
        in_ds = datetime.datetime(*in_ds)
    
    if type(in_df) is list or type(in_df) is tuple:
        in_df = datetime.datetime(*in_df)

    if isFullEntry is False:
        if in_ds <= ds < df <= in_df:
            return True
        return False
    elif isFullEntry is True:
        if in_ds < ds < in_df or in_ds < df < in_df:
            return True
        return False
    return False

def isIntervalMore(ds1, df1, ds2, df2):
    # Длиннее ли интервал?
    if df1 - ds1 > df2 - ds2:
        return True
    return False

def isIntervalLess(ds1, df1, ds2, df2):
    # короче ли интервал?
    if df1 - ds1 < df2 - ds2:
        return True
    return False


def isTupleInterval(interval):
    # проверяет, является ли интервал типа ((1970, 1, 1, 0, 0, 0), (1970, 1, 25, 0, 0, 0))
    isTuple = True
    
    if type(interval) is not tuple or type(interval) is not list:
        isTuple = False

    if len(interval) != 2:
        isTuple = False

    if type(interval[0]) is not tuple or type(interval[0]) is not list:
        isTuple = False

    if len(interval[0]) != 6:
        isTuple = False

    for x in interval[0]:
        if type(x) is not int:
            isTuple = False
            break
    
    if type(interval[1]) is not tuple or type(interval[1]) is not list:
        isTuple = False

    if len(interval[1]) != 6:
        isTuple = False

    for x in interval[1]:
        if type(x) is not int:
            isTuple = False
            break
    
    return isTuple
        
    

