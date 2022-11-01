import pytz
from datetime import timedelta
from re import findall, sub

class ChronoTransformator(object):
    """изменяет внутреннее состояние chrono"""

    def setTS(self, string):
        return self.setTimeShift(string)

    def setTimeShift(self, string):
        # Time + Shift
        # получает строку в которой может быть передано одновременно и время и смещение 
        # пример: 
        # "00:25 +45" → 01:10
        # "025 + 45"  → 01:10
        # a.setTS("2 +3d -25") → задает 02:00 прибавляет 3 дня и вычетает 25 минут

        string = string.strip()
        # ↑ строка должна начинать с чисел времени

        time = findall(r"^\d{1,2}:\d{1,2}|^\d{1,4}", string)
        if len(time) > 0:
            self.setTimeFromString(time[0])
            string = sub(r"(^\d{1,2}:\d{1,2}|^\d{1,4})", r"", string)
        self.shiftTextCommand(string)
        return self

    def shiftTC(self, string):
        return self.shiftTextCommand(string)

    def shiftTextCommand(self, string):
        # Text Command
        # задание смещения текстовыми командами
        # пример:
        # +1y -1y 23mo -23mo 3d -3d +1h 25m 1w
        # +2*2w = +4w, +55*5m = +275m
        shift_args = {'year':0, 'month':0, 'day':0, 'hour':0, 'minute':0, 'second':0, 'week':0}
        
        def multiplication(string):
            multipliers = string[0].split("*")
            return str( int(multipliers[0]) * int(multipliers[1]) )
        string = sub(r'[0-9]+\*[0-9]+', multiplication, string)
        # ↑ выполняет переумножение чисел разделенных `*` в текстовой команде 
        shift = f' {string.lower()} '

        y  = findall(r'([- +]\d+)y', shift)
        mo = findall(r'([- +]\d+)mo', shift)
        d  = findall(r'([- +]\d+)d', shift)
        h  = findall(r'([- +]\d+)h', shift)
        m  = findall(r'([- +]\d+)m ', shift)
        s  = findall(r'([- +]\d+)s', shift)
        w  = findall(r'([- +]\d+)w', shift)
        # ↓ если передано число безх текстового индикатора, то оно считается как минуты
        m.extend(findall(r'([- +]\d+)[ ]', shift))

        if len(y) != 0: shift_args['year'] = sum([int(x) for x in y])
        if len(mo)!= 0: shift_args['month'] = sum([int(x) for x in mo])
        if len(d) != 0: shift_args['day'] = sum([int(x) for x in d])
        if len(h) != 0: shift_args['hour'] = sum([int(x) for x in h])
        if len(m) != 0: shift_args['minute'] = sum([int(x) for x in m])
        if len(s) != 0: shift_args['second'] = sum([int(x) for x in s])
        if len(w) != 0: shift_args['week'] = sum([int(x) for x in w])

        return self.shift(**shift_args)

    def shiftRI(self, string):
        # Relative Indication
        func = self.RelativeIndication.get(string, False)
        if func is not None:
            func()

    def shift(self, year = 0, month = 0, day = 0, hour = 0, minute = 0, second = 0, week = 0):
        
        delta_seconds = second + (minute * 60) + (hour * 3600) +  (day * 86400) + (week * 86400 * 7)
        self.setDT(
            self.getDateTime() + timedelta(seconds = delta_seconds) 
        )

        # Если указан год или месяц, то 
        # находится следующая дата + следующего года или месяца

        if month != 0:
            self.m += month
            if self.m < 1:
                while self.m < 1:
                    self.m += 12
                    self.y -= 1
            elif self.m > 12:
                while self.m > 12:
                    self.m -= 12
                    self.y += 1

        self.y += year

        count_days = {
            1:31,
            2:29 if self.isLeapYear(self.y) else 28,
            3:31,
            4:30,
            5:31,
            6:30,
            7:31,
            8:31,
            9:30,
            10:31,
            11:30,
            12:31
        }

        if self.d > count_days[self.m]: 
            self.d = count_days[self.m]

        return self

    def toTimeZone(self, TimeZone = 'UTC'):
        # переводит время из текущей временной зоны в переданную
        if TimeZone != self.tz:
            preset_tz = pytz.timezone( str(self.tz) )
            preset_dt = preset_tz.localize(
                self.getDateTime()
            )

            new_tz = pytz.timezone(str(TimeZone))
            new_datetime = preset_dt.astimezone(new_tz)

            self.y = new_datetime.year
            self.m = new_datetime.month
            self.d = new_datetime.day
            self.H = new_datetime.hour
            self.M = new_datetime.minute
            self.S = new_datetime.second
            self.tz = str(TimeZone)

        return self

    def toUTC(self):
        return self.toTimeZone('UTC')

    def toLocal(self):
        return self.toTimeZone(
            self.getLocalTimeZone()
        )




    # Имеются ли консенсус по поводу измерения даты на других солнечных объектах?
    # Год на Марсе все так же равняется 365/+1 суткам или 669 соло?
    # Если год на Марсе измеряется в соло, то какой тогда сегодня год на Марсе?

    # def toMars(self):
    # def toMoon(self):

