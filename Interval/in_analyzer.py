
class IntervalAnalyzer(object):

    def isReal(self, isGenerateError=False):
        # является ли полученный интервал реальным?
        # Например если start == finish или start > finish
        # то такого периода не может существовать в реальности
        
        if self.s >= self.f:
            if isGenerateError:
                error = "\nThe created interval cannot exist in reality!\n"
                # Созданный интервал не может существовать в реальности!
                error += "The start of the interval cannot:\n"
                error += "    - occur later than the finish of the interval\n"
                error += "    - coincide with the finish of the interval\n"
                # Старт интервала не может произойти позже финиша интервала.
                # Старт интервала не может совпадать с финишем интервала!
                
                if self.expand is False:
                    error += "Probably using `expand=False` caused the interval to collapse.\n"
                    # Вероятно использование `expand=False` привело к схлопыванию интервала
                
                error += "There may be an error in the received `class Interval` data."
                # Возможна ошибка в полученных данных `class Interval`.
                raise Exception(error)
    
    def isChronoInto(self, chrono):
        # входит ли переданная дата в данный период?
        pass

    def isIntervalInto(self, interval,  onlyFullEntry=False):
        # входит ли переданный интервал в текущий интервал?
        # onlyFullEntry=False — переданный период не может выходить за границы текущего
        # onlyFullEntry=True — достаточно чтобы хотя бы часть периода лежала на текущем периоде
        pass