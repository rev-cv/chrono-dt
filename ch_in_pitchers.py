from datetime import datetime, timedelta

def getСompleted(i1, i2, date):
    # определяет процент завершенности текущего периода на основании переданной даты
    dti1 = datetime(*i1).timestamp()
    dti2 = datetime(*i2).timestamp()
    dtcur = datetime(*date).timestamp()
    if dti1 <= dtcur <= dti2:
        return round((dtcur - dti1) * 100 / (dti2 - dti1), 1)

def getDuration(i1, i2, measure='second'):
    diff = (datetime(*i2) - datetime(*i1)).total_seconds()

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
    



if __name__ == '__main__':
    print(
        getСompleted(
            [2023, 1, 1, 0, 0, 0],
            [2024, 1, 1, 0, 0, 0],
            [2024, 1, 1, 0, 0, 0],
        )
    )