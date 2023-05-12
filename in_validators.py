

def isReal(start, finish, isExpansion = True, isGenerateError=False):
    # является ли полученный интервал start—finish реальным?
    # Например если start == finish или start > finish ↲
    # то такого периода не может существовать в реальности.

    # Функция isReal принимает объекты Chrono и datetime.datetime
    
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

def isDateWithinInterval(date, start, finish):
    # входит ли переданная дата в данный период?
    # Функция isDateWithinInterval принимает объекты Chrono и datetime.datetime
    if start <= date <= finish:
        return True
    return False

def isIntervalWithinInterval(ds, df, in_ds, in_df, isFullEntry=False):
    # входит ли переданный интервал в текущий интервал?

    # принимаемые даты могут быть Chrono или datetime.datetime

    # isFullEntry — 
    # должно ли быть полное вхождение (True) 
    # или интервал может выходить за границы (False)?

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
