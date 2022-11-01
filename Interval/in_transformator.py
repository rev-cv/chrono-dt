import asyncio

class IntervalTransformator(object):
    def __init__(self):
        super(IntervalTransformator, self).__init__()

    def fragmentation(self, frag = "day"):
        # раздробить интервал self на дни / часы / прочее
        # фрагменты не могут выходить за границы интервала self
        self.fragments = list()
        proceed = True
            
        if "day" == frag:
            c = self.chrono(False).setChrono(self.s)
            if c.isDayBegun() is False:
                c.setTupleTime(0,0,0).shift(day=1)
            current = c.getUnixEpoch()

            f = self.chrono(False).setChrono(self.f).setTupleTime(0,0,0)
            finish = f.getUnixEpoch()
            
            chronoes = [current, ]

            while proceed:
                current += 86400
                if current <= finish:
                    chronoes.append(current)
                else:
                    proceed = False
                
        elif 'decade' == frag:
            c = self.chrono(False).setTupleTime(0,0,0)
            current_dec = 0
            if self.s.isDayBegun() is False and self.s.d == 1:
                c.setTupleDate(self.s.y, self.s.m, 1)
            elif self.s.d <= 10:
                c.setTupleDate(self.s.y, self.s.m, 11)
                current_dec = 1
            elif self.s.d <= 20:
                c.setTupleDate(self.s.y, self.s.m, 21)
                current_dec = 2
            else:
                c.setTupleDate(
                    self.s.y if self.s.m + 1 <= 12 else self.s.y + 1,
                    self.s.m + 1 if self.s.m + 1 <= 12 else 1,
                    1
                )
            current = c.getUnixEpoch()
            current_year = c.y
            current_month = c.m

            f = self.chrono(False).setTupleTime(0,0,0)
            if self.f.d <= 10:
                f.setTupleDate(self.f.y, self.f.m, 1)
            elif self.f.d <= 20:
                f.setTupleDate(self.f.y, self.f.m, 11)
            else:
                f.setTupleDate(self.f.y, self.f.m, 21)
            finish = f.getUnixEpoch()

            i10 = 864000 # 10 дней
            i31 = 950400 # 11 дней в некоторых 3х декадах месяца
            i29 = 777600 # 9 дней в феврале високосного года
            i28 = 691200 # 8 дней в феврале обычного года

            increments = {
                1:  [i10, i10, i31],
                2:  [i10, i10, i29 if c.isLeapYear(current_year) else i28],
                3:  [i10, i10, i31],
                4:  [i10, i10, i10],
                5:  [i10, i10, i31],
                6:  [i10, i10, i10],
                7:  [i10, i10, i31],
                8:  [i10, i10, i31],
                9:  [i10, i10, i10],
                10: [i10, i10, i31],
                11: [i10, i10, i10],
                12: [i10, i10, i31],
            }

            chronoes = [current, ]

            while proceed:
                while proceed and current_dec < 3:

                    current += increments[current_month][current_dec]

                    if current < finish:
                        chronoes.append(current)
                        current_dec += 1
                    else:
                        proceed = False

                current_dec = 0

                if current_month + 1 > 12:
                    current_month = 1
                    current_year += 1
                    increments[2][2] = i29 if c.isLeapYear(current_year) else i28
                else:
                    current_month += 1

        elif 'month' == frag:
            c = self.chrono(False).setTupleDate(self.s.y, self.s.m, 1).setTupleTime(0,0,0)
            if c.isDayBegun() is False and self.s.d > 1:
                c.shift(month=1)
            current = c.getUnixEpoch()
            current_year = c.y
            current_month = c.m

            finish = self.chrono(False)\
                .setTupleDate(self.f.y, self.f.m, 1)\
                .setTupleTime(0,0,0)\
                .getUnixEpoch()

            i30 = 2592000 # 30 дней
            i31 = 2592000 + 86400 # 31 дней в некоторых 3х декадах месяца
            i29 = 2592000 - 86400  # 29 дней в феврале високосного года
            i28 = 2592000 - (86400 * 2) # 28 дней в феврале обычного года

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

            chronoes = [current, ]
            
            while proceed:
                current += increments[current_month]

                if current <= finish:
                    chronoes.append(current)
                else:
                    proceed = False

                if current_month + 1 > 12:
                    current_month = 1
                    current_year += 1
                    increments[2] = i29 if c.isLeapYear(current_year) else i28
                else:
                    current_month += 1




        for x in chronoes:
            self.fragments.append(
                self.interval(
                    self.chrono(False).setUnixEpoch(x).toTimeZone(self.tz),
                    roundOff=frag
                )
            )




            








        # async def aisle():


        # async def random_sleep(i: int):
        #     delay = random.randint(1, 5)
        #     print(f"{i}: start sleep")
        #     await asyncio.sleep(delay)
        #     print(f"{i}: end sleep")
            
        # async def main():
        #     await asyncio.gather(
        #         random_sleep(1),
        #         random_sleep(2),
        #         random_sleep(3),
        #         random_sleep(4),
        #         random_sleep(5),
        #     )
            
        # asyncio.run(main())

    def join(self, interval, greedy = False):
        # объединить два интервала
        # если greedy = False, то два интервала объединятся только 
        # если они хотя бы частично входят друг в друга
        # если greedy = True, то для объединения берутся две крайние точки
        # пропуски между интервалами так же входят в состав интервала
        if greedy:
            chs = sorted(
                [self.s, self.f, interval.s, interval.f], 
                key = lambda ch: ch.getUnixEpoch()
            )
            self = self.interval(chs[0], chs[-1])
            return self
        else:
            result = self._defineBoundary(self, interval)
            if isinstance(result, self.interval):
                self = result
                return self
            return False

    
    def _defineBoundary(self, i1, i2):
        # определяет включенность одного интервала в другой
        # если возможно объединение объединяет эти два интервала в один
        if i1.s.isTime() is False:
            i1.s.setTupleTime(0,0,0)
        if i1.f.isTime() is False:
            i1.f.setTupleTime(0,0,0)
        if i2.s.isTime() is False:
            i2.s.setTupleTime(0,0,0)
        if i2.f.isTime() is False:
            i2.f.setTupleTime(0,0,0)

        u1 = i1.s.getUnixEpoch()
        u2 = i1.f.getUnixEpoch()
        u3 = i2.s.getUnixEpoch()
        u4 = i2.f.getUnixEpoch()

        if u3 <= u1 and u2 <= u4:
            # i1 into i2
            return self.interval(i2)
        elif u1 <= u3 and u4 <= u2:
            # i2 into i1
            return self.interval(i1)
        elif u2 == u3 or (u3 < u2 and u1 <= u3):
            # i1 и i2 следуют друг за другом стык-в-стык
            # или начало i2 лежит в периоде i1
            return self.interval(i1.s, i2.f)
        elif u4 == u1 or (u1 < u4 and u3 <= u1):
            # i2 и i1 следуют друг за другом стык-в-стык
            # или начала i1 лежит в периоде i2
            return self.interval(i2.s, i1.f)
        
        return False