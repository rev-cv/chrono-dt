
class IntervalCatcher(object):

    def set(self, start = None, finish = None):


        if start is not None and finish is not None:
            self.setStart(start)
            self.setFinish(finish)
        else:
            if self.roundOff is None:
                self.roundOff = "day"
            if start is not None:
                self.setStart(start)
                self.setFinish(start)
            elif finish is not None:
                self.setStart(finish)
                self.setFinish(finish)
            else:
                now = self.chrono()
                self.setStart(now)
                self.setFinish(now)

        if self.s.tz != self.f.tz:
            # трагическая ситуация, когда пришли две даты с разными временными зонами
            # в этом случае окончание периода приводится к временной зоне начала периода
            self.f.toTimeZone(self.s.tz)
        self.tz = self.s.tz


    def setStart(self, start):
        if self.roundOff is not None:
            if self.expand is True:
                self.s = self.__decrease(
                    self.chrono(start),
                    self.roundOff
                )
            elif self.expand is False:
                self.s = self.__increase(
                    self.chrono(start),
                    self.roundOff
                )
        else:
            self.s = self.chrono(start)

        if self.s.isTime() is False:
            self.s.setTupleTime(0, 0, 0)

        return self


    def setFinish(self, finish):
        if self.roundOff is not None:
            if self.expand is True:
                self.f = self.__increase(
                    self.chrono(finish),
                    self.roundOff
                )
            elif self.expand is False:
                self.f = self.__decrease(
                    self.chrono(finish),
                    self.roundOff
                )
        else:
            self.f = self.chrono(finish)
        
        if self.f.isTime() is False:
            self.f.setTupleTime(0, 0, 0)

        return self

    
    def __increase(self, ch, ro):
        # смещение даты вправо по исторической шкале
        if 'day' == ro:
            ch.H, ch.M, ch.S = 0, 0, 0
            ch.shift(day=1)
        elif 'month' == ro:
            ch.H, ch.M, ch.S, ch.d = 0, 0, 0, 1
            ch.shift(month=1)
        elif 'hour' == ro:
            ch.M, ch.S = 0, 0
            ch.shift(hour=1)
        elif 'year' == ro:
            ch.H, ch.M, ch.S = 0, 0, 0
            ch.d, ch.m = 1, 1
            ch.shift(year=1)
        elif 'decade' == ro:
            ch.H, ch.M, ch.S = 0, 0, 0
            if ch.d <= 10:
                ch.d = 11
            elif ch.d <= 20:
                ch.d = 21
            else:
                ch.d = 1
                ch.shift(month=1)
        elif 'quarter' == ro:
            ch.H, ch.M, ch.S, ch.d = 0, 0, 0, 1
            if ch.m <= 3:
                ch.m = 4
            elif ch.m <= 6:
                ch.m = 7
            elif ch.m <= 9:
                ch.m = 10
            else:
                ch.m = 1
                ch.shift(year=1)
        elif 'decennary' == ro:
            ch.H, ch.M, ch.S = 0, 0, 0,
            ch.d, ch.m = 1, 1
            ch.y = int(str(ch.y)[:-1] + "0") + 10
        elif "minute" == ro:
            ch.M, ch.S = 0, 0
            ch.shift(minute=1)
        
        return ch

    def __decrease(self, ch, ro):
        # смещение даты влево по исторической шкале
        if 'day' == ro:
            ch.H, ch.M, ch.S = 0, 0, 0
        elif 'month' == ro:
            ch.H, ch.M, ch.S, ch.d = 0, 0, 0, 1
        elif 'hour' == ro:
            ch.M, ch.S = 0, 0
        elif 'year' == ro:
            ch.H, ch.M, ch.S = 0, 0, 0
            ch.d, ch.m = 1, 1
        elif 'decade' == ro:
            ch.H, ch.M, ch.S = 0, 0, 0
            if ch.d <= 10:
                ch.d = 1
            elif ch.d <= 20:
                ch.d = 11
            else:
                ch.d = 21
        elif 'quarter' == ro:
            ch.H, ch.M, ch.S, ch.d = 0, 0, 0, 1
            if ch.m <= 3:
                ch.m = 1
            elif ch.m <= 6:
                ch.m = 3
            elif ch.m <= 9:
                ch.m = 6
            else:
                ch.m = 9
        elif 'decennary' == ro:
            ch.H, ch.M, ch.S = 0, 0, 0,
            ch.d, ch.m = 1, 1
            ch.y = int(str(ch.y)[:-1] + "0")
        elif "minute" == ro:
            ch.M, ch.S = 0, 0
        
        return ch


    def setRoundOff(self, roundOff):
        if roundOff in ['hour', 'day', 'month', 'year', 'decade', 'quarter', 'decennary', 'minute', None]:
            return roundOff
        raise Exception("Invalid argument passed for 'roundOff'")

