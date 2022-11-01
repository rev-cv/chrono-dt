class IntervalPitcher(object):

    def getСompleted(self, chrono):
        # определяет процент завершенности текущего периода
        # на основании переданной даты
        if chrono.isTime() is False:
            chrono.setTupleTime(0,0,0)
        c1 = self.s.getUnixEpoch()
        c2 = chrono.getUnixEpoch()
        c3 = self.f.getUnixEpoch()
        if c1 < c2 < c3:
            return round((c2 - c1) * 100 / (c3 - c1), 1)
    
    def getOccupancy(self):
        # выдает процент заполненности интервала self интервалами из self.fragments
        diff = self.getOccupancyFragments()
        frag = self.getDuration()
        return round(diff * 100 / frag, 1)

    def getOccupancyFragments(self, measure='second'):
        # подсчитывает заполнение интервалами из self.fragments для self
        return self.intervals(*self.fragments).occupancy(measure)

    def getDuration(self, measure='second'):
        diff = self.f.getUnixEpoch() - self.s.getUnixEpoch()

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

            return { 'y': by, 'd': bd, 'h': bh, 'm': bm, 's': bs }

         

    

    
         


        



"""
getСomplete(chrono)


getScale("day")
# получить размер периода в днях / часах / секундах и прочее
# получен будет словарь с разбивкой {years: 1, months: 6, days: 2}

getDiff()
получить разницу между start и finish в секундах, минутах, дня и прочее

getSplitInterval("day")
# раздробить данный интервал на дни / часы / прочее
# раздробленные интервалы будут записаны в self.fragments


"""
