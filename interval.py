from chrono import Chrono
from re import sub, compile


class Interval(object):
    def __init__(self, dates = None, roundOff = None, expand=True, about=None):
        super(Interval, self).__init__()

        # roundOff — округляет интервал путем расширения, если expand=True
        # roundOff — округляет интервал путем уменьшения, если expand=False

        # ПРИМЕР start = <2022-10-25 12:45>, finish = <2022-11-26 4:35>

        # roundOff = None — добавляет интервалы никак не преобразовывая входящие Chrono
        # "hour" — округляет период до часа
        #       expand=True  → <2022-10-25 12:00:00 — 2022-11-26 05:00:00>
        #       expand=False → <2022-10-25 13:00:00 — 2022-11-26 04:00:00>
        # 'day' — округляет период до дня
        #       expand=True  → <2022-10-25 00:00:00 — 2022-11-27 00:00:00>
        #       expand=False → <2022-10-26 00:00:00 — 2022-11-26 00:00:00>
        #       ↑ В данном случае должна быть ошибка "Использование `expand=False`
        #       привело к схлопыванию интервала"
        #       Если в interval() передано только start или только finish, а roundOff == None
        #       то применяются roundOff="day"
        # 'month' — округляет период до месяца
        #       expand=True  → <2022-10-01 00:00:00 — 2022-11-30 00:00:00>
        #       expand=False → <2022-11-01 00:00:00 — 2022-11-01 00:00:00>
        #       ↑ В данном случае должна быть ошибка "Использование `expand=False`
        #       привело к схлопыванию интервала"
        # "year" — округляет интервал до года
        #       expand=True  → <2022-01-01 00:00:00 — 2023-01-01 00:00:00>
        #       expand=False → <2023-11-01 00:00:00 — 2022-11-01 00:00:00>
        #       ↑ В данном случае должна быть ошибка "Интервал слишком короткий
        #       чтобы можно было использовать `expand=False` и 'roundOff='year'"
        # "decade" - декада месяца
        # `quarter` - квартал года
        # "decennary" - десятелетие

        self.intervals = Intervals
        self.s = None # start начало временного интервала
        self.f = None # finish конец временного интервала
        self.tz = None
        self.about = about
        # ↑ Любая информация, которую можно присвоить интервалу
        # эта информация будет просто таскаться за интервалом
        # полезно, когда речь идет не о гипотетических интервалах

        self.fragments = []
        # ↑ список возможных дочерних интервалов

        self.roundOff = None
        self.setRoundOff(roundOff)
        self.expand = expand

        if type(dates) is tuple or type(dates) is list:
            self.set(*dates)
        else:
            self.set(dates)
            
        self.isReal(True)
        # ↑ проводит жесткую проверку на верность интервала в ошибкой если это не так
        

    def __str__(self):
        s = 'INTERVAL\n'
        s += '    START START[[yyyy-MM-dd hh:mm:ss]]\n'
        s += '    FINISH FINISH[[yyyy-MM-dd hh:mm:ss]]\n'
        s += '    TZ tz\n'
        s += f'    FRAG {len(self.fragments)}\n'
        return self.template(s)


    # ·······················································
    # CHRONO ANALYZER
    # → Анализирует поступающие и хранящиеся данные
    # ·······················································


    def isReal(self, isGenerateError=False):
        # является ли полученный интервал реальным?
        # Например если start == finish или start > finish
        # то такого периода не может существовать в реальности

        if self.s >= self.f:  # type: ignore
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
        if chrono.isTime() is False:
            chrono.setTupleTime(0, 0, 0)
        if self.s < chrono < self.f:
            return True
        return False

    def isIntervalInto(self, interval):
        # входит ли переданный интервал в текущий интервал? 
        # Переданный период не может выходить за границы текущего!
        if self.s < interval.s < interval.f < self.f:
            return True
        return False

    def isIntervalLayered(self, interval):
        # закрывает ли переданный интервал хотя бы часть текущего интервала?
        if self.s < interval.s < self.f or self.s < interval.f < self.f:
            return True
        return False


    # ·······················································
    # CHRONO CATCHER
    # → Задает данные в interval
    # ·······················································


    def set(self, start = None, finish = None):
    
        if start is not False:
            if start is not None and finish is not None:
                self.setStart(start)
                self.setFinish(finish)
            else:
                if self.roundOff is None:
                    self.roundOff = "day"
                    self.expand = True
                if isinstance(start, Interval):
                    if isinstance(finish, Interval):
                        # если передано два периода, нужно предпринять попытку их объединить
                        result = self._defineBoundary(start, finish)
                        if result is not False:
                            self.s, self.f = result.s, result.f
                    else:
                        self.s, self.f = start.s, start.f
                elif start is not None:
                    self.setStart(start)
                    self.setFinish(start)
                elif finish is not None:
                    self.setStart(finish)
                    self.setFinish(finish)
                else:
                    now = Chrono()
                    self.setStart(now)
                    self.setFinish(now)

            self.tz = self.s.tz # type: ignore
            if self.s.tz != self.f.tz: # type: ignore
                # трагическая ситуация, когда пришли две даты с разными временными зонами
                # в этом случае окончание периода приводится к временной зоне начала периода
                self.f.toTimeZone(self.s.tz)  # type: ignore
        

    def setStart(self, start):
        if self.roundOff is not None:
            if self.expand is True:
                self.s = self._decrease(
                    Chrono(start),
                    self.roundOff
                )
            elif self.expand is False:
                self.s = self._increase(
                    Chrono(self.s),
                    self.roundOff
                )
        else:
            self.s = Chrono(start)

        if self.s.isTime() is False: # type: ignore
            self.s.setTupleTime(0, 0, 0)  # type: ignore

        return self


    def setFinish(self, finish):
        if self.roundOff is not None:
            if self.expand is True:
                self.f = self._increase(
                    Chrono(finish),
                    self.roundOff
                )
            elif self.expand is False:
                self.f = self._decrease(
                    Chrono(finish),
                    self.roundOff
                )
        else:
            self.f = Chrono(finish)
        
        if self.f.isTime() is False: # type: ignore
            self.f.setTupleTime(0, 0, 0)  # type: ignore

        return self

    
    def _increase(self, ch, ro):
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
                ch.y, ch.m = ch.y+1, 1
        elif 'decennary' == ro:
            ch.H, ch.M, ch.S = 0, 0, 0,
            ch.d, ch.m = 1, 1
            ch.y = int(str(ch.y)[:-1] + "0") + 10
        elif "minute" == ro:
            ch.S = 0
            ch.shift(minute=1)
        elif 'week' == ro:
            # смещение до следующего понедельника
            ch.H, ch.M, ch.S = 0, 0, 0
            ch.shift(day = 8 - ch.getWeekday())
        return ch

    def _decrease(self, ch, ro):
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
            if ch.m < 4:
                ch.m = 1
            elif ch.m < 7:
                ch.m = 4
            elif ch.m < 10:
                ch.m = 7
            else:
                ch.m = 10
        elif 'decennary' == ro:
            ch.H, ch.M, ch.S = 0, 0, 0,
            ch.d, ch.m = 1, 1
            ch.y = int(str(ch.y)[:-1] + "0")
        elif "minute" == ro:
            ch.S = 0
        elif 'week' == ro:
            # смещение до прошлого понедельника
            ch.H, ch.M, ch.S = 0, 0, 0
            ch.shift(day = ch.getWeekday() * (-1) + 1)
        return ch

    def setRoundOff(self, roundOff):
        if roundOff in ['hour', 'day', 'month', 'year', 'decade', 'quarter', 'decennary', 'minute', None, 'week']:
            self.roundOff = roundOff
            return self
        raise Exception("Invalid argument passed for 'roundOff'")


    def setFramentation(self, *intervals):
        # задает список интервалов для self.fragments
        # Из переданного исписка исключаются интервалы не входящие в self
        # интервалы входящие частично в self обрезаются 
        s1 = self.s.getUnixEpoch() # type: ignore
        f1 = self.f.getUnixEpoch()  # type: ignore

        for x in intervals:
            s2 = x.s.getUnixEpoch()
            f2 = x.f.getUnixEpoch()

            if s1 <= s2 and f2 <= f1:
                # интервал входит в self
                self.fragments.append(x)
            elif s2 < s1 and s1 < f2 <= f1:
                # старт интервала начинается раньше self. Обрезать!
                self.fragments.append(
                    Interval((self.s, x.f))
                )
            elif s1 <= s2 < f1 and f2 > f1:
                # старт интервала начался в self, но завершился после окончания self. Образать!
                self.fragments.append(
                    Interval( (x.s, self.f) )
                )
            elif s2 <= s1 and f1 <= f2:
                # интервал поглощается self, обрезать с двух сторон
                self.fragments.append(
                    Interval( (self.s, self.f) )
                )
        return self
    

    # ·······················································
    # CHRONO PITCHER
    # → Выводит информацию из interval
    # ·······················································


    def getСompleted(self, chrono):
        # определяет процент завершенности текущего периода
        # на основании переданной даты
        if chrono.isTime() is False:
            chrono.setTupleTime(0, 0, 0)
        c1 = self.s.getUnixEpoch() # type: ignore
        c2 = chrono.getUnixEpoch()
        c3 = self.f.getUnixEpoch()  # type: ignore
        if c1 < c2 < c3:
            return round((c2 - c1) * 100 / (c3 - c1), 1)

    def getOccupancy(self):
        # выдает процент заполненности интервала self интервалами из self.fragments
        diff = self.getOccupancyFragments()
        frag = self.getDuration()
        return round(diff * 100 / frag, 1)  # type: ignore

    def getOccupancyFragments(self, measure='second'):
        # подсчитывает заполнение интервалами из self.fragments для self
        return self.intervals(*self.fragments).occupancy(measure)

    def getDuration(self, measure='second'):
        diff = self.f.getUnixEpoch() - self.s.getUnixEpoch()  # type: ignore

        if 'second' == measure:
            return diff
        elif 'minute' == measure:
            return diff // 60
        elif 'hour' == measure:
            return round(diff / 3600, 1)
        elif 'day' == measure:
            return round(diff / 86400, 1)
        elif 'divided' == measure:
            # не является точным измерением и предназначен для информирования
            by = diff // (86400 * 365)
            bd = (diff - (by * 86400 * 365)) // 86400
            bh = (diff - (bd * 86400)) // 3600
            bm = (diff - (bd * 86400 + bh * 3600)) // 60
            bs = (diff - (bd * 86400 + bh * 3600)) % 60

            return {'y': by, 'd': bd, 'h': bh, 'm': bm, 's': bs}


    # ·······················································
    # CHRONO TRANSFORMATOR
    # → Изменяет внутреннее состояние interval
    # ·······················································

    def fragmentation(self, frag= "day"):
        # раздробить интервал self на дни / часы / прочее
        # фрагменты не могут выходить за границы интервала self
        self.fragments = list()
        proceed = True

        def conversion_from_unixepoch():
            self.fragments = [

                Interval(
                    Chrono(False).setUnixEpoch(x).toTimeZone(
                        self.tz),  # type: ignore
                    roundOff=frag
                )

                for x in self.fragments

            ]
        
        def conversion_from_tuple():
            self.fragments = [

                Interval(
                    Chrono(False).setTupleDate(*x).setTupleTime(0,0,0).toTimeZone(self.tz), # type: ignore
                    roundOff=frag
                )

                for x in self.fragments

            ]
            

        if "day" == frag:
            c = Chrono(False).setChrono(self.s)
            if c.isDayBegun():
                c.setTupleTime(0, 0, 0).shift(day=1)
            current = c.getUnixEpoch()

            f = Chrono(False).setChrono(self.f).setTupleTime(0, 0, 0)
            finish = f.getUnixEpoch()

            while proceed:
                if current < finish:
                    self.fragments.append(current)
                else:
                    proceed = False
                current += 86400
            
            conversion_from_unixepoch()

        elif 'decade' == frag:
            # "2014-10-11", "2014-11-01"
            current_dec = 3
            current_month = self.s.m # type: ignore
            current_year = self.s.y  # type: ignore
            if self.s.d == 1:        # type: ignore
                current_dec = 1
            elif self.s.d <= 11:     # type: ignore
                current_dec = 2

            finish_dec = 3
            finish_month = self.f.m  # type: ignore
            finish_year = self.f.y   # type: ignore
            if self.f.d < 11:        # type: ignore
                finish_dec = 1
            elif self.f.d < 21:      # type: ignore
                finish_dec = 2
            
            d = {1:1,2:11,3:21}

            while proceed:
                self.fragments.append(
                    (current_year, current_month, d[current_dec])
                )

                current_dec += 1

                if 3 < current_dec:
                    current_dec = 1
                    current_month += 1     # type: ignore

                    if 12 < current_month:
                        current_month = 1
                        current_year += 1  # type: ignore
                        
                isDec = current_dec == finish_dec
                isMonth = current_month == finish_month
                isYear = current_year == finish_year

                if isDec and isMonth and isYear:
                    proceed = False
            
            conversion_from_tuple()

        elif 'month' == frag:
            c = Chrono(False).setTupleDate(
                self.s.y, self.s.m, 1).setTupleTime(0, 0, 0) # type: ignore
            if c.isDayBegun() or self.s.d > 1:  # type: ignore
                c.shift(month=1)
            current = c.getUnixEpoch()
            current_year = c.y
            current_month = c.m

            finish = Chrono(False).setTupleDate(self.f.y, self.f.m, 1) # type: ignore
            finish = finish.setTupleTime(0, 0, 0).getUnixEpoch()

            i30 = 2592000  # 30 дней
            i31 = 2592000 + 86400  # 31 дней в некоторых 3х декадах месяца
            i29 = 2592000 - 86400  # 29 дней в феврале високосного года
            i28 = 2592000 - (86400 * 2)  # 28 дней в феврале обычного года

            increments = {
                1:  i30,
                2:  i29 if c.isLeapYear(current_year) else i28,
                3:  i31,
                4:  i30,
                5:  i31,
                6:  i30,
                7:  i31,
                8:  i31,
                9:  i30,
                10: i31,
                11: i30,
                12: i31,
            }

            while proceed:
                current += increments[current_month]  # type: ignore

                if current <= finish:
                    self.fragments.append(current)
                else:
                    proceed = False

                if current_month + 1 > 12:  # type: ignore
                    current_month = 1
                    current_year += 1  # type: ignore
                    increments[2] = i29 if c.isLeapYear(current_year) else i28
                else:
                    current_month += 1  # type: ignore
            
            conversion_from_unixepoch()

        elif 'week' == frag:
            c = Chrono(False).setChrono(self.s)
            if c.isDayBegun():
                c.setTupleTime(0, 0, 0).shift(day=1)
            wdc = c.getWeekday()
            if wdc != 1:
                c.shift(day=8 - wdc)
            current = c.getUnixEpoch()

            f = Chrono(False).setChrono(self.f)
            if f.isDayBegun():
                f.setTupleTime(0, 0, 0)
            wdf = f.getWeekday()
            if wdf != 1:
                f.shift(day=wdf * (-1) + 1)
            finish = f.getUnixEpoch()

            self.fragments.append(current)

            while proceed:
                current += 604800  # 86400 * 7
                if current < finish:
                    self.fragments.append(current)
                else:
                    proceed = False
            
            conversion_from_unixepoch()

        elif 'quarter' == frag:
            isDayNotBegun = self.s.isDayBegun() is False  # type: ignore

            current_qua = 1
            current_year = self.s.y  # type: ignore

            if self.s.m == 1 and self.s.d == 1 and isDayNotBegun:  # type: ignore
                pass
            elif self.s.m < 4 or (self.s.m == 4 and self.s.d == 1 and isDayNotBegun): # type: ignore
                current_qua = 2
            elif self.s.m < 7 or (self.s.m == 7 and self.s.d == 1 and isDayNotBegun): # type: ignore
                current_qua = 3
            elif self.s.m == 10 and self.s.d == 1 and isDayNotBegun: # type: ignore
                current_qua = 4
            else:
                current_year += 1   # type: ignore
            
            isDayNotBegun = self.f.isDayBegun() is False  # type: ignore
            
            finish_qua = 4
            finish_year = self.f.y  # type: ignore

            if self.f.m == 1 and self.f.d == 1 and isDayNotBegun:  # type: ignore
                finish_year -= 1     # type: ignore
            elif self.f.m < 4:       # type: ignore
                finish_qua = 1
            elif self.f.m < 7:       # type: ignore
                finish_qua = 2
            elif self.f.m < 10:      # type: ignore
                finish_qua = 3
            
            q = {1:1,2:4,3:7,4:10}

            while proceed:
                self.fragments.append(
                    (current_year, q[current_qua], 1)
                )

                current_qua += 1

                if 4 < current_qua:
                    current_qua = 1
                    current_year += 1  # type: ignore

                isMoreYear = current_year > finish_year  # type: ignore
                isMoreQua = current_year == finish_year and current_qua > finish_qua
                
                if isMoreYear or isMoreQua:
                    proceed = False

            conversion_from_tuple()

        elif 'year' == frag:
            c = Chrono(False).setChrono(self.s)
            current_year = c.y
            if c.m == 1 and c.d == 1 and c.isDayBegun() is False:
                c.m, c.d, c.H, c.M, c.S = 1, 1, 0, 0, 0
            else:
                c.y, c.m, c.d, c.H, c.M, c.S = c.y+1, 1, 1, 0, 0, 0  # type: ignore
            current = c.getUnixEpoch()

            f = Chrono(False).setChrono(self.f)
            f.m, f.d, f.H, f.M, f.S = 1, 1, 0, 0, 0
            finish = f.getUnixEpoch()

            while proceed:
                if current < finish:
                    self.fragments.append(current)
                else:
                    proceed = False

                current_year += 1  # type: ignore
                # ↓ 366/365 * 86400
                current += 31622400 if c.isLeapYear(current_year) else 31536000
            
            conversion_from_unixepoch()

        elif 'decennary' == frag:
            c = Chrono(False).setChrono(self.s)
            if c.m == 1 and c.d == 1 or c.isDayBegun() is False:
                dy = c.y // 10 * 10  # type: ignore
                c.y = dy if c.y == dy else dy + 10
            else:
                c.y, c.m, c.d, c.H, c.M, c.S = (
                    c.y // 10 + 1) * 10, 1, 1, 0, 0, 0  # type: ignore

            f = Chrono(False).setChrono(self.f)
            f.y, f.m, f.d, f.H, f.M, f.S = f.y // 10 * 10, 1, 1, 0, 0, 0  # type: ignore

            while proceed:
                if c < f:
                    self.fragments.append(c.getUnixEpoch())
                else:
                    proceed = False

                c.y += 10
            
            conversion_from_unixepoch()

        elif 'hour' == frag:
            c = Chrono(False).setChrono(self.s)
            if c.isDayBegun() is False:
                c.shift(hour=1)
                c.H, c.M, c.S = 0, 0, 0
            current = c.getUnixEpoch()

            f = Chrono(False).setChrono(self.f)
            if f.isDayBegun() is False:
                f.H, f.M, f.S = 0, 0, 0
            finish = f.getUnixEpoch()

            while proceed:
                if current < finish:
                    self.fragments.append(current)
                else:
                    proceed = False
                current += 3600
            
            conversion_from_unixepoch()

        elif 'minute' == frag:
            c = Chrono(False).setChrono(self.s)
            if c.M > 0 or c.S > 0:  # type: ignore
                c.shift(minute=1)
                c.M, c.S = 0, 0
            current = c.getUnixEpoch()

            f = Chrono(False).setChrono(self.f)
            if f.isDayBegun() is False:
                f.M, f.S = 0, 0
            finish = f.getUnixEpoch()

            while proceed:
                if current < finish:
                    self.fragments.append(current)
                else:
                    proceed = False
                current += 60

            conversion_from_unixepoch()

        return self

    def step(self, st=0):
        # «шагает» по интервалам в зависимости от roundOff
        # если roundOff == "day", то при st = -1, период будет изменен на предыдущий день
        # если roundOff == None, то интервал будет смещаться на свою длину
        def setNew(inter):
            self.s = inter.s
            self.f = inter.f
        if self.roundOff == "day":
            setNew(Interval(Chrono(self.s).shift(day=st), roundOff="day"))
        elif self.roundOff == "week":
            # предполагается, что self.s при roundOff=="week" всегда понедельник
            setNew(Interval(Chrono(self.s).shift(day=st*7), roundOff="week"))
        elif self.roundOff == "decade":
            ch = Chrono(self.s)
            if st < 0:
                while st < 0:
                    if ch.d < 11: # type: ignore
                        ch.y = ch.y if ch.m-1 > 0 else ch.y-1  # type: ignore
                        ch.m = ch.m-1 if ch.m-1 > 0 else 12  # type: ignore
                        ch.d = 21
                    elif ch.d < 21:  # type: ignore
                        ch.d = 1
                    else:
                        ch.d = 11
                    st += 1
            elif st > 0:
                while st > 0:
                    if ch.d < 11:  # type: ignore
                        ch.d = 11
                    elif ch.d < 21:  # type: ignore
                        ch.d = 21
                    else:
                        ch.y = ch.y if ch.m < 12 else ch.y+1  # type: ignore
                        ch.m = ch.m + 1 if ch.m < 12 else 1  # type: ignore
                        ch.d = 1
                    st -= 1
            setNew(Interval(ch, roundOff="decade"))
        elif self.roundOff == "month":
            setNew(Interval(Chrono(self.s).shift(month=st), roundOff="month"))
        elif self.roundOff == "quarter":
            ch = Chrono(self.s.y, self.s.m, 1, 0, 0, 0)  # type: ignore
            if st < 0:
                while st < 0:
                    if ch.m <= 3:  # type: ignore
                        ch.y -= 1  # type: ignore
                        ch.m = 10
                    elif ch.m <= 6:  # type: ignore
                        ch.m = 1
                    elif ch.m <= 9:  # type: ignore
                        ch.m = 4
                    else:
                        ch.m = 7
                    st += 1
            elif st > 0:
                while st > 0:
                    if ch.m <= 3:  # type: ignore
                        ch.m = 4
                    elif ch.m <= 6:  # type: ignore
                        ch.m = 7
                    elif ch.m <= 9:  # type: ignore
                        ch.m = 10
                    else:
                        ch.m = 1
                        ch.y += 1  # type: ignore
                    st -= 1
            setNew(Interval(ch, roundOff="quarter"))
        elif self.roundOff == "year":
            setNew(Interval(Chrono(self.s).shift(year=st), roundOff="year"))
        elif self.roundOff == "decennary":
            setNew(Interval(Chrono(self.s).shift(year=st*10), roundOff="decennary"))
        elif self.roundOff == "hour":
            setNew(Interval(Chrono(self.s).shift(hour=st), roundOff="hour"))
        elif self.roundOff == "minute":
            setNew(Interval(Chrono(self.s).shift(minute=st), roundOff="minute"))
        elif self.roundOff is None:
            diff = self.getDuration()
            setNew(Interval(Chrono(self.s).shift(second=diff), roundOff="minute")) # type: ignore
        return self

    def join(self, interval, greedy=False):
        # объединить два интервала
        # если greedy = False, то два интервала объединятся только
        # если они хотя бы частично входят друг в друга
        # если greedy = True, то для объединения берутся две крайние точки
        # пропуски между интервалами так же входят в состав интервала
        if greedy:
            chs = sorted(
                [self.s, self.f, interval.s, interval.f],
                key=lambda ch: ch.getUnixEpoch()  # type: ignore
            )
            self = Interval((chs[0], chs[-1]))
            return self
        else:
            result = self._defineBoundary(self, interval)
            if isinstance(result, Interval):
                self = result
                return self
            return False

    def _defineBoundary(self, i1, i2):
        # определяет включенность одного интервала в другой
        # если возможно объединение объединяет эти два интервала в один
        if i1.s.isTime() is False:
            i1.s.setTupleTime(0, 0, 0)
        if i1.f.isTime() is False:
            i1.f.setTupleTime(0, 0, 0)
        if i2.s.isTime() is False:
            i2.s.setTupleTime(0, 0, 0)
        if i2.f.isTime() is False:
            i2.f.setTupleTime(0, 0, 0)

        u1 = i1.s.getUnixEpoch()
        u2 = i1.f.getUnixEpoch()
        u3 = i2.s.getUnixEpoch()
        u4 = i2.f.getUnixEpoch()

        if u3 <= u1 and u2 <= u4:
            # i1 into i2
            return Interval(i2)
        elif u1 <= u3 and u4 <= u2:
            # i2 into i1
            return Interval(i1)
        elif u2 == u3 or (u3 < u2 and u1 <= u3):
            # i1 и i2 следуют друг за другом стык-в-стык
            # или начало i2 лежит в периоде i1
            return Interval((i1.s, i2.f))
        elif u4 == u1 or (u1 < u4 and u3 <= u1):
            # i2 и i1 следуют друг за другом стык-в-стык
            # или начала i1 лежит в периоде i2
            return Interval((i2.s, i1.f))

        return False


    # ·······················································
    # STRING CONSTRUCTION
    # → Изменяет внутреннее состояние chrono
    # ·······················································

    def T(self, temp = r"yyyy-MM-dd hh:mm:ss"):
        return self.template(temp)

    def template(self, temp = r"yyyy-MM-dd hh:mm:ss"):
        """
        Имеются шаблон для старта периода и шаблон для финиша
        START[[yyyy-MM-dd hh:mm:ss]]
        FINISH[[yyyy-MM-dd hh:mm:ss]]
        """

        self.re_start = compile(r'START(\[\[.*?\]\])')
        self.re_finish = compile(r'FINISH(\[\[.*?\]\])')
        self.re_chrono = compile(r'\[\[(.*?)\]\]')

        def start_template(temp_chrono):
            return self.s.template(  # type: ignore
                self.re_chrono.findall(temp_chrono[0])[0]
            )
        
        def finish_template(temp_chrono):
            return self.f.template(  # type: ignore
                self.re_chrono.findall(temp_chrono[0])[0]
            )

        temp = self.re_start.sub(start_template, temp)
        temp = self.re_finish.sub(finish_template, temp)

        regex = r'tz'	#временная зона
        if regex in temp:
            temp = sub(regex, f'{self.tz}', temp)
        
        return temp


class Intervals(object):
    """Обрабатывает список интервалов"""

    def __init__(self, *intervals):
        super(Intervals, self).__init__()
        self.intervals = list(intervals)

    def skip(self):
        # создаст список пропущенных интервалов, которые могут быть вписаны между
        joined = self.join()
        result = list()
        if len(joined) > 0:

            current = joined[0]

            for x in joined[1:]:
                if current.f.getUnixEpoch() < x.s.getUnixEpoch():
                    result.append(
                        Interval(
                            (current.f, x.s)
                        )
                    )
                    current = x

        return result

    def join(self):
        # интервалы между которыми не существует пропусков объединяются в один интервал
        # выдается список объедененныъх интервалов

        toUnite = sorted(self.intervals, key=lambda ch: ch.s.getUnixEpoch())
        result = list()

        if len(toUnite) > 0:

            current = toUnite[0]

            for x in toUnite[1:]:
                r = current.join(x)
                if r is not False:
                    current = r
                else:
                    result.append(current)
                    current = x
            result.append(current)

        return result

    def сalendar(self, year):
        # получить матрицу интервалов содержащих указанный год
        # year.fragments(
        #   months.fragments(
        #       weeks.fragments(
        #           days
        #       )
        #   )
        # )
        pass

    def occupancy(self, measure='second'):
        # заполненность периодами
        # от sum отличается тем, что не учитываются наслаивание периодов
        sumfrags = 0.0
        for x in self.join():
            sumfrags += x.getDuration(measure)
        return sumfrags

    def sum(self, measure='second'):
        # общая сумма всех интервалов содержащихся в self
        sumfrags = 0.0
        for x in self.intervals:
            sumfrags += x.getDuration(measure)
        return sumfrags


if __name__ == '__main__':
    year = Interval(("2014-1-1", "2015-1-1")).fragmentation("quarter")
    s = 'START[[yyyy-MM-dd]] - FINISH[[yyyy-MM-dd]]'

    for y in year.fragments:
        
        print(
            y.template(s),
            y.s.F("%QUA")
        )
